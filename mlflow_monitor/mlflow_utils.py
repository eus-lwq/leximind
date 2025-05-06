import os
import mlflow
from typing import Dict, Any, Optional

def setup_mlflow():
    """Setup MLflow tracking."""
    mlflow.set_tracking_uri("http://mlflow:5000")
    os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://minio:9000"

def start_run(experiment_name: str, run_name: Optional[str] = None, tags: Optional[Dict[str, Any]] = None):
    """Start a new MLflow run."""
    mlflow.set_experiment(experiment_name)
    return mlflow.start_run(run_name=run_name, tags=tags)

def log_params(params: Dict[str, Any]):
    """Log parameters to MLflow."""
    mlflow.log_params(params)

def log_metrics(metrics: Dict[str, float], step: Optional[int] = None):
    """Log metrics to MLflow."""
    mlflow.log_metrics(metrics, step=step)

def log_model(model, artifact_path: str):
    """Log model to MLflow."""
    mlflow.pytorch.log_model(model, artifact_path)

def end_run():
    """End the current MLflow run."""
    mlflow.end_run() 