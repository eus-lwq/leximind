#!/usr/bin/env python3
"""Gradio OpenAI Chatbot Webserver with MinIO Storage Integration"""
import argparse
import gradio as gr
from openai import OpenAI
import boto3
import json
import uuid
import datetime
import os
import requests
import time
from label_studio_sdk.client import LabelStudio
import traceback

def get_public_ip():
    """Get the host's public IP address using multiple methods"""
    # Try AWS metadata service
    try:
        response = requests.get('http://169.254.169.254/latest/meta-data/public-ipv4', timeout=3)
        if response.status_code == 200:
            return response.text.strip()
    except:
        pass
    
    # Try GCP metadata service
    try:
        response = requests.get(
            'http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip',
            headers={'Metadata-Flavor': 'Google'},
            timeout=3
        )
        if response.status_code == 200:
            return response.text.strip()
    except:
        pass
    
    # Try general public IP services
    services = [
        'https://ipinfo.io/ip',
        'https://api.ipify.org',
        'http://checkip.amazonaws.com'
    ]
    
    for service in services:
        try:
            response = requests.get(service, timeout=3)
            if response.status_code == 200:
                return response.text.strip()
        except:
            continue
    
    # Fall back to private IP if all else fails
    try:
        import socket
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except:
        return "localhost"

def setup_minio_client(args):
    """Set up and return MinIO client"""
    try:
        # MinIO client setup
        print(f"Connecting to MinIO at: {args.minio_url}")
        
        s3_client = boto3.client(
            's3',
            endpoint_url=args.minio_url,
            aws_access_key_id=args.minio_user,
            aws_secret_access_key=args.minio_password,
            region_name='us-east-1',
            config=boto3.session.Config(signature_version='s3v4')
        )
        
        # Test connection by listing buckets
        response = s3_client.list_buckets()
        print(f"Connected to MinIO. Available buckets: {[bucket['Name'] for bucket in response['Buckets']]}")
        return s3_client
    except Exception as e:
        print(f"Warning: Could not connect to MinIO: {e}")
        print("Will continue without storage capabilities.")
        return None

def create_label_studio_project(args):
    """Create a Label Studio project for evaluating RAG responses using the SDK"""
    from label_studio_sdk.label_interface import LabelInterface
    from label_studio_sdk.label_interface.create import choices

    # Define the labeling interface
    label_config = LabelInterface.create({
        'question': 'Question',
        'answer': 'Model Answer',
        'rating': choices(['Excellent', 'Good', 'Average', 'Poor', 'Incorrect']),
        'feedback': 'Feedback'
    })

    # Connect to Label Studio using the SDK
    ls = LabelStudio(base_url=args.label_studio_url, api_key=args.label_studio_token)
    print("Creating Label Studio project using SDK...")
    try:
        project = ls.projects.create(
            title='RAG Response Evaluation',
            label_config=label_config,
            description='Evaluate the quality of RAG responses'
        )
        if project is not None:
            print(f"Project created with ID: {project.id}")
            return project.id
        else:
            print("Project creation returned None.")
            return None
    except Exception as e:
        print(f"Error creating project with SDK: {e}")
        traceback.print_exc()
        return None

def get_label_studio_project_id(args):
    """Get the Label Studio project ID or create one if it doesn't exist using the SDK"""
    if args.label_studio_project_id:
        print(f"Using provided Label Studio project ID: {args.label_studio_project_id}")
        return args.label_studio_project_id

    print("No project ID provided. Checking for existing projects using SDK...")
    ls = LabelStudio(base_url=args.label_studio_url, api_key=args.label_studio_token)
    try:
        projects = list(ls.projects.list())
        if projects:
            project_id = projects[0].id
            print(f"Found existing Label Studio project with ID: {project_id}")
            return project_id
        else:
            print("No projects found. Creating a new one...")
            return create_label_studio_project(args)
    except Exception as e:
        print(f"Error communicating with Label Studio SDK: {e}")
        print("Continuing without Label Studio integration.")
        return None

def store_in_minio(s3_client, data, bucket, object_name):
    """Store data in MinIO bucket"""
    if s3_client is None:
        return False
    
    try:
        s3_client.put_object(
            Bucket=bucket,
            Key=object_name,
            Body=json.dumps(data)
        )
        print(f"Stored data in MinIO: {bucket}/{object_name}")
        return True
    except Exception as e:
        print(f"Error storing in MinIO: {e}")
        return False

def predict(message, history, client, model_name, temp, s3_client, args):
    # Generate unique ID for this query
    query_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().isoformat()
    
    # Store query details in MinIO
    if s3_client:
        user_id = args.user_id
        query_data = {
            "id": query_id,
            "timestamp": timestamp,
            "user_id": user_id,
            "question": message,
            "history": str(history)  # Convert history to string for storage
        }
        store_in_minio(s3_client, query_data, "queries", f"{query_id}.json")
    
    # Send request to vLLM API
    try:
        response = client.completions.create(
            model=model_name,
            prompt=message,
            max_tokens=500,
            temperature=temp
        )
        answer_text = response.choices[0].text
        
        # Store response in MinIO
        if s3_client:
            response_data = {
                "id": query_id,
                "timestamp": timestamp,
                "user_id": args.user_id,
                "question": message,
                "answer": answer_text,
                "model_version": model_name
            }
            store_in_minio(s3_client, response_data, "responses", f"{query_id}.json")
        
        # Try to import to Label Studio directly
        if args.label_studio_project_id:
            try_import_to_label_studio(message, answer_text, query_id, args)
        
        return answer_text
    except Exception as e:
        error_msg = f"Error calling model API: {str(e)}"
        print(error_msg)
        return f"Sorry, there was an error: {error_msg}"

