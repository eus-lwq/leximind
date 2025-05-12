#!/bin/bash
# Script to start the pipeline with proper network handling

# Colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the host's public IP address
HOST_IP=$(curl --silent https://ipinfo.io/ip)
if [ -z "$HOST_IP" ]; then
    HOST_IP=$(hostname -I | awk '{print $1}')
fi
echo -e "${GREEN}Using host IP: $HOST_IP${NC}"

# Clean up existing resources
echo -e "${YELLOW}Cleaning up existing resources...${NC}"
docker-compose down
docker network rm production_net 2>/dev/null || true
echo -e "${GREEN}Done.${NC}"

# Create the network manually
echo -e "${YELLOW}Creating network...${NC}"
docker network create production_net
echo -e "${GREEN}Network created.${NC}"

# Start containers one by one for better control
echo -e "${YELLOW}Starting PostgreSQL...${NC}"
docker-compose up -d app-db
echo -e "${GREEN}Waiting for PostgreSQL to initialize...${NC}"
sleep 10

echo -e "${YELLOW}Starting Label Studio...${NC}"
docker-compose up -d label-studio
echo -e "${GREEN}Waiting for Label Studio to initialize...${NC}"
sleep 10

echo -e "${YELLOW}Starting MinIO...${NC}"
docker-compose up -d minio
echo -e "${GREEN}Waiting for MinIO to initialize...${NC}"
sleep 10

echo -e "${YELLOW}Starting remaining services...${NC}"
docker-compose up -d
sleep 10

# Check if containers are running
echo -e "${YELLOW}Checking container status...${NC}"
LABEL_STUDIO_RUNNING=$(docker ps -q -f name=label-studio)
MINIO_RUNNING=$(docker ps -q -f name=minio)

if [ -z "$LABEL_STUDIO_RUNNING" ]; then
    echo -e "${RED}Label Studio is not running! Checking logs...${NC}"
    docker-compose logs label-studio
else
    echo -e "${GREEN}Label Studio is running.${NC}"
fi

if [ -z "$MINIO_RUNNING" ]; then
    echo -e "${RED}MinIO is not running! Checking logs...${NC}"
    docker-compose logs minio
else
    echo -e "${GREEN}MinIO is running.${NC}"
fi

# Get project ID only if Label Studio is running
if [ -n "$LABEL_STUDIO_RUNNING" ]; then
    echo -e "${YELLOW}Getting Label Studio project ID...${NC}"
    # Wait a bit longer for Label Studio to fully initialize
    sleep 20
    PROJECT_ID=$(docker exec -i label-studio curl -s -H "Authorization: Token ab9927067c51ff279d340d7321e4890dc2841c4a" http://localhost:8080/api/projects | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${YELLOW}No project found. You'll need to create one and get the ID manually.${NC}"
        PROJECT_ID_ARG=""
    else
        echo -e "${GREEN}Found Label Studio project ID: $PROJECT_ID${NC}"
        PROJECT_ID_ARG="--label-studio-project-id $PROJECT_ID"
    fi
else
    PROJECT_ID_ARG=""
fi

# Display running containers
echo -e "${BLUE}Running containers:${NC}"
docker ps

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

# Display how to run the Gradio chatbot
echo -e "${GREEN}To start the Gradio chatbot with storage integration, run:${NC}"
echo -e "${YELLOW}python gradio_chatbot_with_storage.py -m <your-model-name> --model-url http://llmendpoint:8080/v1 --minio-url http://$HOST_IP:9000 --label-studio-url http://$HOST_IP:8090 $PROJECT_ID_ARG --host \"0.0.0.0\"${NC}"
echo -e "${GREEN}Replace <your-model-name> with your actual model name.${NC}"

echo -e "\n${GREEN}Pipeline setup complete!${NC}"