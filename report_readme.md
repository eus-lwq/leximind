# Leximind

A question answering platform designed to answer junior developers' coding, general, and onboarding questions to reduce learning time and learning curve when contributing to open source projects.

## Team Members

| Name | NetID | Email | Responsibility |
|------|-------|-------|----------------|
| Tyler Li | WL3187 | w.li@nyu.edu | CI/CD |
| Zeyuan Shen | zs2902 | zs2902@nyu.edu | Training |
| Mohammed Zakriah Ibrahim | mi2471 | mi2471@nyu.edu | Data Pipeline |
| Xing Fang | xf757 | xf757@nyu.edu | Model Serving |

## Value Proposition

- **Product**: A question answering platform that helps junior developers with coding, general, and onboarding questions to reduce the learning curve
- **Target Customer**: Junior developers newly onboarded to open source projects who want to contribute
- **Customer Influence on System Design**: Data consists of coding pairs and normal Q&A pairs

## Scale

- **Data Size**: 100MB
- **Model Size**: 15.03GB (Llama-3-8B-instruct)
- **Training Time**: 
  - 1-2 hours on A100 (CHI@UC computer_gigao)
  - 2-4 hours on RTX6000 (CHI@UC rtx_6000)
- **Deployment Size**: ~10 inference requests per day

## Architecture
![mlops-slide drawio (3)](https://github.com/user-attachments/assets/a9a3622d-c72d-4d3b-a72f-4aac44ef602f)
- **Cloud Native Diagram**: [DrawIO Diagram](https://drive.google.com/file/d/11_f7X4CHkGKUbLRe_rqd6tyC4CPW15L_/view?usp=sharing)

## Infrastructure and Infrastructure-as-Code

- **Bootstrapping with Python-CHI**: [Project Bootstrapping Notebook](https://github.com/eus-lwq/leximind/blob/dev_infra/project6_bootstrapping.ipynb)
- **Bootstrapping with Terraform**: [Terraform Configuration](https://github.com/eus-lwq/leximind/blob/serving/serving/main.tf)
- **Docker for Training**: [Training Docker Compose](https://github.com/eus-lwq/leximind/blob/dev_infra/docker-compose.yaml)
- **Docker for Serving**: [Serving Script](https://github.com/eus-lwq/leximind/blob/serving/serving/scripts/vllm_serving.sh)

## Persistent Storage

| Resource Name | Purpose | Storage Type | Location | Size |
|---------------|---------|--------------|----------|------|
| data_project6 | Training/Test Dataset Volume (15k records) | Object Storage | BareMetal on CHI@UC | 100 MB |
| leximind_project6 | Fine-Tuned LoRA and Base Model Files | Object Storage | BareMetal on CHI@UC | 15 GB |
| block-persist-project6 | RAG Database | Block Storage | VM KVM@TACC | 10 GB |
| leximind-project6-terraform-state | Terraform Configuration State text file | Object Storage | BareMetal on CHI@UC | 20 bytes |

## Datasets

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

## Data Pipeline

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
