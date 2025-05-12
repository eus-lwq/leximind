# Overview of the Serving Folder

The `serving` folder contains scripts, configurations, and utilities to deploy and serve machine learning models. It supports serving models via API endpoints, infrastructure deployment, and system optimizations. This document provides an overview of the folder structure and addresses key questions related to serving, evaluation, and monitoring.

---

## Folder Structure

- **[`scripts/`](./scripts/)**: Contains scripts for setting up and running model-serving applications.
- **[`use-cases/`](./use-cases/)**: Includes Terraform variable files for deploying models in different environments.
- **[`chi@uc.tf`](./chi@uc.tf)**: Terraform configuration for deploying resources at CHI@UC.
- **[`kvm@tacc.tf`](./kvm@tacc.tf)**: Terraform configuration for deploying resources at KVM@TACC.
- **[`shared.tf`](./shared.tf)**: Shared Terraform configurations for reusable components.
- **[`variables.tf`](./variables.tf)**: Defines variables used across Terraform configurations.

---

## Key Questions Addressed

### 1. **Serving from an API Endpoint**
- **Setup**: The API endpoint is implemented using FastAPI in [`scripts/app.py`](./scripts/app.py). It provides a `/ask` endpoint for querying the model.
- **Input**: A JSON payload with a `question` field.
  ```json
  {
    "question": "What is the purpose of the langchain repository?"
  }
  ```
- **Output**: A JSON response with the model's answer.
  ```json
  {
    "answer": "The langchain repository provides tools for building applications with language models."
  }
  ```
### 2. Identify Requirements
#### Customer Requirements:


##### 1. High-Performance GPU Deployment  
**Target Customer**:  
Organizations with access to high-end GPU clusters (e.g., NVIDIA A100, V100).  

**Requirements**:  
- **Low Latency**: Sub-second response times for real-time applications (e.g., chatbots, recommendation systems).  
- **High Throughput**: Handle thousands of concurrent requests.  
- **Full Model Deployment**: Support for large-scale models without compression or optimization.  
- **Infrastructure**: Bare-metal GPU clusters (e.g., `chi@uc`).  

**Example Use Case**:  
AI-powered customer support for large enterprises.  

---

###### 2. Resource-Constrained Edge Deployment  
**Target Customer**:  
Organizations deploying models on edge devices with limited hardware (e.g., NVIDIA RTX6000).  

**Requirements**:  
- **Low Resource Usage**: Optimized for minimal memory and compute power.  
- **Medium to Low Throughput**: Handle thousands of concurrent requests.
- **Small Model Deployment**: Lightweight models or LoRA adapters for task-specific inference.  
- **Infrastructure**: Bare-metal GPU resources (e.g., `chi@uc`).  

**Example Use Case**:  
AI-powered customer support for small to medium size team in enterprise.  

---

###### 3. Cloud-Based Virtual Machine Deployment  
**Target Customer**:  
Organizations using cloud-based virtual machines (e.g., AWS, Azure, GCP) with moderate hardware.  

**Requirements**:  
- **Scalability**: Auto-scaling support for variable workloads.  
- **Cost Efficiency**: Optimized deployments to reduce cloud costs.  
- **Hybrid Models**: Mix of full models and lightweight adapters (e.g., LoRA) based on demand.  
- **Infrastructure**: Virtual machines with GPUs available on-demand. 

**Example Use Case**:  
AI-powered customer support for various team size. 




3. Model Optimizations
Implementation: Model optimizations are handled in the scripts/langchain-rag-vllm.py script, which integrates Retrieval-Augmented Generation (RAG) with vLLM for efficient inference.
Results:
Reduced latency by optimizing retrieval and generation steps.
Improved accuracy by using context-aware prompts.
4. System Optimizations
Implementation: System optimizations are achieved through:
NGINX Configuration: scripts/nginx.conf for load balancing and reverse proxying.
Docker Compose: scripts/docker-compose.yml for containerized deployments.
Results:
Enhanced scalability by distributing traffic across multiple instances.
Simplified deployment and resource management.
5. Offline Evaluation of Model
Implementation: Offline evaluation is performed using the test suite in the optimization/perform_offline_evaluation_against_score_endpoint folder.
test_score.py: Evaluates model accuracy against a predefined dataset.
test_language_model_comparison.py: Compares the model's responses with a commercial-grade model.
Results: Results are logged in the test output and can be integrated with MLFlow for tracking.
6. Load Test in Staging
Implementation: Load testing is performed using the test suite in the optimization/load_test folder.
test_simple_load_test.py: Sends concurrent requests to the vLLM server and measures throughput, latency, and success rate.
Results:
Throughput: 5.12 requests/s
Average Latency: 0.19s
Success Rate: 100%
7. Define a Business-Specific Evaluation
Hypothetical Evaluation: Evaluate the model's ability to generate domain-specific responses for legal documents.
Metric: Measure the accuracy of legal terminology and compliance with regulatory standards.
Implementation: Use a custom dataset of legal questions and expected answers for evaluation.
8. Online Evaluation/Close the Loop
Implementation:
Monitoring dashboards are implemented in the monitoring folder.
fastapi-dashboard.json: Tracks API performance metrics.
vllm-dashboard.json: Monitors vLLM server performance.
Feedback loop is integrated into the API to collect user feedback for improving the model.
Results:
Real-time monitoring of latency, throughput, and error rates.
Continuous improvement of the model based on user feedback.
Notes
Ensure all dependencies are installed before running the scripts.
Refer to the individual README files in each subfolder for detailed instructions.

  