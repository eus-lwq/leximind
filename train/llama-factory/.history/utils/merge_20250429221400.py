from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig
from peft import PeftModel
import torch

base_model_path = "meta-llama/Meta-Llama-3-8B"
lora_model_path = "/Users/ericyuan/Desktop/llama-factory/checkpoints"
output_path = "./merged_model"

# 加载 config
config = AutoConfig.from_pretrained(base_model_path)

# 加载 base 模型并合并 LoRA
base_model = AutoModelForCausalLM.from_pretrained(
    base_model_path,
    config=config,
    torch_dtype=torch.float16,
    device_map="auto"
)
model = PeftModel.from_pretrained(base_model, lora_model_path)
model = model.merge_and_unload()

# 保存合并后的模型
model.save_pretrained(output_path, safe_serialization=True)
tokenizer = AutoTokenizer.from_pretrained(base_model_path)
tokenizer.save_pretrained(output_path)
config.save_pretrained(output_path)  # ✅ 很重要：保存 config.json！
