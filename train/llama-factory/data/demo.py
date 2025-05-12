from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel, PeftConfig

# 路径设置
base_model_path = "meta-llama/Meta-Llama-3-8B"  # 同训练时一致
lora_model_path = "/train/output"  # 注意是容器内路径

# 加载 tokenizer 和基础模型
tokenizer = AutoTokenizer.from_pretrained(base_model_path)
base_model = AutoModelForCausalLM.from_pretrained(
    base_model_path,
    device_map="auto",
    torch_dtype="auto"
)

# 加载 LoRA adapter
model = PeftModel.from_pretrained(base_model, lora_model_path)

# 推理输入
prompt = "Explain what LexiMind does for developers."
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

# 生成回答
outputs = model.generate(**inputs, max_new_tokens=150)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)

print("\n=== 推理结果 ===\n")
print(response)
