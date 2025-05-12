# Leximind

A question answering platform designed to answer junior developers' coding, general, and onboarding questions to reduce learning time and learning curve when contributing to open source projects.

<img width="548" alt="Screenshot 2025-05-11 at 11 31 25 PM" src="https://github.com/user-attachments/assets/258fdce4-9587-45f1-96db-1302a79c2de6" />

## Team Members

| Name | NetID | Email | Responsibility |
|------|-------|-------|----------------|
| Tyler Li | WL3187 | w.li@nyu.edu | CI/CD |
| Zeyuan Shen | zs2902 | zs2902@nyu.edu | Training |
| Mohammed Zakriah Ibrahim | mi2471 | mi2471@nyu.edu | Data Pipeline |
| Xing Fang | xf757 | xf757@nyu.edu | Model Serving |

## 1.1 Value Proposition
<img width="1144" alt="Screenshot 2025-05-11 at 11 32 26 PM" src="https://github.com/user-attachments/assets/462ecb8a-ab26-46e9-9016-370795e70725" />

- **Product**: A question answering platform that helps junior developers with coding, general, and onboarding questions to reduce the learning curve
- **Target Customer**: Junior developers newly onboarded to open source projects who want to contribute
- **Customer Influence on System Design**: Data consists of coding pairs and normal Q&A pairs

## 1.2 Scale

- **Data Size**: 100MB
- **Model Size**: 15.03GB (Llama-3-8B-instruct)
- **Training Time**: 
  - 1-2 hours on A100 (CHI@UC computer_gigao)
  - 2-4 hours on RTX6000 (CHI@UC rtx_6000)
- **Deployment Size**: ~10 inference requests per day

