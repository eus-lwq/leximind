#!/bin/bash
# Source tokens from .env file
if [ -f "/llama-factory/.env" ]; then
  export \$(grep -v "^#" /llama-factory/.env | xargs)
  echo "Loaded Hugging Face and Weights & Biases tokens"
fi