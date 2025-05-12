# Scripts for Serving Machine Learning Models

This folder contains various scripts and configuration files to facilitate the deployment and serving of machine learning models. Below is a description of each file and its purpose.

## Files and Their Descriptions

### [`app.py`](./app.py)
- **Description**: A Python FastAPI application for serving machine learning models.

### [`docker-compose.yml`](./docker-compose.yml)
- **Description**: Docker Compose configuration file for deploying services including NGINX, and Prometheus.

### [`fastapi_serving.sh`](./fastapi_serving.sh)
- **Description**: Shell script to start the FastAPI server for serving models.

### [`gradio-chatbot.py`](./gradio-chatbot.py)
- **Description**: A Gradio-based chatbot interface for interacting with served language model.

### [`langchain-rag-vllm.py`](./langchain-rag-vllm.py)
- **Description**: Script for implementing Retrieval-Augmented Generation (RAG) using LangChain and vLLM.

### [`llama3_chat_template.txt`](./llama3_chat_template.txt)
- **Description**: A text template for configuring chat interactions with the LLaMA-3 based model.

### [`nginx.conf`](./nginx.conf)
- **Description**: NGINX configuration file for reverse proxying and load balancing.

### [`prometheus.yaml`](./prometheus.yaml)
- **Description**: Prometheus configuration file for monitoring deployed services.

### [`requirements.txt`](./requirements.txt)
- **Description**: Python dependencies required for running the scripts in this folder.

### [`vllm_serving_lora_adapter.sh`](./vllm_serving_lora_adapter.sh)
- **Description**: Shell script to start the vLLM server with a LoRA adapter for model serving and to start simple chatui.

### [`vllm_serving.sh`](./vllm_serving.sh)
- **Description**: Shell script to start the vLLM server for serving machine learning models and to start simple chatui.

