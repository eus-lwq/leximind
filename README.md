# LexiMind - Chat with your repository!

## Value Proposition
<!-- 
Discuss: Value proposition: Your will propose a machine learning system that can be used in an existing business or service. (You should not propose a system in which a new business or service would be developed around the machine learning system.) Describe the value proposition for the machine learning system. What’s the (non-ML) status quo used in the business or service? What business metric are you going to be judged on? (Note that the “service” does not have to be for general users; you can propose a system for a science problem, for example.)
-->
- user: junior developer just onboarding to do open source project
- metrics: deliverables, accepted PRs (6 months)
- copyright: open source wiki / open source repo / papers/ docs. free for academic / open source / not for commercial, license issue for academic use


### Contributors

<!-- Table of contributors and their roles. First row: define responsibilities that are shared by the team. Then each row after that is: name of contributor, their role, and in the third column you will link to their contributions. If your project involves multiple repos, you will link to their contributions in all repos here. -->

| Name                            | Responsible for | Link to their commits in this repo |
|---------------------------------|-----------------|------------------------------------|
| Tyler Li                   |        CICD         |                                    |
| Zeyuan Shen                   |       Training          |                                    |
| Mohammed Zakriah Ibrahim                   |       Data          |                                    |
| Xing Fang |    Model Serving              |                                   |



### System diagram

<!-- Overall digram of system. Doesn't need polish, does need to show all the pieces. Must include: all the hardware, all the containers/software platforms, all the models, all the data. -->
[graph here]
### Summary of outside materials

<!-- In a table, a row for each dataset, foundation model. Name of data/model, conditions under which it was created (ideally with links/references), conditions under which it may be used. -->
## QA Pair Dataset

