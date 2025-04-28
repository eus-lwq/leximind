
# Step 3: Create Dockerfile with Python 3.10.12
echo "[Step 3] Creating Dockerfile for Python 3.10.12..."

mkdir -p ~/leximind
cd ~/leximind

cat << 'EOF' > Dockerfile
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

RUN apt-get update && apt-get install -y \
    software-properties-common \
    build-essential \
    wget \
    git \
    curl \
    jq \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libffi-dev \
    libncurses5-dev \
    libncursesw5-dev \
    liblzma-dev \
    uuid-dev \
    xz-utils \
    sudo \
    gnupg2 \
    && rm -rf /var/lib/apt/lists/*

RUN cd /usr/src && \
    wget https://www.python.org/ftp/python/3.10.12/Python-3.10.12.tgz && \
    tar xzf Python-3.10.12.tgz && \
    cd Python-3.10.12 && \
    ./configure --enable-optimizations && \
    make -j$(nproc) && \
    make altinstall

RUN ln -sf /usr/local/bin/python3.10 /usr/bin/python && \
    ln -sf /usr/local/bin/python3.10 /usr/bin/python3 && \
    ln -sf /usr/local/bin/pip3.10 /usr/bin/pip

RUN pip install --upgrade pip

RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

RUN pip install \
    transformers \
    datasets \
    accelerate \
    bitsandbytes \
    peft \
    scikit-learn \
    sentencepiece \
    wandb \
    trl \
    deepspeed \
    scipy \
    tqdm \
    evaluate

WORKDIR /llama-factory
CMD ["bash"]
EOF

# Step 4: Clone llama-factory if not exist
echo "[Step 4] Cloning llama-factory from GitHub (if needed)..."

if [ ! -d "$HOME/llama-factory" ]; then
  git clone https://github.com/Yuan-33/llama-factory.git ~/llama-factory
fi

# Step 5: Build the Docker image
echo "[Step 5] Building the Docker image..."

docker build -t llama-env:py310 .

# Step 6: Start the Docker container (bind mount llama-factory directory)
echo "[Step 6] Starting the Docker container..."

# Create a script inside llama-factory to auto-install correct pip packages
cat << 'EOT' > ~/llama-factory/fix_dependencies.sh
#!/bin/bash
set -e
echo "[Inside Container] Installing specific versions of required Python packages..."
pip install datasets==3.5.0
pip install peft==0.15.1
pip install trl==0.9.6
pip install matplotlib
echo "[Done] All required packages are installed."
EOT

chmod +x ~/llama-factory/fix_dependencies.sh

docker run --gpus all -it --name llama-train -v ~/llama-factory:/llama-factory llama-env:py310 bash
