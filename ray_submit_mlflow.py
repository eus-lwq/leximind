import ray
import subprocess
import os
import sys
from mlflow_monitor import setup_mlflow, start_run, log_params, log_metrics, end_run
import json
import time
from datetime import datetime

print("Starting ray_submit_mlflow.py...")

python_path = sys.executable
print(f"Using Python executable: {python_path}")

# Setup MLflow
setup_mlflow()

# Connect to the Ray cluster using the Ray client protocol
print("Initializing Ray...")
ray.init(address="ray://ray-head:10001")
print("Ray initialized.")

def parse_metrics_from_output(output: str):
    """Extract metrics from training output."""
    metrics = {}
    for line in output.split('\n'):
        if 'loss' in line.lower():
            try:
                # Try to parse lines containing metrics
                if 'train_loss' in line.lower():
                    metrics['train_loss'] = float(line.split(':')[-1].strip())
                elif 'eval_loss' in line.lower():
                    metrics['eval_loss'] = float(line.split(':')[-1].strip())
            except:
                continue
    return metrics

@ray.remote(num_gpus=1)
def train():
    print("Inside train() remote function.")
    
    # Start MLflow run
    with start_run(experiment_name="llama-ray-training", run_name=f"ray-run-{datetime.now().strftime('%Y%m%d-%H%M%S')}"):
        start_time = time.time()
        
        # Log Ray-specific parameters
        ray_params = {
            "num_gpus": 1,
            "ray_address": "ray://ray-head:10001",
            "python_path": python_path,
        }
        log_params(ray_params)
        
        print("About to run /llama-factory/train.sh with the following environment:")
        print(f"PYTHON={os.environ.get('PYTHON', python_path)}")
        print(f"Current working directory: {os.getcwd()}")
        
        try:
            # Run the training script
            result = subprocess.run(
                ["bash", "/llama-factory/train.sh"],
                capture_output=True,
                text=True,
                cwd="/llama-factory",
                env={**os.environ, "PYTHON": python_path}
            )
            print("Subprocess finished.")
            
            # Parse and log metrics
            metrics = parse_metrics_from_output(result.stdout)
            if metrics:
                log_metrics(metrics)
            
            # Log execution time
            execution_time = time.time() - start_time
            log_metrics({
                "execution_time_seconds": execution_time,
                "exit_code": result.returncode
            })
            
            # Log output
            with open("train_output.txt", "w") as f:
                f.write("STDOUT:\n")
                f.write(result.stdout)
                f.write("\nSTDERR:\n")
                f.write(result.stderr)
            
            print("STDOUT:")
            print(result.stdout)
            print("STDERR:")
            print(result.stderr)
            print(f"Return code: {result.returncode}")
            
            return result.returncode
            
        except Exception as e:
            print(f"Exception occurred: {e}")
            # Log the error
            log_params({"error": str(e)})
            return -1

print("Submitting Ray job with MLflow tracking...")
future = train.remote()
print("Job submitted! Waiting for completion...")
result = ray.get(future)
print(f"Training finished with exit code: {result}") 