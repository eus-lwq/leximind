import os
import requests
import json
import boto3
from time import sleep

# Label Studio settings
LS_URL = os.getenv('LABEL_STUDIO_URL', 'http://label-studio:8080')
LS_TOKEN = os.getenv('LABEL_STUDIO_USER_TOKEN', 'ab9927067c51ff279d340d7321e4890dc2841c4a')

# MinIO settings
MINIO_URL = os.getenv('MINIO_URL', 'http://minio:9000')
MINIO_USER = os.getenv('MINIO_USER', 'your-access-key')
MINIO_PASSWORD = os.getenv('MINIO_PASSWORD', 'your-secret-key')

# Initialize MinIO client
s3_client = boto3.client(
    's3',
    endpoint_url=MINIO_URL,
    aws_access_key_id=MINIO_USER,
    aws_secret_access_key=MINIO_PASSWORD,
    region_name='us-east-1',
    config=boto3.session.Config(signature_version='s3v4')
)

def create_project():
    """Create a Label Studio project for evaluating RAG responses"""
    
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
        'Authorization': f'Token {LS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Create project
    project_data = {
        'title': 'RAG Response Evaluation',
        'description': 'Evaluate the quality of RAG responses',
        'label_config': label_config
    }
    
    response = requests.post(
        f'{LS_URL}/api/projects',
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

def setup_s3_storage(project_id):
    """Connect Label Studio to MinIO S3 storage"""
    
    headers = {
        'Authorization': f'Token {LS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    storage_data = {
        'project': project_id,
        'title': 'MinIO Storage',
        'storage_type': 's3',
        'bucket': 'responses',
        'aws_access_key_id': MINIO_USER,
        'aws_secret_access_key': MINIO_PASSWORD,
        'region_name': 'us-east-1',
        'endpoint_url': MINIO_URL,
        'use_blob_urls': True,
        'presign': True,
        'presign_ttl': 3600
    }
    
    response = requests.post(
        f'{LS_URL}/api/storages/s3',
        headers=headers,
        json=storage_data
    )
    
    if response.status_code == 201:
        storage = response.json()
        print(f"S3 storage connected with ID: {storage['id']}")
        return storage['id']
    else:
        print(f"Failed to set up S3 storage: {response.text}")
        return None
        
def prepare_task_for_label_studio(response_data):
    """Transform a response from MinIO to a Label Studio task"""
    
    # Convert the response data to a task
    task = {
        'data': {
            'question': response_data['question'],
            'answer': response_data['answer'],
            'query_id': response_data['id'],
            'user_id': response_data['user_id'],
            'timestamp': response_data['timestamp'],
        }
    }
    
    return task

def import_tasks_to_label_studio(project_id, tasks):
    """Import tasks to Label Studio project"""
    
    headers = {
        'Authorization': f'Token {LS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(
        f'{LS_URL}/api/projects/{project_id}/import',
        headers=headers,
        json=tasks
    )
    
    if response.status_code == 201:
        result = response.json()
        print(f"Successfully imported {len(tasks)} tasks")
        return True
    else:
        print(f"Failed to import tasks: {response.text}")
        return False

def main():
    """Main function to set up Label Studio and import initial data"""
    
    # Wait for Label Studio to be ready
    print("Waiting for Label Studio to start...")
    sleep(30)
    
    # Create project
    project_id = create_project()
    if not project_id:
        return
    
    # Set up S3 storage
    storage_id = setup_s3_storage(project_id)
    if not storage_id:
        return
    
    print("Label Studio project and storage setup complete.")
    print(f"Access Label Studio at {LS_URL} and log in with the configured credentials.")

if __name__ == "__main__":
    main()