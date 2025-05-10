#!/bin/bash
# Script to run the Gradio app with the right parameters

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

# Default values
MODEL_NAME="your-model-name"
MODEL_URL="http://localhost:8000/v1"
LABEL_STUDIO_PROJECT_ID=""

# Check if project ID argument is provided
if [ "$1" ]; then
    LABEL_STUDIO_PROJECT_ID="--label-studio-project-id $1"
    echo -e "${GREEN}Using Label Studio project ID: $1${NC}"
else
    echo -e "${YELLOW}No Label Studio project ID provided. Will not import directly to Label Studio.${NC}"
fi

# Run the Gradio app
echo -e "${GREEN}Starting Gradio chatbot with storage integration...${NC}"
echo -e "${BLUE}Press Ctrl+C to stop${NC}"

python gradio_chatbot_with_storage.py \
    -m "$MODEL_NAME" \
    --model-url "$MODEL_URL" \
    --minio-url "http://$HOST_IP:9000" \
    --minio-user "your-access-key" \
    --minio-password "your-secret-key" \
    --label-studio-url "http://$HOST_IP:8090" \
    $LABEL_STUDIO_PROJECT_ID \
    --host "0.0.0.0"