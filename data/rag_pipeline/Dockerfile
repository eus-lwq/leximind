FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy files into container
COPY requirements.txt .
COPY rag_pipeline.py .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Default environment variable for repo URL
ENV REPO_URL=https://github.com/hwchase17/langchain

# Run script
CMD ["python", "rag_pipeline.py"]
