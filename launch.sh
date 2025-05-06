#!/bin/bash
# Set environment variables
export HOST_IP=$(curl --silent http://169.254.169.254/latest/meta-data/public-ipv4)
git clone https://github.com/Yuan-33/llama-factory.git


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

# Start the integrated environment
echo "Starting LLama-Ray integrated environment..."
docker compose up -d --build  # Added --build flag to ensure trainer image is built
docker cp ray_submit.py llama-trainer:/llama-factory/ray_submit.py

# Show Jupyter URL
echo "Waiting for Jupyter to start..."
sleep 5
docker logs jupyter 2>&1 | grep "http://127.0.0.1:8888"
echo "Environment is ready!"
echo "- Ray dashboard: http://$HOST_IP:8265"
echo "- Grafana: http://$HOST_IP:3000"
echo "- MinIO: http://$HOST_IP:9001"
echo "- Jupyter: http://$HOST_IP:8888"
echo "- Prometheus: http://$HOST_IP:9090"
echo "- MLflow: http://$HOST_IP:5000"
echo "- To connect to llama-trainer: docker exec -it llama-trainer bash"
echo "- To run train directly with bash: docker exec -it llama-trainer bash train.sh"
echo "- To submit Ray job: docker exec -it llama-trainer python3 ray_submit.py"
echo "- To stop the environment: docker compose down"
