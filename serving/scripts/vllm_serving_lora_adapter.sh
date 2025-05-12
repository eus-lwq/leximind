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
echo "📦 Setting up conda environment for vLLM..."
if conda info --envs | grep -q '^vllm'; then
  echo "✅ Conda environment 'vllm' already exists. Activating it..."
else
  echo "⏳ Conda environment 'vllm' not found. Creating..."
  conda create -n vllm python=3.12 -y
fi
conda activate vllm
echo "✅ Conda environment ready and activated."

# Install vLLM and dependencies
echo "📚 Installing vLLM and dependencies..."
pip install vllm gradio -q
pip install git+https://github.com/ChameleonCloud/python-blazarclient.git@chameleoncloud/xena -q
pip install python-openstackclient -q
echo "✅ vLLM and dependencies installed."

# Download models
echo "📥 Downloading model..."
# mkdir -p /home/cc/model
# python3 download_model.py

# Load OpenStack credentials and ensure they are exported
echo "🔑 Loading OpenStack credentials..."
set -a  # automatically export all variables
source /home/cc/scripts/app-cred-uc-openrc.sh
set +a  # stop automatically exporting

echo $LORA_ADAPTER
openstack object list leximind_project6 --prefix $LORA_ADAPTER -f value -c Name | while read object; do
  if [[ "$object" != */ ]]; then
    echo "Saving $object..."
    if ! openstack object save leximind_project6 "$object"; then
      echo "Failed to save $object" >&2
    fi
  fi
done

# Serving the model using vLLM
echo "🚀 Serving the model using vLLM..."
tmux new-session -d -s vllm-session "vllm serve \$MODEL_NAME --dtype=half --enable-lora --lora-modules leximind=\$HOME/\$LORA_ADAPTER"

# Serving the simple chatui with Gradio
echo "🚀 Serving the simple chatui with Gradio..."
tmux new-session -d -s chatui-session "python scripts/gradio-chatbot.py -m leximind --model-url http://localhost:8000/v1 --port 8001"
tmux ls