| Dataset Name | Size (Records) | Link | Source | Description | Dataset Example | Notes | How It Was Created | Conditions of Use |
|-------------|--------------|------|--------|-------------|----------------|-------|----------------|-----------------|
| **SQuAD 2.0** | 150,000+ questions | [SQuAD 2.0](https://rajpurkar.github.io/SQuAD-explorer/) | Stanford University | Combines over 100,000 questions from SQuAD 1.1 with over 50,000 unanswerable questions written adversarially to test the model's ability to abstain from answering when no answer is available in the context. | "What is the capital of France?" with the answer "Paris" found in the given context. | Widely used benchmark for machine reading comprehension. | Questions were crowd-sourced based on Wikipedia articles; unanswerable questions were crafted to resemble answerable ones. | Available for non-commercial use under the CC BY-SA 4.0 license. |
| **Natural Questions** | 323,045 questions | [Natural Questions](https://ai.google.com/research/NaturalQuestions) | Google AI | Real anonymized, aggregated queries issued to the Google search engine, paired with corresponding Wikipedia pages containing the answer. | "What is the tallest mountain in the world?" with the answer "Mount Everest" found in the provided Wikipedia article. | Reflects real-world search queries, providing a realistic QA training set. | Questions are real user queries; answers were annotated by human raters. | Available under the CC BY-SA 3.0 license. |
| **TriviaQA** | 650,000 question-answer-evidence triples | [TriviaQA](http://nlp.cs.washington.edu/triviaqa/) | University of Washington | Contains question-answer pairs from trivia and quiz-league websites, along with evidence documents gathered via Bing and Wikipedia searches. | "Who wrote 'To Kill a Mockingbird'?" with the answer "Harper Lee" and supporting documents from search results. | Includes both web and Wikipedia subsets; useful for open-domain QA. | Questions were scraped from trivia websites; evidence documents were retrieved using search engines. | Available for research purposes; see the dataset license for details. |
| **HotpotQA** | 113,000 questions | [HotpotQA](https://hotpotqa.github.io/) | Carnegie Mellon University & Stanford University | Designed for multi-hop question answering, requiring reasoning over multiple documents to arrive at the answer. | "What is the connection between Marie Curie and the discovery of radium?" requiring information from multiple documents to answer. | Emphasizes explainability by providing supporting facts for each answer. | Questions were crowd-sourced with instructions to require multi-hop reasoning; supporting documents were provided to annotators. | Available under the CC BY-SA 4.0 license. |
| **OpenBookQA** | 5,957 multiple-choice questions | [OpenBookQA](https://allenai.org/data/open-book-qa) | Allen Institute for AI | Focuses on elementary-level science questions that require combining a provided fact ("open book") with external knowledge. | "What happens to water when it is heated?" with choices: A) It freezes, B) It evaporates, C) It condenses, D) It stays the same. Correct answer: B) It evaporates. | Tests the ability to apply elementary science facts to novel situations. | Questions were created based on science facts and require combining the fact with external knowledge to answer. | Available under the CC BY-SA 4.0 license. |
| **DROP (Discrete Reasoning Over Paragraphs)** | 96,567 questions | [DROP](https://allenai.org/data/drop) | Allen Institute for AI | Requires discrete reasoning over paragraphs, such as addition, counting, or sorting, to answer questions. | "How many times did the team win between 2010 and 2015?" requiring counting wins mentioned in the text. | Focuses on numerical reasoning and discrete operations over text. | Questions were crowd-sourced with a focus on requiring discrete reasoning over provided paragraphs. | Available under the CC BY-SA 4.0 license. |


## Coding Pair Datasets

| Dataset Name | Size (Records) | Link | Source | Description | Dataset Example | Notes | How It Was Created | Conditions of Use |
|-------------|--------------|------|--------|-------------|----------------|-------|----------------|-----------------|
| **CodeSearchNet** | 6 million functions | [CodeSearchNet](https://github.com/github/CodeSearchNet) | GitHub | A dataset of functions with associated documentation from open-source projects across six programming languages (Go, Java, JavaScript, PHP, Python, Ruby). | A Python function with its corresponding docstring. | Useful for code search and code summarization tasks. | Collected from public GitHub repositories; functions paired with their docstrings. | Available under the MIT License. |
| **CoNaLa (Code/Natural Language Challenge)** | 2,879 annotated examples | [CoNaLa](https://conala-corpus.github.io/) | Carnegie Mellon University | A dataset of natural language intents and corresponding Python code snippets, focusing on how people express coding tasks in natural language. | "How to convert a list of strings to integers in Python?" with the corresponding code `list(map(int, list_of_strings))`. | Emphasizes the translation of natural language to code. | Collected from Stack Overflow posts; manually annotated to ensure quality. | Available under the CC BY-SA 4.0 license. |
| **Django Dataset** | 18,805 examples | [Django Dataset](https://homepages.inf.ed.ac.uk/s1358032/DJANGO/) | University of Edinburgh | A dataset of Python code snippets paired with English descriptions, extracted from the Django web framework documentation. | English description: "Return the number of records in the database." Code: `Model.objects.count()`. | Useful for code generation and code summarization tasks. | Extracted from Django documentation; paired code snippets with their descriptions. | Available under the BSD 3-Clause License. |
| **SPoC (Structured Python Code)** | 18,356 examples | [SPoC](https://github.com/microsoft/SPoC) | University of Edinburgh | A dataset of Python code snippets paired with pseudocode annotations, focusing on the translation between pseudocode and code. | Pseudocode: "Initialize a list of numbers from 1 to 10." Code: `numbers = list(range(1, 11))`. | Aims to bridge the gap between human-readable pseudocode and executable code. | Collected from programming education platforms; annotated with corresponding pseudocode. | Available under the MIT License. |
| **APPS (Automated Programming Progress Standard)** | 10,000 problems | [APPS](https://github.com/hendrycks/apps) | UC Berkeley | A dataset of coding problems and solutions, designed to evaluate the problem-solving abilities of AI systems in competitive programming. | Problem statement: "Write a function to check if a number is prime." Solution: Python function implementing prime check logic. | Challenges models with diverse and complex programming tasks. | Collected from open-source competitive programming platforms; includes problems of varying difficulty. | Available under the MIT License. |


|              | How it was created | Conditions of use |
|--------------|--------------------|-------------------|
| Data set 1   |                    |                   |
| Data set 2   |                    |                   |
| Base model 1 |                    |                   |
| etc          |                    |                   |


### Summary of infrastructure requirements

<!-- Itemize all your anticipated requirements: What (`m1.medium` VM, `gpu_mi100`), how much/when, justification. Include compute, floating IPs, persistent storage. The table below shows an example, it is not a recommendation. -->

| Requirement     | How many/when                                     | Justification |
|-----------------|---------------------------------------------------|---------------|
| `m1.medium` VMs | 3 for entire project duration                     | ...           |
| `gpu_mi100`     | 4 hour block twice a week                         |               |
| Floating IPs    | 1 for entire project duration, 1 for sporadic use |               |
| etc             |                                                   |               |

### Detailed design plan

<!-- In each section, you should describe (1) your strategy, (2) the relevant parts of the diagram, (3) justification for your strategy, (4) relate back to lecture material, (5) include specific numbers. -->
<img src="assets/train_diagram.jpg" width="600"/>


#### Model training and training platforms

<!-- Make sure to clarify how you will satisfy the Unit 4 and Unit 5 requirements, and which optional "difficulty" points you are attempting. -->

#### Model serving and monitoring platforms

<!-- Make sure to clarify how you will satisfy the Unit 6 and Unit 7 requirements,  and which optional "difficulty" points you are attempting. -->

#### Data pipeline
# Data Pipeline Design

This design addresses the requirements for persistent storage, offline data management and pipelines, online data management and pipelines, and online data simulation.

## 1. Persistent Storage (Chameleon)

**Technology:** Chameleon Block Storage (e.g., Cinder volumes).

### Setup:
- Provision a sufficiently large block storage volume on Chameleon.
- Attach this volume to the virtual machine(s) designated for data processing, model training, and potentially hosting the vector database/data repositories.
- Format and mount the volume (e.g., as `/mnt/persistent_data`).

### Purpose:
This mounted volume (`/mnt/persistent_data`) will serve as the central, persistent location for:
- **Raw Data:** Original downloaded datasets (QA pairs, Coding pairs), cloned open-source repositories.
- **Processed Data:** Cleaned and transformed data ready for fine-tuning (e.g., formatted JSONL/Parquet files).
- **RAG Knowledge Base:** Chunked documents/code, vector embeddings/indices, metadata mapping.
- **Model Artifacts:** Fine-tuned LLM weights, tokenizer files.
- **Evaluation Artifacts:** Test sets, reference answers, evaluation script outputs (scores).
- **Container Images:** Custom Docker images saved as tarballs (though a container registry is often preferable).
- **Logs:** Persistent logs from ETL jobs or training runs.

## 2. Offline Data Management & Pipeline (ETL for Fine-tuning & RAG)

This pipeline focuses on ingesting, processing, and storing data needed for fine-tuning the LLM and populating the RAG knowledge base.

### Data Sources:
- **QA Datasets:** SQuAD 2.0, Natural Questions, TriviaQA, HotpotQA, OpenBookQA, DROP.
- **Coding Pair Datasets:** CodeSearchNet, CoNaLa, Django Dataset, SPoC, APPS.
- **Target Open-Source Repositories:** Specific GitHub repositories containing code and documentation (README files, markdown documentation, Wikis, etc.).

### ETL Pipeline Steps:
#### **Extract (E):**
- **Download Datasets:** Write scripts (e.g., Python with `requests`, `huggingface datasets`) to download datasets.
- **Clone Repositories:** Use `gitpython` to clone target repositories into `/mnt/persistent_data/raw/repositories/`.

#### **Transform (T):**
- **Standardize QA/Coding Data:**
  - Parse raw datasets (JSON, CSV, etc.).
  - Clean text data (normalize whitespace, handle special characters).
  - Convert into a unified format suitable for fine-tuning (e.g., JSON Lines `{"prompt": "...", "completion": "..."}`).
  - Store processed data in `/mnt/persistent_data/processed/finetuning_data/`.
- **Process Repositories for RAG:**
  - Identify relevant files (code, documentation, configuration files).
  - Extract and parse code/documentation content.
  - Chunk large documents and code files.
  - Generate embeddings using a sentence transformer model.
  - Store processed chunks & metadata in `/mnt/persistent_data/processed/rag_data/chunks/`.
  - Build vector index using FAISS, storing it in `/mnt/persistent_data/processed/rag_data/vector_index/`.

#### **Load (L):**
- Fine-tuning data is ready in `/mnt/persistent_data/processed/finetuning_data/`.
- RAG knowledge base is ready in `/mnt/persistent_data/processed/rag_data/`.
- **Orchestration:** Simple Python scripts or workflow tools like Makefiles, Luigi, or Airflow.

## 3. Online Data Management & Pipeline (Inference)

This pipeline handles incoming user queries in real-time using the fine-tuned LLM and the RAG system.

### Data Source:
- Real-time user queries arriving via the chatbot's API endpoint.

### Pipeline Steps:
1. **Receive & Pre-process Query:** Accept user input, clean text.
2. **Generate Query Embedding:** Use the same embedding model as offline processing.
3. **Retrieve Relevant Context (RAG):**
   - Query FAISS Vector Index.
   - Fetch the top-k similar chunks.
   - Retrieve text and metadata from the Chunk Store.
4. **Construct Prompt:** Format query and retrieved chunks for the LLM.
5. **LLM Inference:** Generate a response using the fine-tuned model.
6. **Post-process Response:** Clean output, optionally cite sources.
7. **Return Response:** Send the formatted answer back to the user.

### Data Storage (Online Access):
- The Vector Index and Chunk/Metadata Store are loaded into memory or accessed efficiently.
- The fine-tuned LLM model weights are loaded into GPU/CPU memory.

## 4. Online Data Simulation

### **Purpose:**
To generate realistic traffic for load testing the online inference pipeline and evaluating system performance (latency, concurrency).

### **Script (simulate_traffic.py):**
#### **Query Generation:**
- Use query templates like:
  - "How does the function `{func_name}` work?"
  - "Explain the `{class_name}` class in `{file_path}`."
  - "Summarize the file `{file_path}`."
- Populate templates using extracted function/class names.
- Include adversarial or out-of-scope questions for robustness.
- Adapt portions of QA datasets to codebase queries.

#### **Traffic Pattern:**
- Use `asyncio` and `aiohttp` for asynchronous request generation.
- Control request rate (e.g., 1 req/sec to 100 req/sec for testing limits).
- Simulate multiple concurrent users.
- Introduce randomness in query selection and timing.
- Run from a separate VM or container within the Chameleon environment.

### **Data Characteristics:**
- **Content:** Questions covering code understanding, API usage, module interaction.
- **Format:** Plain text strings sent via HTTP POST/GET requests.
- **Volume:** Configurable rate (e.g., 1 req/sec to 100 req/sec).
- **Variety:** Mix of targeted questions and open-ended exploratory questions.

### **Output:**
- Log response times, status codes, and response latencies for performance analysis.

<img src="assets/data pipeline.png" width="600"/>
<!-- Make sure to clarify how you will satisfy the Unit 8 requirements,  and which optional "difficulty" points you are attempting. -->

#### Continuous X

<!-- Make sure to clarify how you will satisfy the Unit 3 requirements,  and which optional "difficulty" points you are attempting. -->


