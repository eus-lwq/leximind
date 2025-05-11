import os
import time
import subprocess
import yaml
import requests
import numpy as np
from concurrent.futures import ThreadPoolExecutor

CONFIG_FILE = "batch_config.yaml"
SERVER_URL = "http://localhost:8000/v1/completions"

def load_config():
    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f)

def start_server(config, batch_size):
    cmd = [
        "python", "-m", "vllm.entrypoints.openai.api_server",
        "--model", config["model"],
        "--tensor-parallel-size", str(config["gpu_params"]["tensor_parallel_size"]),
        "--dtype", config["gpu_params"]["dtype"],
        "--max-seq-len", str(config["gpu_params"]["max_seq_len"]),
        "--block-size", str(config["gpu_params"]["block_size"]),
        "--swap-space", str(config["gpu_params"]["swap_space"]),
        "--max-num-seqs", str(batch_size),
        "--gpu-memory-utilization", "0.9"
    ]
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def send_request(prompt, max_tokens):
    payload = {
        "model": "llama-2-13b-chat",
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    try:
        start_time = time.time()
        response = requests.post(SERVER_URL, json=payload)
        latency = time.time() - start_time
        return latency, response.status_code == 200
    except Exception as e:
        return None, False

def run_load_test(config):
    test_params = config["test_params"]
    prompts = [f"Prompt {i}: Explain quantum computing basics" 
              for i in range(test_params["num_requests"])]
    
    latencies = []
    success_count = 0
    
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(send_request, prompt, test_params["max_tokens"]) 
                  for prompt in prompts]
        
        for future in futures:
            result = future.result()
            if result[0] and result[1]:
                latencies.append(result[0])
                success_count += 1
    
    return {
        "throughput": len(latencies) / np.sum(latencies),
        "avg_latency": np.mean(latencies),
        "p95_latency": np.percentile(latencies, 95),
        "success_rate": success_count / test_params["num_requests"]
    }

def tune_gpu_batch():
    config = load_config()
    results = {}
    
    for batch_size in config["batch_sizes"]:
        print(f"\nTesting batch size: {batch_size}")
        
        server_process = start_server(config, batch_size)
        time.sleep(25)  # Reduced warmup time for GPU
        
        metrics = run_load_test(config)
        results[batch_size] = metrics
        
        server_process.terminate()
        server_process.wait()
        time.sleep(10)  # GPU cooldown
    
    print("\nGPU Batch Size Tuning Results:")
    print("Batch Size | Throughput (t/s) | Avg Latency | P95 Latency | Success Rate")
    for size, metrics in results.items():
        print(f"{size:10} | {metrics['throughput']:15.2f} | {metrics['avg_latency']:10.2f}s | "
              f"{metrics['p95_latency']:9.2f}s | {metrics['success_rate']:10.2%}")

if __name__ == "__main__":
    tune_gpu_batch()