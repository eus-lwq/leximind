import pytest
import numpy as np
import time
import concurrent.futures
import requests

def send_request(prompt, max_tokens, server_url="http://localhost:8000/generate"):
    """
    Send a request to the vLLM server.

    Args:
        prompt (str): The input prompt for the server.
        max_tokens (int): Maximum number of tokens to generate.
        server_url (str): URL of the vLLM server.

    Returns:
        tuple: (latency, success) where latency is the time taken for the request
               and success is a boolean indicating if the request was successful.
    """
    start_time = time.time()
    try:
        response = requests.post(
            server_url,
            json={"prompt": prompt, "max_tokens": max_tokens},
            timeout=10  # Set a timeout for the request
        )
        latency = time.time() - start_time
        if response.status_code == 200:
            return latency, True
        else:
            return latency, False
    except requests.RequestException:
        latency = time.time() - start_time
        return latency, False

def run_load_test(config):
    """
    Run a load test against the vLLM server.

    Args:
        config (dict): Configuration for the load test, including:
            - num_requests: Number of requests to send.
            - max_tokens: Maximum tokens per request.
            - server_url: URL of the vLLM server.
            - max_workers: Number of concurrent workers.

    Returns:
        dict: Metrics including throughput, avg_latency, p95_latency, and success_rate.
    """
    test_params = config["test_params"]
    num_requests = test_params["num_requests"]
    max_tokens = test_params["max_tokens"]
    server_url = test_params["server_url"]
    max_workers = test_params["max_workers"]

    latencies = []
    success_count = 0

    def task(request_id):
        prompt = f"Request {request_id}: Generate text"
        latency, success = send_request(prompt, max_tokens, server_url)
        return latency, success

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(task, i) for i in range(num_requests)]
        for future in concurrent.futures.as_completed(futures):
            latency, success = future.result()
            latencies.append(latency)
            if success:
                success_count += 1

    if latencies:
        throughput = len(latencies) / np.sum(latencies)
        avg_latency = np.mean(latencies)
        p95_latency = np.percentile(latencies, 95)
    else:
        throughput = 0
        avg_latency = 0
        p95_latency = 0

    return {
        "throughput": throughput,
        "avg_latency": avg_latency,
        "p95_latency": p95_latency,
        "success_rate": success_count / num_requests
    }

@pytest.mark.parametrize("num_requests,max_tokens,throughput_threshold", [
    (10, 32, 5),    # Small test, low threshold
    (50, 64, 3),    # Medium test, moderate threshold
    (100, 128, 2),  # Larger test, lower threshold
])
def test_run_load_test_throughput(num_requests, max_tokens, throughput_threshold):
    """
    Test the throughput of the load test function against the real vLLM server.
    """
    config = {
        "test_params": {
            "num_requests": num_requests,
            "max_tokens": max_tokens,
            "server_url": "http://localhost:8000/generate",
            "max_workers": 10
        }
    }
    results = run_load_test(config)
    assert results["throughput"] > throughput_threshold, (
        f"Throughput {results['throughput']} below threshold {throughput_threshold}"
    )
    assert results["avg_latency"] > 0
    assert results["p95_latency"] > 0
    assert results["success_rate"] > 0.0

def test_run_load_test_real_server():
    """
    Test the load test function against the real vLLM server with a small number of requests.
    """
    config = {
        "test_params": {
            "num_requests": 5,
            "max_tokens": 16,
            "server_url": "http://localhost:8000/generate",
            "max_workers": 2
        }
    }
    results = run_load_test(config)
    assert results["success_rate"] > 0.0
    assert results["throughput"] > 0