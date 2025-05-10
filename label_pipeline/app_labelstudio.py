from fastapi import FastAPI, Request
from pydantic import BaseModel
import faiss, pickle, numpy as np
from sentence_transformers import SentenceTransformer
import requests
import os
import json
import uuid
import datetime
import boto3
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Enable Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Load model & data
model = SentenceTransformer('all-MiniLM-L6-v2')
repo_name = "langchain"  # Example
index = faiss.read_index(f'/mnt/block/rag_data/vector_index/{repo_name}_faiss.index')
with open(f'/mnt/block/rag_data/chunks/{repo_name}_chunks.pkl', 'rb') as f:
    chunks = pickle.load(f)

# MinIO client setup
minio_client = boto3.client(
    's3',
    endpoint_url=os.getenv('MINIO_URL', 'http://minio:9000'),
    aws_access_key_id=os.getenv('MINIO_USER', 'your-access-key'),
    aws_secret_access_key=os.getenv('MINIO_PASSWORD', 'your-secret-key'),
    region_name='us-east-1',  # This is arbitrary for MinIO
    config=boto3.session.Config(signature_version='s3v4')
)

# Request model
class QueryRequest(BaseModel):
    question: str
    user_id: str = "anonymous"

def retrieve_context(question, k=5):
    query_embedding = model.encode([question])
    D, I = index.search(query_embedding, k)
    return [chunks[i][1] for i in I[0]]  # Only text

def create_prompt(contexts, question):
    context_str = "\n\n".join(contexts)
    return f"""Use the following context to answer the question.

Context:
{context_str}

Question: {question}
Answer:"""

def store_in_minio(data, bucket, object_name):
    try:
        minio_client.put_object(
            Bucket=bucket,
            Key=object_name,
            Body=json.dumps(data)
        )
        return True
    except Exception as e:
        print(f"Error storing in MinIO: {e}")
        return False

@app.post("/ask")
def ask_question(request: QueryRequest):
    # Generate unique ID for this query
    query_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().isoformat()
    
    # Get contexts for RAG
    contexts = retrieve_context(request.question)
    prompt = create_prompt(contexts, request.question)

    # Store query details in MinIO
    query_data = {
        "id": query_id,
        "timestamp": timestamp,
        "user_id": request.user_id,
        "question": request.question,
        "contexts": contexts
    }
    
    store_in_minio(query_data, "queries", f"{query_id}.json")

    # Read the model path from the environment variable
    model_ver = os.getenv("MODEL_VER", "whole_model")

    # vLLM OpenAI-compatible API call
    response = requests.post(
        "http://llmendpoint:8080/v1/completions",
        json={
            "model": f"/home/cc/model/{model_ver}/",
            "prompt": prompt,
            "max_tokens": 500,
            "temperature": 0.7,
            "stop": None
        }
    )
    
    answer_text = response.json()["choices"][0]["text"]
    
    # Store response in MinIO
    response_data = {
        "id": query_id,
        "timestamp": timestamp,
        "user_id": request.user_id,
        "question": request.question,
        "answer": answer_text,
        "model_version": model_ver
    }
    
    store_in_minio(response_data, "responses", f"{query_id}.json")
    
    # Return the response to the user
    return {"answer": answer_text, "query_id": query_id}