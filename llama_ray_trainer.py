# llama_ray_trainer.py
import os
import ray
from ray import train
from ray.train import ScalingConfig
import json

# Connect to Ray
ray.init(address="ray://ray-head:6379")

# Load your dataset
with open("/mnt/codeqa/train.json", "r") as f:
    train_data = json.load(f)
    
with open("/mnt/codeqa/test.json", "r") as f:
    test_data = json.load(f)

# Configure Ray Train
scaling_config = ScalingConfig(
    num_workers=1,  # Number of GPU workers
    use_gpu=True,
    resources_per_worker={"GPU": 1, "CPU": 16}
)

# Define the training function
def train_func(config):
    import os
    import subprocess
    
    # Create LLama-Factory command
    cmd = [
        "python", "/llama-factory/src/train_bash.py",
        "--stage", "sft",
        "--do_train",
        "--model_name_or_path", config["model_path"],
        "--dataset", config["dataset_path"],
        "--output_dir", config["output_dir"],
        "--overwrite_cache",
        "--per_device_train_batch_size", str(config["batch_size"]),
        "--gradient_accumulation_steps", str(config["gradient_accumulation"]),
        "--lr_scheduler_type", "cosine",
        "--logging_steps", "1",
        "--save_steps", "1000",
        "--learning_rate", str(config["learning_rate"]),
        "--num_train_epochs", str(config["epochs"]),
        "--logging_strategy", "steps",
        "--save_strategy", "steps",
        "--save_total_limit", "3",
        "--fp16"
    ]
    
    # Execute LLama-Factory training
    subprocess.run(cmd, check=True)

# Start Ray training
trainer = train.Trainer(
    train_func,
    scaling_config=scaling_config,
    run_config=train.RunConfig(
        storage_path="s3://ray/checkpoints",
        name="llama-factory-training"
    )
)

# Launch training with hyperparameters
result = trainer.fit({
    "model_path": "meta-llama/Llama-2-7b-hf",
    "dataset_path": "/mnt/codeqa",
    "output_dir": "/llama-factory/outputs/sft_llama2",
    "batch_size": 4,
    "gradient_accumulation": 4,
    "learning_rate": 2e-5,
    "epochs": 1
})