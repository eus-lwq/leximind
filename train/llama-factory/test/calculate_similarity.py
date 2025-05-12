import openai
import json
import numpy as np
from tqdm import tqdm
import csv
import os

# 从环境变量中读取 OpenAI API Key，避免硬编码
openai.api_key = os.getenv("OPENAI_API_KEY")

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_embedding(text, model="text-embedding-3-small"):
    response = openai.embeddings.create(
        input=[text],
        model=model
    )
    return response.data[0].embedding

input_path = "/llama-factory/output/test_predictions/generated_predictions.jsonl"
output_path = "/llama-factory/output/test_predictions/prediction_similarity.csv"

results = []

with open(input_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(tqdm(lines)):
    item = json.loads(line)
    pred = item["predict"].strip()
    label = item["label"].strip()

    try:
        pred_emb = get_embedding(pred)
        label_emb = get_embedding(label)
        sim = cosine_similarity(pred_emb, label_emb)
    except Exception as e:
        sim = -1
        print(f"[Error] Line {i}: {e}")

    results.append({
        "index": i,
        "predict": pred,
        "label": label,
        "similarity": sim
    })

with open(output_path, "w", newline='', encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["index", "predict", "label", "similarity"])
    writer.writeheader()
    writer.writerows(results)

print(f"\n✅ Done. Similarities saved to: {output_path}")
