from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig
from peft import PeftModel
import torch

# base_model_path = "meta-llama/Meta-Llama-3-8B"
# lora_model_path = "/llama-factory/checkpoints/checkpoint-1335"
# output_path = "./merged_model"

base_model_path = "meta-llama/Meta-Llama-3-8B-instruct"
lora_model_path = "/llama-factory/output/lora"
output_path = "./merged_model"

config = AutoConfig.from_pretrained(base_model_path)
base_model = AutoModelForCausalLM.from_pretrained(
    base_model_path,
    config=config,
    torch_dtype=torch.float16,
    device_map="auto"
)
model = PeftModel.from_pretrained(base_model, lora_model_path)
model = model.merge_and_unload()


model.save_pretrained(output_path, safe_serialization=True)
tokenizer = AutoTokenizer.from_pretrained(base_model_path)
tokenizer.save_pretrained(output_path)
config.save_pretrained(output_path)  # ✅ 
