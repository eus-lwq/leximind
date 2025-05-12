import json
import re

input_path = "/train/llamafactory/data/myalpaca/train_alpaca.json"
output_path = "/train/llamafactory/data/myalpaca/train_alpaca_cleaned.json"

def clean_output(output_raw):
    if isinstance(output_raw, list):
        return output_raw[0].strip() if output_raw else ""
    if isinstance(output_raw, str):
        output_raw = output_raw.strip()

        # 检查是否是 list 结构包在字符串里
        try:
            parsed = json.loads(output_raw)
            if isinstance(parsed, list) and parsed:
                return parsed[0].strip()
        except json.JSONDecodeError:
            pass

        # 如果含有大量转义字符，做简单去除
        output_raw = re.sub(r'\\[nrt"]+', ' ', output_raw)
        output_raw = re.sub(r'\s+', ' ', output_raw)
        return output_raw.strip()
    return str(output_raw).strip()

with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)

cleaned = []
dropped = []

for i, item in enumerate(data):
    if isinstance(item, dict):
        instruction = item.get("instruction", "").strip()
        output = clean_output(item.get("output", ""))
        if instruction and output:
            cleaned.append({
                "instruction": instruction,
                "input": item.get("input", ""),
                "output": output
            })
        else:
            dropped.append((i, item))
    else:
        dropped.append((i, item))

# 保存清洗结果
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(cleaned, f, ensure_ascii=False, indent=2)

# 打印统计信息
print(f"✅ 总样本数: {len(data)}")
print(f"✅ 保留样本: {len(cleaned)}")
print(f"⚠️ 丢弃样本: {len(dropped)}")
if dropped:
    print("⚠️ 示例丢弃项:")
    for i, d in dropped[:3]:
        print(f"  Index {i}: {str(d)[:100]}...")
