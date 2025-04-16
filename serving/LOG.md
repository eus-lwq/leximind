## Capture Requirements

- A
- B

## Context Research (Broad)

### Key Aspects of Model Serving:

1. Deployment – The model is placed in a production environment where it can be accessed by applications.
2. Inference – The model processes input data and returns predictions.
3. Scalability – Model serving solutions ensure the system can handle multiple requests efficiently.
4. Latency & Performance – Optimized serving ensures quick responses to requests.
5. Monitoring & Logging – Tracking model performance and usage over time.

### Common Model Serving Frameworks & Tools:

- TensorFlow Serving – For serving TensorFlow models.
- TorchServe – For serving PyTorch models.
- FastAPI / Flask – Used to wrap ML models into web services.
- KServe (KFServing) – For deploying models in Kubernetes environments.
- NVIDIA Triton Inference Server – Optimized for high-performance serving.

### Selection

- TorchServe + KServe Configuration + MinIO/S3 for model storage
- 