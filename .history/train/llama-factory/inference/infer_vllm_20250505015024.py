from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_id = "/llama-factory/merged_model"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

# Prepare the input prompt
inputs = tokenizer(
    "Introduce llama3 features", 
    return_tensors="pt"
).to(model.device)

# Perform Contrastive Search generation
outputs = model.generate(
    **inputs,
    max_new_tokens=512,             # Maximum number of new tokens to generate
    do_sample=False,               # Disable sampling for deterministic output
    penalty_alpha=0.6,             # Contrastive penalty strength
    top_k=4,                       # Number of candidates to consider per step
    repetition_penalty=1.15,       # Penalize repeating tokens
    no_repeat_ngram_size=3,        # Prevent repeating n-grams of size 3
    early_stopping=True,           # Stop when all beams hit EOS
    pad_token_id=tokenizer.eos_token_id  # Explicitly set padding token
)

# Decode and print the generated text
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
