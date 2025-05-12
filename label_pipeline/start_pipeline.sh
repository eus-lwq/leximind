#!/bin/bash
# Script to start the entire pipeline and display dashboard links

# Colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the host's public IP address using multiple methods
echo -e "${YELLOW}Attempting to determine public IP address...${NC}"

# Try AWS metadata service
HOST_IP=$(curl --silent --max-time 3 http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null)

# If AWS didn't work, try GCP
if [ -z "$HOST_IP" ]; then
    HOST_IP=$(curl --silent --max-time 3 -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip 2>/dev/null)
fi

# If GCP didn't work, try Azure
if [ -z "$HOST_IP" ]; then
    HOST_IP=$(curl --silent --max-time 3 -H Metadata:true "http://169.254.169.254/metadata/instance/network/interface/0/ipv4/ipAddress/0/publicIpAddress?api-version=2021-02-01&format=text" 2>/dev/null)
fi

# If cloud-specific methods failed, try generic services
if [ -z "$HOST_IP" ]; then
    HOST_IP=$(curl --silent --max-time 3 https://ipinfo.io/ip 2>/dev/null)
fi

if [ -z "$HOST_IP" ]; then
    HOST_IP=$(curl --silent --max-time 3 https://api.ipify.org 2>/dev/null)
fi

if [ -z "$HOST_IP" ]; then
    HOST_IP=$(curl --silent --max-time 3 http://checkip.amazonaws.com 2>/dev/null)
fi

# If all else fails, fall back to private IP
if [ -z "$HOST_IP" ]; then
    HOST_IP=$(hostname -I | awk '{print $1}')
    echo -e "${YELLOW}Could not determine public IP. Using private IP instead: $HOST_IP${NC}"
    echo -e "${YELLOW}Note: This IP may only be accessible within your network.${NC}"
else
    echo -e "${GREEN}Found public IP: $HOST_IP${NC}"
fi

echo -e "${GREEN}Stopping any existing containers...${NC}"
docker compose down

echo -e "${GREEN}Creating network if it doesn't exist...${NC}"
docker network create production_net 2>/dev/null || true

echo -e "${GREEN}Starting Docker Compose Pipeline...${NC}"
# Start Docker Compose in detached mode
docker compose up -d

# Check if containers are running
echo -e "${YELLOW}Checking containers status...${NC}"
sleep 10

# Check if Label Studio is running
if [ ! "$(docker ps -q -f name=label-studio)" ]; then
    echo -e "${RED}Label Studio container is not running! Checking logs...${NC}"
    docker compose logs label-studio
    echo -e "${YELLOW}Trying to restart Label Studio...${NC}"
    docker compose up -d label-studio
    sleep 20
fi

# Check if MinIO is running
if [ ! "$(docker ps -q -f name=minio)" ]; then
    echo -e "${RED}MinIO container is not running! Checking logs...${NC}"
    docker compose logs minio
    echo -e "${YELLOW}Trying to restart MinIO...${NC}"
    docker compose up -d minio
    sleep 20
fi

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to initialize...${NC}"
sleep 30

# Get the Label Studio project ID
echo -e "${BLUE}Getting Label Studio project ID...${NC}"
PROJECT_ID=$(docker exec -i label-studio curl -s -H "Authorization: Token ab9927067c51ff279d340d7321e4890dc2841c4a" http://localhost:8080/api/projects | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}Label Studio project ID not found. You'll need to set it manually after creating a project.${NC}"
    PROJECT_ID_ARG=""
else
    echo -e "${GREEN}Found Label Studio project ID: $PROJECT_ID${NC}"
    PROJECT_ID_ARG="--label-studio-project-id $PROJECT_ID"
fi

# Display dashboard URLs with the host's IP
echo -e "\n${GREEN}=======================================================${NC}"
echo -e "${GREEN}🚀 DASHBOARD LINKS:${NC}"
echo -e "${BLUE}🏷️ Label Studio:${NC} http://$HOST_IP:8090"
echo -e "${BLUE}🗄️ MinIO Console:${NC} http://$HOST_IP:9001"
echo -e "${BLUE}    Username: your-access-key${NC}"
echo -e "${BLUE}    Password: your-secret-key${NC}"
echo -e "${BLUE}📈 Prometheus:${NC} http://$HOST_IP:9090"
echo -e "${BLUE}📓 Jupyter Notebook:${NC} http://$HOST_IP:8888"
echo -e "${GREEN}=======================================================${NC}\n"

# Show running containers
echo -e "${GREEN}Running containers:${NC}"
docker ps

# Display how to run the Gradio chatbot
echo -e "\n${GREEN}To start the Gradio chatbot with storage integration, run:${NC}"
echo -e "${YELLOW}python gradio_chatbot_with_storage.py -m <your-model-name> --model-url http://llmendpoint:8080/v1 --minio-url http://$HOST_IP:9000 --label-studio-url http://$HOST_IP:8090 $PROJECT_ID_ARG --host \"0.0.0.0\"${NC}"
echo -e "${GREEN}Replace <your-model-name> with your actual model name.${NC}"

echo -e "\n${GREEN}Pipeline is ready!${NC}"