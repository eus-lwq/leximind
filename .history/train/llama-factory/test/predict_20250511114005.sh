#!/bin/bash
set -e

export HF_TOKEN=your_huggingface_token_if_needed

CUDA_VISIBLE_DEVICES=0 python3 src/train.py \
  --stage sft \
  --model_name_or_path output\predict
  --do_predict \
  --predict_file data/myalpaca2/test.json \
  --template alpaca \
  --finetuning_type lora \
  --output_dir output/test_predictions \
  --per_device_eval_batch_size 8 \
  --cutoff_len 512 \
  --predict_with_generate \
  --max_samples 5000 \
  --report_to none \
  --plot_loss 