# clone our repo
git clone https://github.com/teaching-on-testbeds/eval-offline-chi
# install docker
curl -sSL https://get.docker.com/ | sudo sh
# add permission
sudo groupadd -f docker; sudo usermod -aG docker $USER

docker run test-conda

# add nvidia container toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# check if we can see gpu in container
sudo docker run --rm --gpus all ubuntu nvidia-smi


# single gpu section
-
# multiple gpu section
sudo docker pull pytorch/pytorch:2.5.1-cuda12.4-cudnn9-devel
sudo apt update; sudo apt -y install nvtop

# pull llama2 docker
docker pull ericyuanale/llama-env:llm-v1