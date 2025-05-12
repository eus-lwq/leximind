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
