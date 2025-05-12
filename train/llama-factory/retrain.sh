#!/bin/bash

set -e
echo "======== [RETRAIN CHECK START] ========"
echo "[INFO] Timestamp: $(date)"

FEEDBACK_FILE="feedback_data/pending.jsonl"
USED_DIR="feedback_data/used"
MERGED_FILE="data/myalpaca2/data.jsonl"

# Check if new feedback data exists
if [ ! -f "$FEEDBACK_FILE" ]; then
  echo "[INFO] No feedback data found. Skipping retrain."
  exit 0
fi

# Count new samples
NEW_COUNT=$(wc -l < "$FEEDBACK_FILE")
echo "[INFO] Detected $NEW_COUNT new feedback samples."

# Threshold to trigger retrain
THRESHOLD=1000

if [ "$NEW_COUNT" -lt "$THRESHOLD" ]; then
  echo "[INFO] Not enough new samples to retrain. Waiting for more."
  exit 0
fi

echo "[INFO] Merging new data into main dataset..."
cat "$FEEDBACK_FILE" >> "$MERGED_FILE"

# Archive used feedback
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p "$USED_DIR"
mv "$FEEDBACK_FILE" "$USED_DIR/feedback_used_$TIMESTAMP.jsonl"
echo "[INFO] Archived used feedback to $USED_DIR/feedback_used_$TIMESTAMP.jsonl"

# Launch retraining
echo "[INFO] Starting retraining..."
bash train.sh

echo "[INFO] Retraining complete at $(date)"
echo "======== [RETRAIN CHECK END] =========="
