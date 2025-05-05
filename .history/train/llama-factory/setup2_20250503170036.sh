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

# expose W&B token in container env
ENV WANDB_API_KEY=${WANDB_API_KEY}

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

sudo apt update && sudo apt install git-lfs -y
git lfs install

if [ ! -d "$HOME/llama-factory" ]; then
  git clone https://github.com/Yuan-33/llama-factory.git ~/llama-factory
fi

cd ~/llama-factory
# Initialize Git LFS and fetch large checkpoint files
git pull origin main
git lfs pull

# Step 5: Build the Docker image
echo "[Step 5] Building the Docker image..."

cd ~/leximind 
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

docker rm -f llama-train || true

docker run --gpus all -it --name llama-train \
  -e WANDB_API_KEY=$WANDB_API_KEY \
  -v ~/llama-factory:/llama-factory \
  llama-env:py310 \
  bash

# Manual step: After entering container, run
#cd /llama-factory
# bash train.sh

[chi_tacc]
type = swift
user_id = YOUR_USER_ID
application_credential_id = 17b2836ab77a4753aa7c285e00b36f72
application_credential_secret = D-P_vsM8RbzlSd5Ti2yBSvei3nBYW9DjGC4a-ZjeCG96y23Zrs7e8lMD_EBNdnieBmq0EDbUzWQMjKhXuRx_OA
auth = https://chi.tacc.chameleoncloud.org:5000/v3
region = CHI@TACC