import mlflow
from typing import Dict, Any, Optional
import time
from datetime import datetime

class TrainingMonitor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.start_time = time.time()
        self.step = 0
        
    def on_train_start(self):
        """Called when training starts."""
        if "mlflow" in (self.config.get("report_to") or []):
            mlflow.log_params(self.config)
    
    def on_step_end(self, metrics: Dict[str, float]):
        """Called at the end of each training step."""
        self.step += 1
        if "mlflow" in (self.config.get("report_to") or []):
            # Log metrics
            mlflow.log_metrics(metrics, step=self.step)
            
            # Log training time
            elapsed_time = time.time() - self.start_time
            mlflow.log_metric("training_time_seconds", elapsed_time, step=self.step)
            
            # Log tokens per second if available
            if "tokens_per_second" in metrics:
                mlflow.log_metric("tokens_per_second", metrics["tokens_per_second"], step=self.step)
    
    def on_evaluate(self, eval_metrics: Dict[str, float]):
        """Called after evaluation."""
        if "mlflow" in (self.config.get("report_to") or []):
            # Prefix eval metrics to distinguish them from training metrics
            eval_metrics = {f"eval_{k}": v for k, v in eval_metrics.items()}
            mlflow.log_metrics(eval_metrics, step=self.step)
    
    def on_train_end(self, final_metrics: Optional[Dict[str, float]] = None):
        """Called when training ends."""
        if "mlflow" in (self.config.get("report_to") or []):
            if final_metrics:
                mlflow.log_metrics(final_metrics, step=self.step)
            
            # Log total training time
            total_time = time.time() - self.start_time
            mlflow.log_metric("total_training_time_seconds", total_time)
            
            # Log training end time
            end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            mlflow.log_param("training_end_time", end_time) 