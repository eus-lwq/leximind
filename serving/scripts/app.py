from fastapi import FastAPI, Request
from pydantic import BaseModel
import faiss, pickle, numpy as np
from sentence_transformers import SentenceTransformer
import requests
import os
from prometheus_fastapi_instrumentator import Instrumentator  # Import Prometheus instrumentator

app = FastAPI()

# Enable Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Load model & data
model = SentenceTransformer('all-MiniLM-L6-v2')
repo_name = "langchain"  # Example
index = faiss.read_index(f'/mnt/block/rag_data/vector_index/{repo_name}_faiss.index')
with open(f'/mnt/block/rag_data/chunks/{repo_name}_chunks.pkl', 'rb') as f:
    chunks = pickle.load(f)

# Request model
class QueryRequest(BaseModel):
    question: str

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

@app.post("/ask")
def ask_question(request: QueryRequest):
    contexts = retrieve_context(request.question)
    prompt = create_prompt(contexts, request.question)

    # Read the model path from the environment variable
    model_ver = os.getenv("MODEL_VER", "whole_model")  # Default to "/home/cc/model/whole_model/" if not set

    # vLLM OpenAI-compatible API endpoint
    response = requests.post(
        "http://llmendpoint:8080/v1/completions",
        json={
            "model": f"/home/cc/model/{model_ver}/",  # Use the environment variable value
            "prompt": prompt,
            "max_tokens": 500,
            "temperature": 0.7,
            "stop": None
        }
    )
    return {"answer": response.json()["choices"][0]["text"]}