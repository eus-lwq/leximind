# Choosing the Right Inference Engine

This section provides a comprehensive walkthrough of comparing different inference engines based on their performance. The goal is to help you make an informed decision about which inference engine best suits your use case.

## Overview

Inference engines play a critical role in deploying machine learning models efficiently. This folder contains scripts and benchmarks to evaluate and compare the performance of various inference engines, such as:

- **Transformers-based inference**: Using Hugging Face's `transformers` library for model inference.
- **vLLM-based inference**: Leveraging vLLM for optimized and batched inference.

## Key Metrics for Comparison

The comparison focuses on the following performance metrics:

1. **Latency**: The time taken to process a single request.
2. **Throughput**: The number of requests processed per second.
3. **Scalability**: The ability to handle batched requests efficiently.
4. **Resource Utilization**: GPU/CPU memory usage and computational efficiency.

## Contents

- **[`infer_with_transformers.py`](./infer_with_transformers.py)**: Script for running inference using the Hugging Face `transformers` library. It supports both serial and batched inference and provides performance metrics.
- **[`infer_with_vllm.py`](./infer_with_vllm.py)**: Script for running inference using the vLLM engine. It includes server startup, serial and batched inference, and performance benchmarks.
- **[`convert_sample_to_batch_input.py`](./convert_sample_to_batch_input.py)**: Utility script to convert input data into a format suitable for batch inference.

## How to Use

1. **Prepare the Environment**:
   - Ensure the required dependencies are installed (e.g., `transformers`, `torch`, `vLLM`, `requests`).
   - Place your model in the appropriate directory (e.g., `./merged_model`).

2. **Run Benchmarks**:
   - Use [`infer_with_transformers.py`](./infer_with_transformers.py) to evaluate the performance of the `transformers` library.
   - Use [`infer_with_vllm.py`](./infer_with_vllm.py) to evaluate the performance of the vLLM engine.

3. **Analyze Results**:
   - Compare the latency, throughput, and resource utilization metrics from both scripts.
   - Use the results to determine the best inference engine for your specific workload.

## Conclusion

This section provides the tools and scripts necessary to evaluate and compare inference engines. By analyzing the performance metrics, you can make an informed decision about which engine to use for deploying your machine learning models.