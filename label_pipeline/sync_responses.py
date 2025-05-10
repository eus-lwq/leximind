import os
import boto3
import requests
import json
import time
from datetime import datetime, timedelta

# Label Studio settings
LS_URL = os.getenv('LABEL_STUDIO_URL', 'http://label-studio:8080')
LS_TOKEN = os.getenv('LABEL_STUDIO_USER_TOKEN', 'ab9927067c51ff279d340d7321e4890dc2841c4a')

# MinIO settings
MINIO_URL = os.getenv('MINIO_URL', 'http://minio:9000')
MINIO_USER = os.getenv('MINIO_USER', 'your-access-key')
MINIO_PASSWORD = os.getenv('MINIO_PASSWORD', 'your-secret-key')

# Project ID - get this from the output of ls_integration.py
PROJECT_ID = os.getenv('LABEL_STUDIO_PROJECT_ID')

# Initialize MinIO client
s3_client = boto3.client(
    's3',
    endpoint_url=MINIO_URL,
    aws_access_key_id=MINIO_USER,
    aws_secret_access_key=MINIO_PASSWORD,
    region_name='us-east-1',
    config=boto3.session.Config(signature_version='s3v4')
)

def get_imported_tasks():
    """Get list of tasks already imported to Label Studio"""
    
    headers = {
        'Authorization': f'Token {LS_TOKEN}'
    }
    
    response = requests.get(
        f'{LS_URL}/api/projects/{PROJECT_ID}/tasks',
        headers=headers
    )
    
    if response.status_code == 200:
        tasks = response.json()
        # Extract query_ids from imported tasks
        imported_ids = []
        for task in tasks:
            if 'query_id' in task['data']:
                imported_ids.append(task['data']['query_id'])
        return imported_ids
    else:
        print(f"Failed to get tasks: {response.text}")
        return []

def get_new_responses(imported_ids):
    """Get responses from MinIO that haven't been imported yet"""
    
    # List objects in the responses bucket
    response = s3_client.list_objects_v2(Bucket='responses')
    
    new_responses = []
    if 'Contents' in response:
        for obj in response['Contents']:
            key = obj['Key']
            # Extract the query_id from the filename (removing .json)
            query_id = key.split('.')[0]
            
            if query_id not in imported_ids:
                # This is a new response, get its content
                obj_response = s3_client.get_object(Bucket='responses', Key=key)
                content = obj_response['Body'].read().decode('utf-8')
                response_data = json.loads(content)
                new_responses.append(response_data)
    
    return new_responses

def prepare_tasks(responses):
    """Prepare Label Studio tasks from responses"""
    
    tasks = []
    for response in responses:
        task = {
            'data': {
                'question': response['question'],
                'answer': response['answer'],
                'query_id': response['id'],
                'user_id': response['user_id'],
                'timestamp': response['timestamp'],
                'model_version': response.get('model_version', 'unknown')
            }
        }
        tasks.append(task)
    
    return tasks

def import_tasks(tasks):
    """Import tasks to Label Studio"""
    
    if not tasks:
        print("No new tasks to import")
        return
    
    headers = {
        'Authorization': f'Token {LS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(
        f'{LS_URL}/api/projects/{PROJECT_ID}/import',
        headers=headers,
        json=tasks
    )
    
    if response.status_code == 201:
        result = response.json()
        print(f"Successfully imported {len(tasks)} new tasks")
    else:
        print(f"Failed to import tasks: {response.text}")

def sync_loop():
    """Continuously sync new responses to Label Studio"""
    
    print(f"Starting sync loop for project {PROJECT_ID}")
    
    while True:
        try:
            # Get already imported tasks
            imported_ids = get_imported_tasks()
            print(f"Found {len(imported_ids)} existing tasks in Label Studio")
            
            # Get new responses
            new_responses = get_new_responses(imported_ids)
            print(f"Found {len(new_responses)} new responses in MinIO")
            
            # Prepare and import tasks
            if new_responses:
                tasks = prepare_tasks(new_responses)
                import_tasks(tasks)
            
            # Wait before next sync
            time.sleep(60)  # Check every minute
        
        except Exception as e:
            print(f"Error in sync loop: {e}")
            time.sleep(30)  # Wait a bit before retrying

if __name__ == "__main__":
    # Check if project ID is set
    if not PROJECT_ID:
        print("Please set LABEL_STUDIO_PROJECT_ID environment variable")
        exit(1)
    
    sync_loop()