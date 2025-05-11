#!/bin/bash

#export HF_TOKEN=h1***

bash "$(dirname "$0")/fix_dependencies.sh"

echo "[INFO] Starting MLflow server in background..."
mlflow server --host 0.0.0.0 --port 5000 \
  --backend-store-uri ./mlruns \
  --default-artifact-root ./mlruns > mlflow.log 2>&1 &

# waiting for mlflow
sleep 3
echo "[INFO] MLflow server launched at http://<your-host>:5000"

for i in {1..10}; do
  if curl -s http://localhost:5000 > /dev/null; then
    echo "[INFO] MLflow server is up."
    break
  else
    echo "[WAITING] MLflow not ready yet... (${i}/10)"
    sleep 2
  fi
done

# if not available after retries, exit
if ! curl -s http://localhost:5000 > /dev/null; then
  echo "[ERROR] MLflow server failed to start."
  cat mlflow.log
  exit 1
fi

export MLFLOW_TRACKING_URI=http://localhost:5000
export MLFLOW_EXPERIMENT_NAME=llama3-instruct-exp


set -e  # Exit immediately on error


: "${HF_TOKEN:?Error: Please set HF_TOKEN environment variable}"
export HF_TOKEN

CUDA_VISIBLE_DEVICES=0 python3 src/train.py \
  --stage sft \
  --model_name_or_path meta-llama/Meta-Llama-3-8B-Instruct \
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
  --num_train_epochs 1.5 \
  --learning_rate 5e-5 \
  --lr_scheduler_type linear \
  --warmup_ratio 0.03 \
  --max_grad_norm 0.3 \
  --bf16 \
  --logging_steps 20 \
  --save_strategy steps \
  --save_steps 200 \
  --save_total_limit 3 \
  --max_samples 60000 \
  --val_size 0.05 \
  --logging_dir mlflow_logs \
  --report_to mlflow \
  --run_name llama3-8b-lora-myalpaca2-v2 \
  --cutoff_len 512 \
  --include_tokens_per_second true \
  --plot_loss \
  --metric_for_best_model loss \
  --lora_rank 8 \
  --lora_target "q_proj,k_proj,v_proj,o_projj"


