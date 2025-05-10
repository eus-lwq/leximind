#!/usr/bin/env python3
"""Test the complete pipeline by adding test data to MinIO and Label Studio"""
import boto3
import requests
import json
import uuid
import datetime
import os
import time
import argparse

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

def parse_args():
    parser = argparse.ArgumentParser(description='Test the pipeline')
    
    # Get the public IP for default values
    public_ip = get_public_ip()
    print(f"Detected public IP: {public_ip}")
    
    parser.add_argument('--minio-url', type=str, default=f'http://{public_ip}:9000')
    parser.add_argument('--minio-user', type=str, default='your-access-key')
    parser.add_argument('--minio-password', type=str, default='your-secret-key')
    parser.add_argument('--label-studio-url', type=str, default=f'http://{public_ip}:8090')
    parser.add_argument('--label-studio-token', type=str, 
                        default='ab9927067c51ff279d340d7321e4890dc2841c4a')
    return parser.parse_args()

def setup_minio_client(args):
    """Set up and return MinIO client"""
    print(f"Connecting to MinIO at {args.minio_url}...")
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

def get_label_studio_project_id(args):
    """Get the Label Studio project ID"""
    print(f"Getting Label Studio project ID from {args.label_studio_url}...")
    headers = {
        'Authorization': f'Token {args.label_studio_token}'
    }
    
    try:
        response = requests.get(
            f'{args.label_studio_url}/api/projects',
            headers=headers
        )
        
        if response.status_code == 200:
            projects = response.json()
            if projects:
                project_id = projects[0]['id']
                print(f"Found Label Studio project ID: {project_id}")
                return project_id
            else:
                print("No projects found in Label Studio. Creating one...")
                return create_label_studio_project(args)
        else:
            print(f"Failed to get projects: {response.text}")
            return None
    except Exception as e:
        print(f"Error getting Label Studio project ID: {e}")
        return None

def create_label_studio_project(args):
    """Create a Label Studio project"""
    print("Creating a new Label Studio project...")
    
    # Define the labeling interface
    label_config = """
    <View>
      <Header value="Question:"/>
      <Text name="question" value="$question"/>
      
      <Header value="Model Answer:"/>
      <Text name="answer" value="$answer"/>
      
      <Header value="Rating:"/>
      <Choices name="rating" toName="answer" choice="single" showInLine="true">
        <Choice value="Excellent"/>
        <Choice value="Good"/>
        <Choice value="Average"/>
        <Choice value="Poor"/>
        <Choice value="Incorrect"/>
      </Choices>
      
      <TextArea name="feedback" toName="answer" placeholder="Provide feedback on the answer..." rows="4"/>
    </View>
    """
    
    headers = {
        'Authorization': f'Token {args.label_studio_token}',
        'Content-Type': 'application/json'
    }
    
    # Create project
    project_data = {
        'title': 'RAG Response Evaluation',
        'description': 'Evaluate the quality of RAG responses',
        'label_config': label_config
    }
    
    try:
        response = requests.post(
            f'{args.label_studio_url}/api/projects',
            headers=headers,
            json=project_data
        )
        
        if response.status_code == 201:
            project = response.json()
            print(f"Project created with ID: {project['id']}")
            return project['id']
        else:
            print(f"Failed to create project: {response.text}")
            return None
    except Exception as e:
        print(f"Error creating project: {e}")
        return None

def add_test_data(s3_client, project_id, args):
    """Add test data to MinIO and Label Studio"""
    print("Adding test data to the pipeline...")
    
    # Generate test data
    query_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().isoformat()
    user_id = "test-user"
    question = "What is the capital of France?"
    answer = "The capital of France is Paris. It is known as the 'City of Light' and is famous for landmarks such as the Eiffel Tower, Louvre Museum, and Notre-Dame Cathedral."
    
    # Create query data
    query_data = {
        "id": query_id,
        "timestamp": timestamp,
        "user_id": user_id,
        "question": question
    }
    
    # Create response data
    response_data = {
        "id": query_id,
        "timestamp": timestamp,
        "user_id": user_id,
        "question": question,
        "answer": answer,
        "model_version": "test-model"
    }
    
    # Store in MinIO
    print(f"Storing test query in MinIO (queries/{query_id}.json)...")
    s3_client.put_object(
        Bucket="queries",
        Key=f"{query_id}.json",
        Body=json.dumps(query_data)
    )
    
    print(f"Storing test response in MinIO (responses/{query_id}.json)...")
    s3_client.put_object(
        Bucket="responses",
        Key=f"{query_id}.json",
        Body=json.dumps(response_data)
    )
    
    # Import to Label Studio
    if project_id:
        print(f"Importing test data to Label Studio project {project_id}...")
        
        task = {
            "data": {
                "question": question,
                "answer": answer,
                "query_id": query_id,
                "user_id": user_id,
                "timestamp": timestamp
            }
        }
        
        headers = {
            'Authorization': f'Token {args.label_studio_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                f'{args.label_studio_url}/api/projects/{project_id}/import',
                headers=headers,
                json=[task]
            )
            
            if response.status_code == 201:
                print("Successfully imported test data to Label Studio")
            else:
                print(f"Failed to import test data to Label Studio: {response.text}")
        except Exception as e:
            print(f"Error importing to Label Studio: {e}")
    
    print("Test data added successfully!")

def main():
    args = parse_args()
    
    try:
        # Setup MinIO client
        s3_client = setup_minio_client(args)
        
        # Get Label Studio project ID
        project_id = get_label_studio_project_id(args)
        
        # Add test data
        add_test_data(s3_client, project_id, args)
        
        # Display success message with URLs
        public_ip = get_public_ip()
        print("\n" + "="*50)
        print("🎉 Pipeline tested successfully!")
        print("You can view the results at:")
        print(f"🏷️ Label Studio: {args.label_studio_url}")
        print(f"🗄️ MinIO Console: http://{public_ip}:9001")
        print("="*50 + "\n")
        
        # Print the project ID for use with the Gradio chatbot
        if project_id:
            print(f"When starting the Gradio chatbot, use:")
            print(f"--label-studio-project-id {project_id}")
        
    except Exception as e:
        print(f"Error testing pipeline: {e}")

if __name__ == "__main__":
    main()