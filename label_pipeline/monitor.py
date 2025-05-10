#!/usr/bin/env python3
"""Monitor the status of all services in the pipeline"""
import requests
import time
import os
import json
from datetime import datetime

def check_label_studio():
    """Check if Label Studio is up and running"""
    try:
        url = os.getenv('LABEL_STUDIO_URL', 'http://label-studio:8080')
        response = requests.get(f"{url}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_minio():
    """Check if MinIO is up and running"""
    try:
        url = os.getenv('MINIO_URL', 'http://minio:9000')
        response = requests.get(f"{url}/minio/health/live", timeout=5)
        return response.status_code == 200
    except:
        return False

def print_status(service, status):
    """Print service status with color"""
    time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    status_str = "✅ UP" if status else "❌ DOWN"
    color = "\033[92m" if status else "\033[91m"  # Green for up, red for down
    reset = "\033[0m"
    print(f"[{time_str}] {color}{service}: {status_str}{reset}")

def main():
    """Main monitoring loop"""
    print("Starting service monitoring...")
    
    while True:
        try:
            # Check service statuses
            ls_status = check_label_studio()
            minio_status = check_minio()
            
            # Print status
            print("\n--- Service Status Report ---")
            print_status("Label Studio", ls_status)
            print_status("MinIO", minio_status)
            print("-----------------------------\n")
            
            # Sleep for a minute
            time.sleep(60)
        except Exception as e:
            print(f"Error in monitoring: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()