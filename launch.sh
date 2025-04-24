#!/bin/bash

# Set environment variables
export HOST_IP=$(curl --silent http://169.254.169.254/latest/meta-data/public-ipv4)

# Add wandb dependency to eric container
# Build extended llama image if it doesn't exist or if Dockerfile.llama-extended has changed
if ! docker image ls | grep -q llama-env-extended || [ "$(stat -c %Y Dockerfile.llama-extended)" -gt "$(docker inspect -f '{{.Created}}' llama-env-extended:v1 2>/dev/null | date -f - +%s 2>/dev/null || echo 0)" ]; then
    echo "Building extended llama image with additional dependencies..."
    docker build -t llama-env-extended:v1 -f Dockerfile.llama-extended .
fi

# Create dataset volume if not exists
if ! docker volume ls | grep -q codeqa; then
    echo "Creating codeqa volume..."
    docker volume create codeqa
    docker compose -f docker-compose-data.yaml up -d
fi

# Build Jupyter image if needed
if ! docker image ls | grep -q jupyter-ray; then
    echo "Building Jupyter image..."
    docker build -t jupyter-ray -f Dockerfile.jupyter-ray .
fi

# Update docker-compose file to use new image
# This uses sed to replace the image name in the docker-compose.yaml file
sed -i 's|image: ericyuanale/llama-env:llm-v1|image: llama-env-extended:v1|g' docker-compose.yaml

# Start the integrated environment
echo "Starting LLama-Ray integrated environment..."
docker compose up -d

# Show Jupyter URL
echo "Waiting for Jupyter to start..."
sleep 5
docker logs jupyter 2>&1 | grep "http://127.0.0.1:8888"

# After starting the container
echo "Copying Ray scripts to container..."
docker cp ray_submit.py llama-trainer:/root/ray_scripts/
docker cp ray_monitor.py llama-trainer:/root/ray_scripts/
docker exec llama-trainer chmod +x /root/ray_scripts/ray_submit.py
docker exec llama-trainer chmod +x /root/ray_scripts/ray_monitor.py

echo "Environment is ready!"
echo "- Ray dashboard: http://$HOST_IP:8265"
echo "- Grafana: http://$HOST_IP:3000"
echo "- MinIO: http://$HOST_IP:9001"
echo "- To connect to llama-trainer: docker exec -it llama-trainer bash"
echo "- To submit Ray job: docker exec -it llama-trainer python /root/ray_scripts/ray_submit.py"
echo "- To monitor training: docker exec -it llama-trainer python /root/ray_scripts/ray_monitor.py"
echo "- To stop the environment: docker compose down"
