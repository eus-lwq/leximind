#!/bin/bash

#export HF_TOKEN=h1***

set -e  # Exit immediately on error

cd "$(dirname "$0")/.."  # Move to llama-factory directory

: "${HF_TOKEN:?Error: Please set HF_TOKEN environment variable}"
export HF_TOKEN

# Set MLflow environment variables
export MLFLOW_TRACKING_URI="http://mlflow:5000"
export MLFLOW_S3_ENDPOINT_URL="http://minio:9000"
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"

# Create a Python wrapper script for MLflow integration
cat > mlflow_monitor/mlflow_train_wrapper.py << 'EOF'
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mlflow_monitor.mlflow_utils import setup_mlflow, start_run, log_params, end_run
import subprocess

def get_params_from_args(args):
    params = {}
    i = 0
    while i < len(args):
        if args[i].startswith('--'):
            param_name = args[i][2:]
            if i + 1 < len(args) and not args[i + 1].startswith('--'):
                params[param_name] = args[i + 1]
                i += 2
            else:
                params[param_name] = True
                i += 1
        else:
            i += 1
    return params

def main():
    setup_mlflow()
    
    # Extract training parameters
    train_args = sys.argv[1:]
    params = get_params_from_args(train_args)
    
    # Start MLflow run
    with start_run(
        experiment_name="llama-factory-training",
        run_name=params.get('run_name', 'default-run')
    ):
        # Log all parameters
        log_params(params)
        
        # Run the actual training command
        cmd = ["python3", "src/train.py"] + train_args
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Stream and capture output
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        # Get return code
        return_code = process.poll()
        if return_code != 0:
            raise subprocess.CalledProcessError(return_code, cmd)

if __name__ == "__main__":
    main()
EOF

# Run the training through the MLflow wrapper
CUDA_VISIBLE_DEVICES=0 python3 mlflow_monitor/mlflow_train_wrapper.py \
  --stage sft \
  --model_name_or_path meta-llama/Meta-Llama-3-8B \
  --do_train \
  --do_eval \
  --dataset_dir data \
  --dataset myalpaca2 \
  --template alpaca \
  --finetuning_type lora \
  --output_dir output \
  --overwrite_cache \
  --overwrite_output_dir \
  --per_device_train_batch_size 8 \
  --per_device_eval_batch_size 8 \
  --gradient_accumulation_steps 8 \
  --num_train_epochs 1 \
  --learning_rate 1e-5 \
  --lr_scheduler_type cosine \
  --warmup_ratio 0.1 \
  --max_grad_norm 0.3 \
  --bf16 \
  --logging_steps 20 \
  --save_strategy steps \
  --save_steps 200 \
  --save_total_limit 3 \
  --max_samples 60000 \
  --val_size 0.05 \
  --logging_dir wandb_logs \
  --report_to wandb,mlflow \
  --run_name llama3-8b-lora-myalpaca2-v2 \
  --cutoff_len 512 \
  --include_tokens_per_second true \
  --plot_loss \
  --metric_for_best_model loss \
  --lora_rank 8 \
  --lora_target "q_proj,v_proj" 