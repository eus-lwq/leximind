#!/bin/bash
# Install required dependencies for all scripts

# Colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Installing dependencies for all scripts...${NC}"

# Create requirements.txt for the Dockerfile.sync if it doesn't exist
if [ ! -f "requirements.txt" ]; then
    echo -e "${BLUE}Creating requirements.txt for Label Studio integration...${NC}"
    cat > requirements.txt << EOF
requests==2.31.0
boto3==1.29.0
label-studio-sdk==0.0.30
EOF
fi

# Install Python dependencies for the Gradio app
echo -e "${BLUE}Installing Python dependencies for the Gradio app...${NC}"
pip install openai gradio boto3 requests

echo -e "${GREEN}Dependencies installed successfully!${NC}"