def try_import_to_label_studio(question, answer, query_id, args):
    """Try to import task directly to Label Studio if available"""
    if not args.label_studio_project_id:
        print("No Label Studio project ID provided, skipping direct import")
        return False
    
    try:
        # Prepare task data
        task = {
            "data": {
                "question": question,
                "answer": answer,
                "query_id": query_id,
                "user_id": args.user_id,
                "timestamp": datetime.datetime.now().isoformat(),
            }
        }
        
        # Send request to Label Studio
        headers = {
            'Authorization': f'Token {args.label_studio_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f'{args.label_studio_url}/api/projects/{args.label_studio_project_id}/import',
            headers=headers,
            json=[task],
            timeout=5  # Short timeout to not block the UI
        )
        
        if response.status_code == 201:
            print(f"Successfully imported task to Label Studio project {args.label_studio_project_id}")
            return True
        else:
            print(f"Failed to import to Label Studio: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error importing to Label Studio: {e}")
        return False

def parse_args():
    parser = argparse.ArgumentParser(
        description='Chatbot Interface with MinIO Storage')
    
    # Get the public IP for default values
    public_ip = get_public_ip()
    print(f"Detected public IP: {public_ip}")
    
    parser.add_argument("--label-studio-username", type=str, default="labelstudio@example.com")
    parser.add_argument("--label-studio-password", type=str, default="labelstudio")

    parser.add_argument('--model-url',
                        type=str,
                        default='http://localhost:8000/v1',
                        help='Model URL')
    parser.add_argument('-m',
                        '--model',
                        type=str,
                        required=True,
                        help='Model name for the chatbot')
    parser.add_argument('--temp',
                        type=float,
                        default=0.8,
                        help='Temperature for text generation')
    parser.add_argument("--host", type=str, default=None)
    parser.add_argument("--port", type=int, default=7860)
    parser.add_argument("--minio-url", type=str, default=f"http://{public_ip}:9000")
    parser.add_argument("--minio-user", type=str, default="your-access-key")
    parser.add_argument("--minio-password", type=str, default="your-secret-key")
    parser.add_argument("--label-studio-url", type=str, default=f"http://{public_ip}:8090")
    parser.add_argument("--label-studio-token", type=str, 
                       default="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6ODA1NDExNjY0OSwiaWF0IjoxNzQ2OTE2NjQ5LCJqdGkiOiIyNTUwMjE0M2RkYzA0YzE1YWZlOTAwZGY4YjViOGY1NCIsInVzZXJfaWQiOjF9.Yqx9lGOn7ROF5ANU5YUoZYACuyvzJT-0m8bS1kcSX4Q", # PAT
                       help="Label Studio API token (from Access Tokens page)")
    parser.add_argument("--label-studio-project-id", type=str, default=None)
    parser.add_argument("--user-id", type=str, default="gradio-user")
    parser.add_argument("--create-project", action="store_true",
                        help="Create a new Label Studio project if none exists")
    return parser.parse_args()

def build_gradio_interface(client, model_name, temp, s3_client, args):
    def chat_predict(message, history):
        return predict(message, history, client, model_name, temp, s3_client, args)

    # Create a chat interface with history
    chatbot = gr.ChatInterface(
        fn=chat_predict,
        title="RAG Evaluation Chatbot",
        description="Ask me questions and I'll provide answers. Your conversations are stored for evaluation.",
        examples=[
            "What is the capital of France?",
            "Explain how a transformer neural network works.",
            "What are the main benefits of retrieval-augmented generation?",
            "Can you summarize the key points of the last IPCC report?",
            "How do I implement a binary search algorithm?"
        ],
        theme="soft"
    )
    
    # Add additional components
    with gr.Blocks() as demo:
        chatbot.render()
        
        with gr.Accordion("About this Demo", open=False):
            gr.Markdown(f"""
            ## RAG Evaluation System
            
            This chatbot is connected to:
            - Model API at: `{args.model_url}`
            - MinIO storage at: `{args.minio_url}`
            - Label Studio at: `{args.label_studio_url}`
            - Label Studio Project ID: `{args.label_studio_project_id}`
            
            All queries and responses are stored for evaluation purposes.
            You can view and evaluate responses in Label Studio.
            """)
    
    return demo

def main():
    # Parse the arguments
    args = parse_args()
    
    # Setup MinIO client
    s3_client = setup_minio_client(args)

    # Get or create Label Studio project using SDK
    if args.label_studio_token:
        project_id = get_label_studio_project_id(args)
        if project_id:
            args.label_studio_project_id = project_id
            print(f"Using Label Studio project ID: {project_id}")
        else:
            print("⚠️ Warning: Could not get or create a Label Studio project. Label Studio integration will be disabled.")
            args.label_studio_project_id = None
    else:
        print("⚠️ Warning: No Label Studio token provided. Label Studio integration will be disabled.")
        args.label_studio_project_id = None
    
    # Create an OpenAI client
    client = OpenAI(api_key="EMPTY", base_url=args.model_url)
    print(f"Connected to model API at {args.model_url}")

    # Display dashboard links
    print("\n" + "="*50)
    print("🚀 DASHBOARD LINKS:")
    print(f"📊 Gradio Interface: http://{args.host or 'localhost'}:{args.port}")
    print(f"🏷️ Label Studio: {args.label_studio_url}")
    print(f"🗄️ MinIO Console: http://{get_public_ip()}:9001")
    print("="*50 + "\n")

    # Define the Gradio chatbot interface using the predict function
    gradio_interface = build_gradio_interface(client, args.model, args.temp, s3_client, args)

    # Launch the interface
    gradio_interface.queue().launch(
        server_name=args.host or "0.0.0.0",  # Use 0.0.0.0 by default for external access
        server_port=args.port,
        share=True
    )

if __name__ == "__main__":
    main()