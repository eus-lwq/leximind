#!/bin/bash
set -e

# 确保你已经训练好模型并保存到了 output/ 目录
# 确保测试集文件存在，例如：data/myalpaca2/test.json

# 环境变量（可选）
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