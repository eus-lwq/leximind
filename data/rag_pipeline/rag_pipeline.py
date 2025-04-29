from git import Repo
import os, shutil, pickle
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from textwrap import wrap

# --- Paths ---
CHUNKS_DIR = '/mnt/block/rag_data/chunks'
INDEX_DIR = '/mnt/block/rag_data/vector_index'
CHUNKS_METADATA_PATH = os.path.join(CHUNKS_DIR, 'chunks_metadata.pkl')
FAISS_INDEX_PATH = os.path.join(INDEX_DIR, 'faiss_index.index')

os.makedirs(CHUNKS_DIR, exist_ok=True)
os.makedirs(INDEX_DIR, exist_ok=True)

# --- 1. Clone Repo ---
def clone_repo(repo_url, clone_dir='cloned_repo'):
    if os.path.exists(clone_dir):
        shutil.rmtree(clone_dir)
    Repo.clone_from(repo_url, clone_dir)
    return clone_dir

# --- 2. Collect doc files ---
def collect_doc_files(repo_path, allowed_exts={'.md', '.txt', '.rst'}):
    doc_files = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in allowed_exts):
                doc_files.append(os.path.join(root, file))
    return doc_files

# --- 3. Read contents ---
def read_files(file_paths):
    docs = []
    for path in file_paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                docs.append((path, f.read()))
        except:
            continue
    return docs

# --- 4. Chunk content ---
def chunk_docs(docs, max_tokens=300):
    chunks = []
    for path, content in docs:
        parts = wrap(content, max_tokens * 4)
        for part in parts:
            chunks.append((path, part))
    return chunks

# --- 5. Embed & store ---
def embed_chunks(chunks, model_name='all-MiniLM-L6-v2'):
    model = SentenceTransformer(model_name)
    texts = [chunk[1] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)
    return np.array(embeddings), chunks

def store_chunks_and_index(embeddings, chunks):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    faiss.write_index(index, FAISS_INDEX_PATH)
    with open(CHUNKS_METADATA_PATH, 'wb') as f:
        pickle.dump(chunks, f)
    print(f"✅ Saved FAISS index at {FAISS_INDEX_PATH}")
    print(f"✅ Saved chunk metadata at {CHUNKS_METADATA_PATH}")

# --- Entry Point ---
if __name__ == '__main__':
    repo_url = os.getenv('REPO_URL')
    print(f"📦 Cloning repo: {repo_url}")
    repo_path = clone_repo(repo_url)
    doc_files = collect_doc_files(repo_path)
    docs = read_files(doc_files)
    chunks = chunk_docs(docs)
    embeddings, chunks = embed_chunks(chunks)
    store_chunks_and_index(embeddings, chunks)
