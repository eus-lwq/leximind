#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
jsonl_processor.py

This script is used to convert a huggingface `.jsonl` dataset file into two formats:

1. Intermediate `.json` format — where each line of the original JSONL is parsed into a list of JSON objects.
   Example: `train.jsonl` ➜ `train_intermediate.json`

2. Alpaca (LLaMA fine-tuning) format — each JSON object is transformed into the format:
   {
       "instruction": <question>,
       "input": "",
       "output": <solutions>
   }
   Example: `train_intermediate.json` ➜ `train_alpaca.json`

Usage:
    python convert.py path/to/train.jsonl
"""
import json
import os
import argparse
from pathlib import Path

def convert_jsonl_to_json(input_path):
    input_path = Path(input_path)
    base_name = input_path.stem  # 'train' from 'train.jsonl'
    dir_path = input_path.parent

    intermediate_path = dir_path / f"{base_name}_intermediate.json"

    with open(input_path, "r") as f:
        data = [json.loads(line) for line in f]

    with open(intermediate_path, "w") as f:
        json.dump(data, f, indent=2)

    print("1. Converted JSONL to JSON:", intermediate_path)
    return intermediate_path

def convert_to_llama_format(intermediate_path):
    intermediate_path = Path(intermediate_path)
    base_name = intermediate_path.stem.replace("_intermediate", "")
    dir_path = intermediate_path.parent

    alpaca_path = dir_path / f"{base_name}_alpaca.json"

    with open(intermediate_path, "r") as f:
        data = json.load(f)

    converted = [{
        "instruction": item["question"],
        "input": "",
        "output": item["solutions"]
    } for item in data]

    os.makedirs(dir_path, exist_ok=True)
    with open(alpaca_path, "w") as f:
        json.dump(converted, f, indent=2)

    print("2. Converted to LLaMA/Alpaca format:", alpaca_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert JSONL to JSON and Alpaca format.")
    parser.add_argument("input_jsonl", type=str, help="Path to input JSONL file")

    args = parser.parse_args()

    intermediate = convert_jsonl_to_json(args.input_jsonl)
    convert_to_llama_format(intermediate)
