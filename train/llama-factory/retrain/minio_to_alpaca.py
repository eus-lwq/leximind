import os
import json
from minio import Minio

# === MinIO Configuration ===
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
BUCKET_NAME = "user-feedback-bucket"

# === Local Paths ===
LOCAL_SAVE_DIR = "/mnt/minio/qadata"
ALPACA_OUTPUT_FILE = os.path.expanduser("~/llama-factory/data/myalpaca2/train.json")

# === Connect to MinIO ===
client = Minio(
    endpoint=MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

# Ensure local directories exist
os.makedirs(LOCAL_SAVE_DIR, exist_ok=True)
os.makedirs(os.path.dirname(ALPACA_OUTPUT_FILE), exist_ok=True)

print("[INFO] Downloading files from MinIO...")
alpaca_data = []

# Iterate over MinIO bucket objects
for obj in client.list_objects(BUCKET_NAME, recursive=True):
    local_path = os.path.join(LOCAL_SAVE_DIR, obj.object_name)
    client.fget_object(BUCKET_NAME, obj.object_name, local_path)

    # Parse QA and convert to Alpaca format
    try:
        with open(local_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            alpaca_item = {
                "instruction": data["question"],
                "input": "",
                "output": data["answer"]
            }
            alpaca_data.append(alpaca_item)
    except Exception as e:
        print(f"[WARN] Skipped invalid file {obj.object_name}: {e}")

print(f"[INFO] Collected {len(alpaca_data)} valid QA pairs.")

# Write to train.json
with open(ALPACA_OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(alpaca_data, f, indent=2, ensure_ascii=False)

print(f"[DONE] Saved Alpaca-style dataset to {ALPACA_OUTPUT_FILE}")
