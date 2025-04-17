## Environment Setup 
1.
sudo apt update
sudo apt install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

2.
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

3.
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

4.
sudo usermod -aG docker $USER
newgrp docker

5.
docker pull ericyuanale/llama-env:llm-v1

6.
sudo rm /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list > /dev/null <<EOF
deb https://nvidia.github.io/libnvidia-container/stable/ubuntu22.04/amd64 /
EOF
curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | sudo apt-key add -
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

7.
scp -r -i ~/.ssh/leximind ~/Desktop/llama-factory cc@192.5.87.227:~/llama-factory
docker ps
docker cp ~/llama-factory <container_id>:/train/

8.
# c++
apt-get update
apt-get install -y build-essential 





(7.
docker run -it --gpus all -p 8888:8888 -p 8000:8000 ericyuanale/llama-env:llm-v1 bash

7.
jupyter lab --ip=0.0.0.0 --port=8888 --allow-root --no-browser)




