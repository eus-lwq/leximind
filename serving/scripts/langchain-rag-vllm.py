"""
Retrieval Augmented Generation (RAG) Implementation with FastAPI and Langchain
==================================================================

This script demonstrates a RAG implementation using FastAPI, LangChain, Milvus
and vLLM. RAG enhances LLM responses by retrieving relevant context
from a document collection.

Features:
- Web content loading and chunking
- Vector storage with Milvus
- Embedding generation with vLLM
- Question answering with context
- RESTful API endpoints with FastAPI

Prerequisites:
1. Install dependencies:
    pip install -U vllm \
                 langchain_milvus langchain_openai \
                 langchain_community beautifulsoup4 \
                 langchain-text-splitters \
                 fastapi uvicorn

2. Start services:
    # Start embedding service (port 8000)
    vllm serve ssmits/Qwen2-7B-Instruct-embed-base

    # Start chat service (port 8001)
    vllm serve qwen/Qwen1.5-0.5B-Chat --port 8001

Usage:
    uvicorn app:app --reload

Notes:
    - Ensure both vLLM services are running before executing
    - Default ports: 8000 (embedding), 8001 (chat)
    - First run may take time to download models
"""

import argparse
from argparse import Namespace
from typing import Any, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_milvus import Milvus
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Initialize FastAPI app
app = FastAPI(
    title="RAG API",
    description="Retrieval Augmented Generation API using LangChain and vLLM",
    version="1.0.0"
)

# Pydantic models for request/response
class QuestionRequest(BaseModel):
    question: str = Field(..., description="The question to answer")
    top_k: int = Field(default=3, description="Number of top results to retrieve")

class QuestionResponse(BaseModel):
    answer: str = Field(..., description="The answer to the question")
    context: Optional[List[str]] = Field(default=None, description="Retrieved context used for answering")

class ConfigRequest(BaseModel):
    url: str = Field(..., description="URL of the document to process")
    chunk_size: int = Field(default=1000, description="Chunk size for document splitting")
    chunk_overlap: int = Field(default=200, description="Chunk overlap for document splitting")
    embedding_model: str = Field(default="ssmits/Qwen2-7B-Instruct-embed-base", description="Model name for embeddings")
    chat_model: str = Field(default="qwen/Qwen1.5-0.5B-Chat", description="Model name for chat")
    vllm_api_key: str = Field(default="EMPTY", description="API key for vLLM compatible services")
    vllm_embedding_endpoint: str = Field(default="http://localhost:8000/v1", description="Base URL for embedding service")
    vllm_chat_endpoint: str = Field(default="http://localhost:8001/v1", description="Base URL for chat service")
    uri: str = Field(default="./milvus.db", description="URI for Milvus database")

# Global variables to store the QA chain and configuration
qa_chain = None
current_config = None

def load_and_split_documents(config: dict[str, Any]):
    """
    Load and split documents from web URL
    """
    try:
        loader = WebBaseLoader(web_paths=(config["url"], ))
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config["chunk_size"],
            chunk_overlap=config["chunk_overlap"],
        )
        return text_splitter.split_documents(docs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading document from {config['url']}: {str(e)}")

def init_vectorstore(config: dict[str, Any], documents: list[Document]):
    """
    Initialize vector store with documents
    """
    try:
        return Milvus.from_documents(
            documents=documents,
            embedding=OpenAIEmbeddings(
                model=config["embedding_model"],
                openai_api_key=config["vllm_api_key"],
                openai_api_base=config["vllm_embedding_endpoint"],
            ),
            connection_args={"uri": config["uri"]},
            drop_old=True,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing vector store: {str(e)}")

def init_llm(config: dict[str, Any]):
    """
    Initialize llm
    """
    try:
        return ChatOpenAI(
            model=config["chat_model"],
            openai_api_key=config["vllm_api_key"],
            openai_api_base=config["vllm_chat_endpoint"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing LLM: {str(e)}")

def get_qa_prompt():
    """
    Get question answering prompt template
    """
    template = """You are an assistant for question-answering tasks.
Use the following pieces of retrieved context to answer the question.
If you don't know the answer, just say that you don't know.
Use three sentences maximum and keep the answer concise.
Question: {question}
Context: {context}
Answer:
"""
    return PromptTemplate.from_template(template)

def format_docs(docs: list[Document]):
    """
    Format documents for prompt
    """
    return "\n\n".join(doc.page_content for doc in docs)

def create_qa_chain(retriever: Any, llm: ChatOpenAI, prompt: PromptTemplate):
    """
    Set up question answering chain
    """
    return ({
        "context": retriever | format_docs,
        "question": RunnablePassthrough(),
    }
            | prompt
            | llm
            | StrOutputParser())

@app.post("/configure", response_model=dict)
async def configure_rag(request: ConfigRequest):
    """
    Configure the RAG system with new settings
    """
    global qa_chain, current_config
    
    try:
        config = request.dict()
        current_config = config
        
        # Load and split documents
        documents = load_and_split_documents(config)
        
        # Initialize vector store and retriever
        vectorstore = init_vectorstore(config, documents)
        retriever = vectorstore.as_retriever(search_kwargs={"k": config.get("top_k", 3)})
        
        # Initialize llm and prompt
        llm = init_llm(config)
        prompt = get_qa_prompt()
        
        # Set up QA chain
        qa_chain = create_qa_chain(retriever, llm, prompt)
        
        return {"status": "success", "message": "RAG system configured successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question to the RAG system
    """
    global qa_chain, current_config
    
    if qa_chain is None:
        raise HTTPException(status_code=400, detail="RAG system not configured. Please call /configure first")
    
    try:
        # Update top_k if provided
        if current_config:
            current_config["top_k"] = request.top_k
        
        # Get answer
        answer = qa_chain.invoke(request.question)
        
        return QuestionResponse(
            answer=answer,
            context=None  # You can modify this to include context if needed
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "qa_chain_initialized": qa_chain is not None}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)