#!/bin/bash

#export HF_TOKEN=h1***
cd /llama-factory
CUDA_VISIBLE_DEVICES=0 python3 /llama-factory/src/train.py \
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
  --report_to wandb \
  --run_name llama3-8b-lora-myalpaca2-v2 \
  --cutoff_len 512 \
  --include_tokens_per_second true \
  --plot_loss \
  --metric_for_best_model loss 