from setuptools import setup, find_packages

setup(
    name="mlflow_monitor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "mlflow>=2.11.1",
        "torch",
        "ray[default]>=2.42.1"
    ],
    description="MLflow monitoring utilities for LLaMA training",
    author="LexiMind Team",
    python_requires=">=3.10",
) 