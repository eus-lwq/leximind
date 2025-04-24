import ray
import subprocess
import os
import time
import sys

# Print debugging information
print("Current working directory:", os.getcwd())
print("Python version:", sys.version)
print("Ray version:", ray.__version__)

# Connect to the local Ray node you just started
try:
    print("Connecting to local Ray node...")
    # The address is localhost:6379 since Ray is running in this container
    # ray.init(address="localhost:6379")
    ray.init(address="ray-head:6379")
except Exception as e:
    print(f"Connection failed: {e}")
    sys.exit(1)

print("Successfully connected to Ray cluster!")
print(f"Available resources: {ray.available_resources()}")

# Define a remote function that runs the training script with environment variables
@ray.remote(num_gpus=1, runtime_env={
    "env_vars": {
        "HUGGINGFACE_TOKEN": "",
        "HF_TOKEN": "",
        "WANDB_API_KEY": ""
    }
})
def run_train_script():
    # Add timestamp to log for tracking
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"[{timestamp}] Starting training job via script")
    
    # Run the bash script with modified path, but this time don't use check=True
    # so we can capture the error without raising an exception
    cmd = ["bash", "-c", "/llama-factory/train_outside.sh"]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Log completion
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"[{timestamp}] Training completed with exit code: {result.returncode}")
    
    # Return both stdout and stderr to diagnose issues
    return {
        "status": "completed" if result.returncode == 0 else "failed",
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr
    }

# Submit the job
print("Submitting training job to Ray cluster...")
job_id = run_train_script.remote()

# Monitor the job
print(f"Submitted job with ID: {job_id}")
print("Waiting for results...")
result = ray.get(job_id)

print(f"Training completed with status: {result['status']}")
print(f"Exit code: {result['exit_code']}")
print("=== STDERR ===")
print(result['stderr'])
print("=== STDOUT ===")
print(result['stdout'][:500] + "..." if len(result['stdout']) > 500 else result['stdout'])