from git import Repo
import os
import shutil
import pickle
import re
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from urllib.parse import urlparse

# --- Get Repo Name ---
def get_repo_name(repo_url):
    parsed = urlparse(repo_url)
    return os.path.splitext(os.path.basename(parsed.path))[0]

# --- 1. Clone Repo ---
def clone_repo(repo_url, clone_dir='cloned_repo'):
    if os.path.exists(clone_dir):
        shutil.rmtree(clone_dir)
    Repo.clone_from(repo_url, clone_dir)
    return clone_dir

# --- 2. Collect guide files ---
def collect_guides_files(repo_path, guides_dir='guides', allowed_exts={'.md'}):
    """Specifically collect Markdown files from the guides directory"""
    guides_path = os.path.join(repo_path, guides_dir)
    doc_files = []
    
    if os.path.exists(guides_path):
        for root, dirs, files in os.walk(guides_path):
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
        except Exception as e:
            print(f"Error reading {path}: {e}")
            continue
    return docs

# --- 4. Chunk content ---
def chunk_markdown_docs(docs, max_chunk_size=500):
    """Chunk markdown documents based on headers and paragraphs"""
    chunks = []
    
    # Pattern to match headers
    header_pattern = re.compile(r'^#{1,6}\s+.+$', re.MULTILINE)
    
    for path, content in docs:
        # Extract filename from path for better context
        filename = os.path.basename(path)
        
        # Split content by headers
        if header_pattern.search(content):
            # If headers exist, split by headers
            sections = header_pattern.split(content)
            headers = header_pattern.findall(content)
            
            current_chunk = ""
            current_header = f"File: {filename}"
            
            # Process first section (before any header)
            if sections[0].strip():
                chunks.append((path, f"{current_header}\n\n{sections[0].strip()}"))
            
            # Process remaining sections with their headers
            for i, section in enumerate(sections[1:], 0):
                if i < len(headers):  # Make sure we have a header for this section
                    current_header = f"File: {filename} - {headers[i].strip()}"
                
                # Further split section into paragraphs if it's too large
                if len(section) > max_chunk_size:
                    paragraphs = re.split(r'\n\s*\n', section)
                    for j, para in enumerate(paragraphs):
                        if para.strip():
                            para_header = f"{current_header} [Part {j+1}/{len(paragraphs)}]"
                            chunks.append((path, f"{para_header}\n\n{para.strip()}"))
                else:
                    if section.strip():
                        chunks.append((path, f"{current_header}\n\n{section.strip()}"))
        else:
            # If no headers, chunk by paragraphs
            paragraphs = re.split(r'\n\s*\n', content)
            if len(paragraphs) > 1:
                for i, para in enumerate(paragraphs):
                    if para.strip():
                        para_header = f"File: {filename} [Paragraph {i+1}/{len(paragraphs)}]"
                        chunks.append((path, f"{para_header}\n\n{para.strip()}"))
            else:
                chunks.append((path, f"File: {filename}\n\n{content.strip()}"))
    
    return chunks

# --- 5. Embed & store ---
def embed_chunks(chunks, model_name='all-MiniLM-L6-v2'):
    print(f"🔄 Embedding {len(chunks)} chunks with model {model_name}")
    model = SentenceTransformer(model_name)
    texts = [chunk[1] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)
    return np.array(embeddings), chunks

def store_chunks_and_index(embeddings, chunks, repo_name):
    chunks_dir = '/mnt/block/rag_data/chunks'
    index_dir = '/mnt/block/rag_data/vector_index'
    os.makedirs(chunks_dir, exist_ok=True)
    os.makedirs(index_dir, exist_ok=True)
    
    chunk_path = os.path.join(chunks_dir, f'{repo_name}_guides_chunks.pkl')
    index_path = os.path.join(index_dir, f'{repo_name}_guides_faiss.index')
    
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    faiss.write_index(index, index_path)
    
    with open(chunk_path, 'wb') as f:
        pickle.dump(chunks, f)
    
    print(f"✅ Saved FAISS index at {index_path}")
    print(f"✅ Saved chunk metadata at {chunk_path}")
    print(f"✅ Total chunks: {len(chunks)}")
    return chunk_path, index_path

# --- Process files and log metadata ---
def log_chunk_metadata(chunks):
    # Create a summary of the chunks for reference
    file_counts = {}
    for path, _ in chunks:
        filename = os.path.basename(path)
        if filename in file_counts:
            file_counts[filename] += 1
        else:
            file_counts[filename] = 1
    
    print(f"\n📊 Chunk distribution by file:")
    for filename, count in file_counts.items():
        print(f"  - {filename}: {count} chunks")

# --- Entry Point ---
if __name__ == '__main__':
    # Set the repository URL directly to the Gradio repository
    repo_url = "https://github.com/gradio-app/gradio.git"
    repo_name = get_repo_name(repo_url)
    
    print(f"📦 Cloning repo: {repo_url}")
    repo_path = clone_repo(repo_url)
    
    print(f"🔍 Searching for Markdown files in guides directory")
    doc_files = collect_guides_files(repo_path)
    print(f"📄 Found {len(doc_files)} markdown files in guides directory")
    
    print(f"📖 Reading file contents")
    docs = read_files(doc_files)
    print(f"📄 Successfully read {len(docs)} files")
    
    print(f"✂️ Chunking documents")
    chunks = chunk_markdown_docs(docs)
    print(f"🧩 Created {len(chunks)} chunks")
    
    # Log chunk distribution
    log_chunk_metadata(chunks)
    
    # Embed and store
    embeddings, chunks = embed_chunks(chunks)
    chunk_path, index_path = store_chunks_and_index(embeddings, chunks, repo_name)
    
    print(f"\n✅ RAG pipeline complete!")
    print(f"📚 Your chunks are stored at: {chunk_path}")
    print(f"🔍 Your FAISS index is at: {index_path}")