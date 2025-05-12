import requests
import subprocess
import time
import os

# vLLM server configuration
VLLM_SERVER_URL = "http://localhost:8000/generate"
MODEL_PATH = "/home/cc/model/whole_model"  # Path to the model
MAX_RETRIES = 10
RETRY_INTERVAL = 10  # seconds

# Test samples
samples = [
    {
        "instruction": "Where did the buffer display ?",
        "input": "@contextlib contextmanagerdef MockVimBuffers buffers current_buffer cursor_position 1 1 if current_buffer not in buffers raise RuntimeError u'Currentbuffermustbepartofthebufferslist ' with patch u'vim buffers' buffers with patch u'vim current buffer' current_buffer with patch u'vim current window cursor' cursor_position yield",
    },
    {
        "instruction": "What does the code make ?",
        "input": "def mountCgroups mounts quietRun 'cat/proc/mounts' cgdir '/sys/fs/cgroup'csdir cgdir + '/cpuset' if 'cgroup%s' % cgdir not in mounts and 'cgroups%s' % cgdir not in mounts raise Exception 'cgroupsnotmountedon' + cgdir if 'cpuset%s' % csdir not in mounts errRun 'mkdir-p' + csdir errRun 'mount-tcgroup-ocpusetcpuset' + csdir",
    },
    {
        "instruction": "What does the new denying rule match  ?",
        "input": "private boolean checkRuleMatch ( ACLRule newRule ) { List < Integer > allowRuleList = new ArrayList < > ( ) ; for ( ACLRule existingRule : getRules ( ) ) { if ( newRule . match ( existingRule ) ) { return _BOOL ; } if ( existingRule . getAction ( ) == Action . ALLOW && newRule . getAction ( ) == Action . DENY ) { if ( existingRule . match ( newRule ) ) { allowRuleList . add ( existingRule . getId ( ) ) ; } } } deny2Allow . put ( newRule . getId ( ) , allowRuleList ) ; return _BOOL ; }",
    },
    {
        "instruction": "What list in an environment ?",
        "input": "def list_states saltenv 'base' return __context__['fileclient'] list_states saltenv",
    },
]

# Inference parameters
max_new_tokens = 64
temperature = 0.6


def start_vllm_server():
    """
    Start the vLLM server as a subprocess.
    """
    print("Starting vLLM server...")
    command = [
        "python",
        "-m",
        "vllm.entrypoints.openai.api_server",
        "--model",
        MODEL_PATH,
        "--port",
        "8000",
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process


def wait_for_vllm_server():
    """
    Wait for the vLLM server to be ready.
    """
    for attempt in range(MAX_RETRIES):
        print(f"Waiting for vLLM server to be ready (attempt {attempt + 1}/{MAX_RETRIES})...")
        time.sleep(RETRY_INTERVAL)
        try:
            response = requests.get(f"{VLLM_SERVER_URL.replace('/generate', '/health')}", timeout=5)
            if response.status_code == 200:
                print("vLLM server is ready.")
                return True
        except requests.RequestException:
            print("vLLM server is not ready yet.")
    return False


def stop_vllm_server(process):
    """
    Stop the vLLM server subprocess.
    """
    print("Stopping vLLM server...")
    process.terminate()
    process.wait()


def format_prompt(sample):
    """
    Format the input prompt for vLLM.
    """
    return f"Instruction: {sample['instruction']}\nInput: {sample['input']}\nOutput:"


def send_request_to_vllm(prompts):
    """
    Send a request to the vLLM server for inference.

    Args:
        prompts (list): List of input prompts.

    Returns:
        list: List of generated outputs.
    """
    try:
        response = requests.post(
            VLLM_SERVER_URL,
            json={
                "prompt": prompts if isinstance(prompts, list) else [prompts],
                "max_tokens": max_new_tokens,
                "temperature": temperature,
                "top_p": 0.9,
                "top_k": 50,
            },
            timeout=30,
        )
        response.raise_for_status()
        return [output["text"] for output in response.json()["choices"]]
    except requests.RequestException as e:
        print(f"Error: Failed to connect to vLLM server. {e}")
        return []


def run_serial_inference(samples):
    """
    Perform serial inference on the samples and measure performance.
    """
    start_time = time.time()
    for sample in samples:
        prompt = format_prompt(sample)
        outputs = send_request_to_vllm(prompt)
        if outputs:
            print(f"{prompt}\n{outputs[0].strip()}\n{'-'*50}")

    end_time = time.time()
    latency = (end_time - start_time) / len(samples)
    print(f"Serial Inference Metrics:\n  Total Time: {end_time - start_time:.2f}s\n  Latency per Sample: {latency:.2f}s\n")


def run_batched_inference(samples, batch_size=2):
    """
    Perform batched inference on the samples and measure performance.
    """
    start_time = time.time()
    for i in range(0, len(samples), batch_size):
        batch = samples[i:i + batch_size]
        prompts = [format_prompt(sample) for sample in batch]
        outputs = send_request_to_vllm(prompts)
        for j, output in enumerate(outputs):
            print(f"{prompts[j]}\n{output.strip()}\n{'-'*50}")

    end_time = time.time()
    latency = (end_time - start_time) / len(samples)
    throughput = len(samples) / (end_time - start_time)
    print(f"Batched Inference Metrics:\n  Total Time: {end_time - start_time:.2f}s\n  Latency per Sample: {latency:.2f}s\n  Throughput: {throughput:.2f} samples/s\n")


if __name__ == "__main__":
    # Start the vLLM server
    vllm_process = start_vllm_server()

    try:
        # Wait for the server to be ready
        if not wait_for_vllm_server():
            raise RuntimeError("vLLM server failed to start.")

        # Run serial inference
        print("Running Serial Inference...")
        run_serial_inference(samples)

        # Run batched inference
        print("Running Batched Inference...")
        run_batched_inference(samples, batch_size=2)

    finally:
        # Stop the vLLM server
        stop_vllm_server(vllm_process)