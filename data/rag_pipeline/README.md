# 🧠 RAG Pipeline: Vectorize GitHub Documentation using Docker

This pipeline clones a GitHub repository, extracts documentation files, chunks and embeds them using a Sentence Transformer, and stores the vector embeddings and metadata in mounted block storage for later use in a Retrieval-Augmented Generation (RAG) setup.

---

## 📦 Prerequisites

- A VM instance running on [Chameleon Cloud](https://chameleoncloud.org/) using `python-chi`
- Docker installed on the instance
- A block storage volume attached and mounted

---

## 🚀 Step-by-Step Instructions

### 1. 🔗 Attach Block Volume to the VM (in Chameleon Jupyter environment)

```python
cinder_client = chi.clients.cinder()
volume = [v for v in cinder_client.volumes.list() if v.name=='block-persist-project6'][0]

volume_manager = chi.nova().volumes
volume_manager.create_server_volume(server_id=s.id, volume_id=volume.id)
```

---

### 2. 🗂 Mount the Block Volume

SSH into your VM and run:

```bash
sudo mkdir -p /mnt/block
sudo mount /dev/vdb1 /mnt/block
```

---

### 3. 📥 Clone the GitHub Branch

```bash
git clone --branch data https://github.com/eus-lwq/leximind.git
cd leximind/data/rag_pipeline
```

---

### 4. 🛠 Build the Docker Image

```bash
docker build -t rag-pipeline .
```

---

### 5. 🏃‍♂️ Run the RAG Pipeline Container

Use the command below, replacing the repo URL as needed:

```bash
docker run -v /mnt/block:/mnt/block -e REPO_URL=https://github.com/your/repo rag-pipeline
```

✅ **The script will:**

- Clone the GitHub repo specified via `REPO_URL`
- Extract documentation files (`.md`, `.txt`, `.rst`)
- Chunk and embed them using `all-MiniLM-L6-v2`
- Save:
  - Chunk metadata to `/mnt/block/rag_data/chunks/<repo_name>_chunks.pkl`
  - FAISS vector index to `/mnt/block/rag_data/vector_index/<repo_name>_faiss.index`

---

## 📁 Example Output Paths

If the repo is `https://github.com/hwchase17/langchain`:

```
/mnt/block/rag_data/chunks/langchain_chunks.pkl
/mnt/block/rag_data/vector_index/langchain_faiss.index
```

---

## 💡 Notes

- You can re-run the container with different `REPO_URL`s to generate multiple embeddings.
- The embeddings can later be used by an LLM for retrieval-augmented inference.