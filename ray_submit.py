import ray
import subprocess
import os
import sys

print("Starting ray_submit.py...")

python_path = sys.executable
print(f"Using Python executable: {python_path}")

# Connect to the Ray cluster using the Ray client protocol
print("Initializing Ray...")
ray.init(address="ray://ray-head:10001")
print("Ray initialized.")

@ray.remote(num_gpus=1)
def train():
    print("Inside train() remote function.")
    print("About to run /llama-factory/train.sh with the following environment:")
    print(f"PYTHON={os.environ.get('PYTHON', python_path)}")
    print(f"Current working directory: {os.getcwd()}")
    try:
        result = subprocess.run(
            ["bash", "/llama-factory/train.sh"],
            capture_output=True,
            text=True,
            cwd="/llama-factory",
            env={**os.environ, "PYTHON": python_path}
        )
        print("Subprocess finished.")
        print("STDOUT:")
        print(result.stdout)
        print("STDERR:")
        print(result.stderr)
        print(f"Return code: {result.returncode}")
        return result.returncode
    except Exception as e:
        print(f"Exception occurred: {e}")
        return -1

print("Submitting Ray job...")
future = train.remote()
print("Job submitted! Waiting for completion...")
result = ray.get(future)
print(f"Training finished with exit code: {result}")