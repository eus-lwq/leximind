#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Ensure W&B API key is provided
: "${WANDB_API_KEY:?Error: Please set WANDB_API_KEY environment variable}"
export WANDB_API_KEY


# Step 0: Pre-clean broken NVIDIA repo
if [ -f /etc/apt/sources.list.d/nvidia-container-toolkit.list ]; then
    echo "[Step 0] Cleaning broken NVIDIA container toolkit source..."
    sudo rm -f /etc/apt/sources.list.d/nvidia-container-toolkit.list
fi

# Step 1: Install Docker and NVIDIA container toolkit
echo "[Step 1] Installing Docker and NVIDIA container toolkit..."
curl -sSL https://get.docker.com/ | sudo sh
sudo groupadd -f docker
sudo usermod -aG docker $USER

# Reload group without reboot
# Just print a message for user
echo "[Info] Docker installed. Please re-login or run 'newgrp docker' manually if needed."
sleep 3

# Check Docker version
docker --version

# Step 2: Fix Nvidia repo if needed, then install NVIDIA Container Toolkit
echo "[Step 2] Setting up NVIDIA Container Toolkit..."

# Clean broken nvidia-container-toolkit.list if exists
if [ -f /etc/apt/sources.list.d/nvidia-container-toolkit.list ]; then
    echo "[Warning] Cleaning broken NVIDIA container toolkit source..."
    sudo rm -f /etc/apt/sources.list.d/nvidia-container-toolkit.list
fi

distribution=$(. /etc/os-release; echo $ID$VERSION_ID)

curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey \
    | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
    | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
    | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list > /dev/null


# Fix Docker cgroup driver issue
echo "[Step 2.5] Configuring Docker cgroup driver..."

sudo apt-get install -y jq  # Make sure jq exists

if [ ! -f /etc/docker/daemon.json ]; then
    echo '{}' | sudo tee /etc/docker/daemon.json > /dev/null
fi

sudo jq 'if has("exec-opts") then . else . + {"exec-opts": ["native.cgroupdriver=cgroupfs"]} end' /etc/docker/daemon.json \
    | sudo tee /etc/docker/daemon.json.tmp > /dev/null
sudo mv /etc/docker/daemon.json.tmp /etc/docker/daemon.json

sudo systemctl restart docker

