# ✅ 模型类定义：LLaMA 2 + LoRA adapter（可选）
from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer
from peft import PeftModel, PeftConfig
import torch

# base model
class Llama2ChatModel:
    def __init__(self,
                 base_model='NousResearch/Llama-2-7b-hf',
                 adapter_path=None,
                 use_lora=True):
        self.tokenizer = AutoTokenizer.from_pretrained(base_model, use_fast=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            base_model,
            device_map='auto',
            torch_dtype=torch.float16
        )
        if use_lora and adapter_path:
            self.model = PeftModel.from_pretrained(self.model, adapter_path)
            print("✅ LoRA adapter loaded from:", adapter_path)
        else:
            print("⚠️ No LoRA adapter applied (base model only)")
        self.model.eval()

    def chat(self, user_input, max_new_tokens=128):
        prompt = f"[INST] {user_input} [/INST]"
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            top_p=0.9,
            temperature=0.7
        )
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response.split('[/INST]')[-1].strip()


#  Testing
chatbot = Llama2ChatModel()
reply = chatbot.chat("What is the difference between supervised and unsupervised learning?")
print("🤖", reply)