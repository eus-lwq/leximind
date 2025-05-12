import ray
import time
import subprocess
import json
import os
from ray.util.metrics import Counter, Gauge

# Connect to Ray cluster
ray.init(address="ray-head:6379")

# Define metrics
gpu_util_gauge = Gauge("training_gpu_utilization", description="GPU utilization %")
gpu_mem_gauge = Gauge("training_gpu_memory", description="GPU memory utilization MB")
train_loss_gauge = Gauge("training_loss", description="Training loss value")
step_counter = Counter("training_steps", description="Training steps completed")

def monitor_training_metrics():
    """Periodically collect metrics and report to Ray's metrics system."""
    while True:
        try:
            # Get GPU metrics
            gpu_info = subprocess.run(
                ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used", "--format=csv,noheader,nounits"],
                capture_output=True, text=True, check=True
            )
            
            if gpu_info.stdout.strip():
                util, mem = gpu_info.stdout.strip().split(",")
                gpu_util_gauge.set(float(util))
                gpu_mem_gauge.set(float(mem))
            
            # Check for training logs
            log_path = "/llama-factory/wandb_logs/latest-run/logs.json"
            alt_log_path = "/llama-factory/output/trainer_log.json"
            
            for path in [log_path, alt_log_path]:
                if os.path.exists(path):
                    try:
                        # Get the last line of the log file
                        last_line = subprocess.run(
                            ["tail", "-n", "1", path],
                            capture_output=True, text=True, check=True
                        ).stdout.strip()
                        
                        # Parse the JSON log
                        if last_line:
                            log_data = json.loads(last_line)
                            if "loss" in log_data:
                                train_loss_gauge.set(log_data["loss"])
                            if "step" in log_data:
                                step_counter.inc()
                    except (json.JSONDecodeError, subprocess.SubprocessError) as e:
                        print(f"Error parsing log: {e}")
        
        except Exception as e:
            print(f"Error collecting metrics: {e}")
            
        time.sleep(5)  # Collect metrics every 5 seconds

if __name__ == "__main__":
    print("Starting metrics monitoring...")
    monitor_training_metrics()