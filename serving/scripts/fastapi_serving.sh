#!/bin/bash

# Exit on error
set -e

echo "🛠️ Checking Miniconda installation..."
if [ -x "$HOME/miniconda/bin/conda" ]; then
    echo "✅ Miniconda is already installed."
else
    echo "🔽 Installing Miniconda..."
    MINICONDA=Miniconda3-latest-Linux-x86_64.sh
    wget https://repo.anaconda.com/miniconda/$MINICONDA -O ~/miniconda.sh
    bash ~/miniconda.sh -b -p $HOME/miniconda
    eval "$($HOME/miniconda/bin/conda shell.bash hook)"
    conda init
    source ~/.bashrc
    echo "✅ Miniconda installed and initialized."
fi

# Ensure conda is in PATH for this script
eval "$($HOME/miniconda/bin/conda shell.bash hook)"

# Create and activate new conda env if it doesn't exist
echo "📦 Setting up conda environment for FastAPI..."
if conda info --envs | grep -q '^fastapi'; then
  echo "✅ Conda environment 'fastapi' already exists. Activating it..."
else
  echo "⏳ Conda environment 'fastapi' not found. Creating..."
  conda create -n fastapi python=3.12 -y
fi
conda activate fastapi
echo "✅ Conda environment ready and activated."

echo $MODEL_VER
# Install FastAPI and dependencies
echo "📚 Installing FastAPI and dependencies..."
pip install -r /home/cc/scripts/requirements.txt -q
echo "✅ FastAPI and dependencies installed."

echo "🚀 Serving with FastAPI..."
tmux new-session -d -s fastapi-session "cd /home/cc/scripts && uvicorn app:app --reload --port 8000 --host 0.0.0.0"
tmux ls

