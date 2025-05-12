# Load Testing for vLLM Inference Engine

This folder contains scripts and utilities to perform load testing on the vLLM inference engine. The goal is to evaluate the performance of the vLLM server under different workloads and configurations.

## Overview

The `test_simple_load_test.py` script is designed to:
- Start the vLLM server before running the tests.
- Perform load testing by sending multiple concurrent requests to the vLLM server.
- Measure key performance metrics such as throughput, latency, and success rate.
- Validate the server's ability to handle varying workloads.

## Key Metrics

The script evaluates the following performance metrics:
1. **Throughput**: The number of requests processed per second.
2. **Average Latency**: The average time taken to process a single request.
3. **95th Percentile Latency (P95)**: The latency below which 95% of the requests are processed.
4. **Success Rate**: The percentage of successful requests.

## Contents

- **[`test_simple_load_test.py`](./test_simple_load_test.py)**: The main script for load testing the vLLM server. It includes:
  - Automatic startup and shutdown of the vLLM server.
  - Load testing with configurable parameters such as the number of requests, maximum tokens, and concurrency level.
  - Performance metric calculations and assertions to validate the server's performance.

## How to Use

1. **Prepare the Environment**:
   - Ensure the required dependencies are installed (e.g., `vLLM`, `pytest`, `numpy`, `requests`).
   - Place your model in the appropriate directory (e.g., `./merged_model`).

2. **Run the Tests**:
   - Use `pytest` to execute the load tests:
     ```bash
     pytest test_simple_load_test.py
     ```

3. **Analyze the Results**:
   - The script will output performance metrics such as throughput, average latency, P95 latency, and success rate.
   - Assertions are included to ensure the server meets predefined performance thresholds.


