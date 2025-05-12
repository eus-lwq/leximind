#!/bin/bash
set -e

echo "[INFO] Starting auto-retrain task..."

# Paths
WORK_DIR="$HOME/llama-factory"
DATA_FILE="$WORK_DIR/data/myalpaca2/train.json"
TRAIN_SCRIPT="$WORK_DIR/train.sh"

# Step 1: Update QA dataset from MinIO
echo "[STEP 1] Syncing MinIO QA to Alpaca format..."
python3 "$WORK_DIR/scripts/minio_to_alpaca.py"

# Step 2: Count entries in train.json
if [ ! -f "$DATA_FILE" ]; then
  echo "[ERROR] Dataset file not found: $DATA_FILE"
  exit 1
fi

QA_COUNT=$(jq length "$DATA_FILE")
echo "[INFO] Current QA pair count: $QA_COUNT"

# Step 3: If count >= threshold, trigger training
if [ "$QA_COUNT" -ge 1000 ]; then
  echo "[STEP 3] Threshold met. Launching training..."
  bash "$TRAIN_SCRIPT"
  echo "[DONE] Training triggered."
else
  echo "[SKIP] Not enough data to retrain. ($QA_COUNT < 1000)"
fi
