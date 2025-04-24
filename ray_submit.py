import ray
import subprocess
import os
import time

# Connect to Ray
ray.init(address="ray-head:6379")

# Define a remote function that runs the training script
@ray.remote(num_gpus=1)
def run_train_script():
    # Add timestamp to log for tracking
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"[{timestamp}] Starting training job via script")
    
    # Run the bash script
    cmd = ["bash", "/llama-factory/train.sh"]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    
    # Log completion
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"[{timestamp}] Training completed")
    
    return {"status": "completed", "output": result.stdout}

# Submit the job
print("Submitting training job to Ray cluster...")
job_id = run_train_script.remote()

# Monitor the job
print(f"Submitted job with ID: {job_id}")
print("Waiting for results...")
result = ray.get(job_id)
print(f"Training completed with status: {result['status']}")