## 2.1 Architecture
![mlops-slide drawio (3)](https://github.com/user-attachments/assets/a9a3622d-c72d-4d3b-a72f-4aac44ef602f)
- **Cloud Native Diagram**: [DrawIO Diagram](https://drive.google.com/file/d/11_f7X4CHkGKUbLRe_rqd6tyC4CPW15L_/view?usp=sharing)

## 2.2 Infrastructure and Infrastructure-as-Code

- **Bootstrapping with Python-CHI**: [Project Bootstrapping Notebook](https://github.com/eus-lwq/leximind/blob/dev_infra/project6_bootstrapping.ipynb)
- **Bootstrapping with Terraform**: [Terraform Configuration](https://github.com/eus-lwq/leximind/tree/serving/serving)
- **Docker for Training**: [Training Docker Compose](https://github.com/eus-lwq/leximind/blob/dev_infra/docker-compose.yaml)
- **Docker for Serving**: [Serving Script](https://github.com/eus-lwq/leximind/blob/serving/serving/scripts/vllm_serving.sh)

## 3.1 Persistent Storage

| Resource Name | Purpose | Storage Type | Location | Size |
|---------------|---------|--------------|----------|------|
| data_project6 | Training/Test Dataset Volume (15k records) | Object Storage | BareMetal on CHI@UC | 100 MB |
| leximind_project6 | Fine-Tuned LoRA and Base Model Files | Object Storage | BareMetal on CHI@UC | 15 GB |
| block-persist-project6 | RAG Database | Block Storage | VM KVM@TACC | 10 GB |
| leximind-project6-terraform-state | Terraform Configuration State text file | Object Storage | BareMetal on CHI@UC | 20 bytes |

## 3.2 Offline Data: Datasets

### CodeQA
CodeQA is a free-form question answering dataset for source code comprehension. Given a code snippet and a question, a textual answer is generated. The dataset contains:
- Java dataset: 119,778 question-answer pairs
- Python dataset: 70,085 question-answer pairs

#### Sample:
```
Question: How do all tags in an html tree convert to xhtml?

Code:
def html to xhtml html try html html getroot except Attribute Error passprefix '{%s}' % XHTML NAMESPACE for el in html iter etree Element tag el tagif tag[ 0 ] '{' el tag prefix + tag

Answer: by moving them to the xhtml namespace
```

### CoNaLa Dataset
A dataset crawled from Stack Overflow, automatically filtered, then curated by annotators:
- 2,379 training examples
- 500 test examples

#### Sample:
```json
{
  "intent": "How do I check if all elements in a list are the same?", 
  "rewritten_intent": "check if all elements in list `mylist` are the same", 
  "snippet": "len(set(mylist)) == 1", 
  "question_id": 22240602
}
```

### Data Transformation
For fine-tuning Llama 3.1 using LLaMa factory, we transform the data to the alpaca format:

```json
{
  "instruction": "Summarize the following article:",
  "input": "<<!nav>>article content<<!/nav>>",
  "output": "A concise summary of the article."
}
```

## 3.3 Data Pipeline


## 3.3.1 ETL Steps:

1. **Extract**:
   - CodeQA dataset: Extracted from Google Drive
   - CoNaLa dataset: Extracted from an online zip

2. **Transform & Combine**:
   - CodeQA: Match question, answer, and code files in alpaca format
     - Question → instruction
     - Code → input
     - Answer → output
   - CoNaLa: Transform intent as input and snippet as output
   - Both datasets are combined and shuffled into a single final dataset

3. **Load**:
   - Load transformed datasets into object store data_project6
   - Files: data/train.json (150k examples) and data/test.json (19k examples)

Here is the Docker compose file that implements this: [ETL CodeQA](https://github.com/eus-lwq/leximind/blob/data/data/data_pipeline/docker-compose-etl.yaml)

## 3.3.2 RAG Pipeline:

The RAG pipeline converts the GitHub repository documentation into vector embeddings and stores them in block storage. This data is later used as context during inference while querying the LLM. 

Here is the folder that implements this: [RAG pipeline](https://github.com/eus-lwq/leximind/tree/data/data/rag_pipeline)

### Data Division:
- 80% training, 20% testing
- Repository documentation goes to RAG database
- Stack Overflow Q&A used for evaluation

### Data Leakage Prevention:
- Ensuring no mixing of testing/training data

## 4.1 Modeling
Our model takes a natural language question as input, such as “What does this function do?”, and uses it to retrieve related content from code and documentation. This context, together with the question, is passed to a fine-tuned LLaMA model which generates a natural language answer. The process helps developers quickly understand code by providing accurate, context-aware explanations.

<img width="1253" alt="Screenshot 2025-05-11 at 11 59 08 PM" src="https://github.com/user-attachments/assets/4ec65d71-62ff-4d7d-8fc4-894266d68c5e" />
We fine-tune the LLaMA-3-8B-Instruct model using the llama-factory framework with the CodeQA dataset formatted in Alpaca-style instruction-based JSON. Training is performed on a single A100 GPU, which provides sufficient capacity for efficient fine-tuning. The LLaMA-3-8B architecture strikes a balance between performance and resource efficiency, making it well-suited for understanding and answering developer-level questions about source code. This setup enables the model to generate accurate and context-aware responses based on code-related prompts.

## 4.2 Train and re-train
In our project, we train and retrain a large language model using a custom instruction-following dataset derived from the CodeQA benchmark. CodeQA contains question–answer pairs grounded in source code written in Python and Java. We converted these examples into the Alpaca format (instruction–input–output) to support instruction tuning. The resulting dataset, includes approximately 60,000 question–answer pairs, and enables the model to learn how to answer natural language questions about real-world code functions, files, and APIs.

The base model is Meta-LLaMA-3-8B-Instruct, an 8B-parameter decoder-only transformer released by Meta. We fine-tune this model using LoRA for parameter-efficient training, and we use bf16 mixed-precision with gradient accumulation to fit the training process on a single A100 80GB GPU (compute-gigaio node) on Chameleon Cloud.

You can find the training details [here](https://github.com/eus-lwq/leximind/blob/dev_eric/pipeline/train_pipeline.md)

We collect user feedback via MinIO and periodically merge new feedback data into the training set. A weekly scheduled job on a self-hosted runner retrains the model using the updated data to ensure it remains aligned with recent user behavior.

You can find the re-training details [here](https://github.com/eus-lwq/leximind/blob/main/.github/workflows/retrain.yml)

We use MLflow to monitor and log the entire training workflow, including both initial training and retraining runs. Each run is recorded with detailed metadata such as training configuration, loss curves, and run names, allowing us to track model performance over time.

![image](https://github.com/user-attachments/assets/f1ce6497-e59f-4399-88bb-e91db740dbdd)

## 4.3 Justification of Modeling Choices

We selected Meta-LLaMA-3-8B-Instruct as our base model for the following reasons:
- It is a strong instruction-tuned LLM, capable of understanding both general and domain-specific prompts.
- At 8 billion parameters, it achieves a balance between capacity and trainability on a single A100 80GB GPU.
- It is publicly available and compatible with Hugging Face, allowing for seamless integration into llama-factory.

Since full fine-tuning of such a large model is computationally expensive and memory-intensive, we adopted LoRA with rank 8. We injected LoRA modules into critical projection layers, including attention heads (q_proj, k_proj, v_proj, o_proj) . This decrease the training time from 2hours/epoch to 80minutes/epoch compared to default lora settings.

We conducted several controlled experiments to determine the most effective training configuration. Below are the key decisions and the rationale:

- **Batch size & accumulation**: Due to GPU memory constraints, we used a per-device batch size of 8 and gradient_accumulation_steps=8, giving an effective batch size of 64. We found this provided stable convergence without OOM errors.
- **Cutoff length**: We set --cutoff_len=512 to avoid exceeding VRAM limits and to encourage the model to focus on concise, localized code explanations.
- **Precision**: We used bf16 (rather than fp32 or fp16) to reduce memory usage while maintaining training stability.
- **Learning rate**: After testing several values in the range of 1e-4 to 1e-5, we selected 5e-5, which provided fast convergence without oscillations. We used a linear learning rate scheduler with warmup ratio 0.03 and gradient clipping (max_grad_norm=0.3).
- **Epochs**: We trained for 1.5 epochs on a 60,000-sample dataset (QACode), balancing underfitting risk and cost.

ref: https://github.com/eus-lwq/leximind/blob/main/train/llama-factory/train.sh
 

## 4.4 Model Optimizations for training

To train LLaMA-3-8B-Instruct model, we applied several strategies to decrease the training time and try to make a balance between model performance and training time.

1. **LoRA**
   We used LoRA with --lora_rank=8, and targeting:
   lora_target="q_proj,k_proj,v_proj,o_proj
   This allowed us to fine-tune only a small subset of the model parameters, while freezing the rest.
   - With LoRA: 1 epoch ≈ 80 minutes
   - Without LoRA (full finetune): really long time

2. **bf16**
   - With bf16: Training stable, no overflow, fits batch size 8
   - Without bf16 (fp32): OOM unless batch size ≤ 4; training slowed to > 120 minutes per epoch

3. **Gradient Accumulation**
   - --per_device_train_batch_size=8
   - --gradient_accumulation_steps=8
   - With accumulation: Stable convergence in 80 min
   - Without accumulation: need higher batch size and the model cant converge, otherwise needs 8 hours to train one epoch



## 4.5 Experiment tracking 
We use Ray train to schedule training jobs along with grafana and mlflow for tracking the various experiments.

1. [Ray training monitoring compose file](https://github.com/eus-lwq/leximind/blob/dev_infra/docker-compose.yaml)

![image](https://github.com/user-attachments/assets/b6034969-0760-40f5-bdcd-16c9430fa03f)

2. [Ray Submit file](https://github.com/eus-lwq/leximind/blob/dev_infra/ray_scripts/ray_submit.py)

![image](https://github.com/user-attachments/assets/7af8514a-4aed-4f91-a07d-7eca6842fc47)

3. Ray Overview

![image](https://github.com/user-attachments/assets/d990710c-e74f-4fd9-95d7-e3dcfe7691c7)

4. Grafana Monitoring dashboard

![image](https://github.com/user-attachments/assets/303872ed-fa6d-4a25-bf5c-5c46ca204bde)


## 4.6 Model Evaluation Summary (Prediction Phase)
During the prediction phase, we assessed the performance of our fine-tuned **LLaMA-based model** using both standard automatic metrics and semantic similarity analysis. The results demonstrate promising generalization and meaningful language understanding, with clear potential for further refinement.

#### 📈 Automatic Generation Metrics
- **BLEU-4:** 26.03  
  *A solid score that reflects the model’s ability to generate n-gram overlaps with reference outputs. While there's space for improvement, this indicates the model often captures key phrases or structure correctly.*

- **ROUGE Scores:**
  - **ROUGE-1:** 38.61  
  - **ROUGE-2:** 16.17  
  - **ROUGE-L:** 36.58  
  *These scores show that the model retains a strong ability to reflect relevant content (unigrams) and captures some phrase-level structure (ROUGE-L). The moderate ROUGE-2 suggests that fluency and phrase continuity are being learned, but could benefit from further optimization.*

### 🧠 Semantic Similarity (OpenAI Embeddings)
- **Average Embedding Similarity:** 0.559 (using `text-embedding-3-small`)  
  *This similarity score indicates that the model’s predictions are, on average, semantically aligned with the ground truth. The outputs tend to convey the correct intent, even in cases where exact wording differs—suggesting effective instruction comprehension.*

### ⚙️ Runtime and Throughput
- **Throughput:** 1.10 samples/sec | 0.143 steps/sec  
- **Total Runtime:** ~90 seconds for 100 samples


## 5.1 Serving from an API point
- **Setup**: The API endpoint is implemented using FastAPI, and it provides a `/ask` endpoint for querying the model.
    User could also access the model without RAG through vLLM's OpenAI compatible server.
    
    serving endpoint: [vLLM serving point](https://github.com/eus-lwq/leximind/blob/serving/serving/scripts/vllm_serving_lora_adapter.sh) + [Fast API](https://github.com/eus-lwq/leximind/blob/serving/serving/scripts/app.py)
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

## 5.2 Identify requirements
**1. High-Performance GPU Deployment**

**Target Customer**:  
Organizations with access to high-end GPU clusters (e.g., NVIDIA A100, V100).  

**Requirements**:  
- **Low Latency**: Sub-second response times for real-time applications (e.g., chatbots, recommendation systems).  
- **High Throughput**: Handle thousands of concurrent requests.  
- **Full Model Deployment**: Support for large-scale models without compression or optimization.  
- **Infrastructure**: Bare-metal GPU clusters (e.g., `chi@uc`).  

**Example Use Case**:  
AI-powered customer support for large enterprises.  

**2. Resource-Constrained Edge Deployment**

**Target Customer**:  
Organizations deploying models on edge devices with limited hardware (e.g., NVIDIA RTX6000).  

**Requirements**:  
- **Low Resource Usage**: Optimized for minimal memory and compute power.  
- **Medium to Low Throughput**: Handle thousands of concurrent requests.
- **Small Model Deployment**: Lightweight models or LoRA adapters for task-specific inference.  
- **Infrastructure**: Bare-metal GPU resources (e.g., `chi@uc`).  

**Example Use Case**:  
AI-powered customer support for small to medium size team in enterprise.  

**3. Cloud-Based Virtual Machine Deployment**

**Target Customer**:  
Organizations using cloud-based virtual machines (e.g., AWS, Azure, GCP) with moderate hardware.  

**Requirements**:  
- **Scalability**: Auto-scaling support for variable workloads.  
- **Cost Efficiency**: Optimized deployments to reduce cloud costs.  
- **Hybrid Models**: Mix of full models and lightweight adapters (e.g., LoRA) based on demand.  
- **Infrastructure**: Virtual machines with GPUs available on-demand. 

**Example Use Case**:  
AI-powered customer support for various team size. 

## 5.3 Model optimizations
- **Model-Level Optimization: Half Precision and 8-Bit Quantization with vLLM:**
   
   Reduces the model’s numerical precision to half, to accomodate GPU restrictions and reduces memory footprint.
   ref: https://github.com/eus-lwq/leximind/blob/serving/serving/scripts/vllm_serving_lora_adapter.sh#L64C1-L65C1

- **Effect on Inference:**
   
   Lower VRAM consumption, enabling larger batch sizes or larger models to run on the same hardware.
   Increased throughput with minimal to moderate impact on accuracy, depending on the calibration method.

## 5.4 System optimizations

1. **Using Batch Inference:**

   Processes multiple inference requests simultaneously, improving hardware utilization and reducing average latency per request under concurrent workloads.
   ref: https://github.com/eus-lwq/leximind/blob/serving/optimization/perform_offline_evaluation_against_score_endpoint/test_language_model_comparison.py#L52C4-L55C40
 
   **Effect on Inference:**

   Higher throughput (more tokens per second). Lower per-request latency in high-concurrency scenarios due to amortized compute costs.

2. **Serving using LoRA Adapter:**

   To accomodate scenarios that has limits on hardware, we could use smaller model with LoRA adapter to fine-tune the model. 
   ref: [`Link to Detailed Comparison`](./serving/use-cases/README.md)

## 5.5 Offline evaluation of model (Offline)
- Offline predict script: https://github.com/eus-lwq/leximind/blob/dev_eric/train/llama-factory/test/predict.sh
- Offline evaluation on llm output and compare with commercial model: https://github.com/eus-lwq/leximind/blob/serving/optimization/perform_offline_evaluation_against_score_endpoint/test_language_model_comparison.py
- Test Score to evaluate relevance: https://github.com/eus-lwq/leximind/blob/serving/optimization/perform_offline_evaluation_against_score_endpoint/test_score.py

## 5.6 Load test in staging (Online)
- load test on 10 request per sec: https://github.com/eus-lwq/leximind/blob/serving/optimization/load_test/test_simple_load_test.py

## 5.7 Define a business-specific evaluation
The effectiveness of our AI assistant can be evaluated based on its impact on developer productivity and repository contributions.
- **Metrics:**
- **Accepted PRs (6 months):** Measures the number of successfully merged pull requests, indicating improved developer output.
- **Time to First Contribution:** Tracks how quickly new developers make their first accepted PR, reflecting faster onboarding.
- **Search-to-PR Conversion Rate:** Measures how often developers using the assistant proceed to make successful contributions.

## 5.8 (optional difficult point) Multiple options for serving
- CPU inference with transformer: https://github.com/eus-lwq/leximind/blob/dev_eric/train/llama-factory/inference/infer_no_vllm.py
- GPU inference with vLLM: https://github.com/eus-lwq/leximind/blob/dev_eric/train/llama-factory/inference/infer.py
allow inference in CPU with transformer and GPU with vLLM/transformer: https://github.com/eus-lwq/leximind/blob/dev_eric/infer_pipeline/docker-compose.cpu.yml

## 6.1 Staged deployment
we put our token/ api keys into repository secret so that runner can use the secret to configure chameleon clouds yaml and keys directly.
<img width="919" alt="Screenshot 2025-05-11 at 9 24 36 PM" src="https://github.com/user-attachments/assets/6c706371-869c-4393-8a52-5e19f06c7987" />

Three stage deployment: 
https://github.com/eus-lwq/leximind/blob/serving_stage_deploy/.github/workflows/stage_deployments.yaml
<img width="979" alt="Screenshot 2025-05-11 at 9 25 25 PM" src="https://github.com/user-attachments/assets/19321426-c22b-435f-8dc0-3415457446b3" />
it's showing fail because currently there's out of KVM@TACC floating point to use...

## 7.1 Online Data 
read fast api post request from serving site and save to MinIO object store automatically
fastapi post (ask) will store the user query and model answer to minio bucket storage: 
https://github.com/eus-lwq/leximind/blob/serving/serving/scripts/app.py#L40
New data store:
https://github.com/eus-lwq/leximind/blob/feedback_loop/label_pipeline/app_labelstudio.py#L86
storage format: 
<img width="612" alt="Screenshot 2025-05-11 at 9 26 19 PM" src="https://github.com/user-attachments/assets/6dfd2482-aae4-43de-8804-6a37e01d3d4c" />
buckets in MiniO:
<img width="694" alt="Screenshot 2025-05-11 at 9 26 38 PM" src="https://github.com/user-attachments/assets/0f2f34f2-a3ab-4bb0-bdae-2d1922c50ae3" />
<img width="685" alt="Screenshot 2025-05-11 at 9 26 49 PM" src="https://github.com/user-attachments/assets/42af1ff3-d87c-4dc5-bb2a-c2c8e945c117" />
<img width="858" alt="Screenshot 2025-05-11 at 9 27 03 PM" src="https://github.com/user-attachments/assets/8d4aef43-603a-4cc1-92b2-4689b44d0048" />

## 8.1 Online evaluation/Close the loop
- we are using the label studio + minio to collect and fix the answer correctness of model output
<img width="904" alt="Screenshot 2025-05-11 at 9 27 33 PM" src="https://github.com/user-attachments/assets/78c96d38-8ff7-4991-8a09-b6c3ad29f21f" />
Code: https://github.com/eus-lwq/leximind/tree/feedback_loop/label_pipeline

## 9.1 CICD
Automatically deploy, offline-eval, retrain, deploy
triggers re-training: weekly every sunday
redeploying: after retrained new model and stored to obj store we will run the deploy pipeline again
retrain pipeline: https://github.com/eus-lwq/leximind/blob/main/.github/workflows/retrain.yml

## 10.1 further thoughts and lesson learned
- challenge 1: evaluation on llm result when we extracted low quality github issues, and using documentation to rag probably not enough to solve some issue
- thoughts: probably use stackoverflow + slack channel Q&A + discord Q&A + twitter + youtube channel in the future

- challenge 2: data is from very different sources hard to preprocess at once
- thoughts: process differently with different process logic, using lfs/jsonl processor to process hugging face datasets, using simple cleaner to clean some formatted kaggle datasets

- challenge 3: 7b model maybe not good enough to retrieve and answer questions very accurately due to its context window length
- thoughts: using an API like OpenAI/Anthropic API directly can reduce the costs of model storage, inference, and also get longer context window, higher quality model answers.

- challenge 4: data from github issue is not well-formatted, sometimes the question is not actually resolved it just closed due to a feature being added, this is not a bug..etc. sometimes they have multiple threads discussing the problem but nobody gave a correct final answer.
- thoughts: using stackoverflow qa at least they will give answer, not just discussion
