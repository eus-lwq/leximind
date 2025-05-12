# Leximind

A question answering platform designed to answer junior developers' coding, general, and onboarding questions to reduce learning time and learning curve when contributing to open source projects.

## Team Members

| Name | NetID | Email | Responsibility |
|------|-------|-------|----------------|
| Tyler Li | WL3187 | w.li@nyu.edu | CI/CD |
| Zeyuan Shen | zs2902 | zs2902@nyu.edu | Training |
| Mohammed Zakriah Ibrahim | mi2471 | mi2471@nyu.edu | Data Pipeline |
| Xing Fang | xf757 | xf757@nyu.edu | Model Serving |

## 1.1 Value Proposition

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
- **Bootstrapping with Terraform**: [Terraform Configuration](https://github.com/eus-lwq/leximind/blob/serving/serving/main.tf)
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

### ETL Steps:

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

### Data Division:
- 80% training, 20% testing
- Repository documentation goes to RAG database
- Stack Overflow Q&A used for evaluation

### Data Leakage Prevention:
- Ensuring no mixing of testing/training data

## 4.1 Modeling

Our modeling approach treats the task as an instruction-based generation problem, where the model receives a natural language question about source code—often related to a function, class, or file—and produces a detailed, context-aware answer that may include explanations or relevant code. To support this, we fine-tune LLaMA-3-8B-Instruct. Its architecture is well-suited for tasks that require structured reasoning over programming logic. Compared to larger variants (e.g., 13B or 70B), the 8B model offers sufficient capacity for deep code understanding while remaining lightweight enough for efficient fine-tuning and inference on a single A100 GPU.

By training on Q&A pairs, the model is adapted to understand project-specific codebases and respond accurately to developer-level technical questions. It also integrates a retrieval-augmented generation (RAG) pipeline, enabling real-time grounding of responses in live documentation or source files. Overall, this architecture provides a scalable and effective solution for building domain-adapted code assistants.

## 4.2 Train and re-train

In our project, we train and retrain a large language model using a custom instruction-following dataset derived from the CodeQA benchmark. CodeQA contains question–answer pairs grounded in source code written in Python and Java. We converted these examples into the Alpaca format (instruction–input–output) to support instruction tuning. The resulting dataset, includes approximately 60,000 question–answer pairs, and enables the model to learn how to answer natural language questions about real-world code functions, files, and APIs.

The base model is Meta-LLaMA-3-8B-Instruct, an 8B-parameter decoder-only transformer released by Meta. We fine-tune this model using LoRA for parameter-efficient training, and we use bf16 mixed-precision with gradient accumulation to fit the training process on a single A100 80GB GPU (compute-gigaio node) on Chameleon Cloud.

We retrain with new production data by collecting user feedback in a separate file (feedback_data/pending.jsonl). A scheduled pipeline checks this file daily using a cron job. If more than 1000 new samples are detected, the pipeline automatically merges them into the training dataset and launches a new training run using train.sh.

We use MLflow to monitor and log the entire training workflow, including both initial training and retraining runs. Each run is recorded with detailed metadata such as training configuration, loss curves, and run names, allowing us to track model performance over time.

## 4.3 Justification of Modeling Choices

We selected Meta-LLaMA-3-8B-Instruct as our base model for the following reasons:
- It is a strong instruction-tuned LLM, capable of understanding both general and domain-specific prompts.
- At 8 billion parameters, it achieves a balance between capacity and trainability on a single A100 80GB GPU.
- It is publicly available and compatible with Hugging Face, allowing for seamless integration into llama-factory.

Since full fine-tuning of such a large model is computationally expensive and memory-intensive, we adopted LoRA with rank 8. We injected LoRA modules into critical projection layers, including attention heads (q_proj, k_proj, v_proj, o_proj) and MLP components (gate_proj, up_proj, down_proj).

We conducted several controlled experiments to determine the most effective training configuration. Below are the key decisions and the rationale:

- **Batch size & accumulation**: Due to GPU memory constraints, we used a per-device batch size of 8 and gradient_accumulation_steps=8, giving an effective batch size of 64. We found this provided stable convergence without OOM errors.
- **Cutoff length**: We set --cutoff_len=512 to avoid exceeding VRAM limits and to encourage the model to focus on concise, localized code explanations.
- **Precision**: We used bf16 (rather than fp32 or fp16) to reduce memory usage while maintaining training stability.
- **Learning rate**: After testing several values in the range of 1e-4 to 1e-5, we selected 5e-5, which provided fast convergence without oscillations. We used a linear learning rate scheduler with warmup ratio 0.03 and gradient clipping (max_grad_norm=0.3).
- **Epochs**: We trained for 1.5 epochs on a 60,000-sample dataset (QACode), balancing underfitting risk and cost.

## 4.4 Justification of Modeling Choices

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

## 5.1 Serving from an API point
- serving endpoint: vLLM serving point + Fast API
- input: user input query. e.g question to the repository
- output:answer from llm model
<img width="1096" alt="Screenshot 2025-05-11 at 8 11 35 PM" src="https://github.com/user-attachments/assets/9bedb0b4-a48e-4fa4-884e-e0fe7a1fc303" />

## 5.2 
