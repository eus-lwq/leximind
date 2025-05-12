python3 utils/merge.py 

pip install openai==0.28

pip install --upgrade pip                                        
pip install vllm            

export HF_HUB_OFFLINE=1

CUDA_VISIBLE_DEVICES=0 vllm serve ./merged_model \
  --host 0.0.0.0 \
  --port 8000 \
  --dtype auto \
  --api-key your_api_key_here \
  --gpu-memory-utilization 0.5 \
  --max-seq-len-to-capture 256 \
  --no-enable-prefix-caching \
  --enforce-eager \
  --swap-space 4

# new terminal -> container
sudo docker exec -it llama-train bash

curl http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_key_here" \
  -d '{
        "model": "./merged_model",
        "prompt": "What do you think of qwen model?",
        "max_tokens": 60,
        "temperature": 0.6,
        "top_k": 50,
        "top_p": 0.9,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.5
      }'

# batch inference
# /Users/ericyuan/Desktop/leximind/train/llama-factory/inference/batch_infer.py