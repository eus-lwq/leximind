import openai

openai.api_key = "your_api_key_here"
openai.api_base = "http://localhost:8000/v1"

prompts = [
    "What is a kernel?",
    "Explain LoRA in one sentence.",
    "How to write a function in Python?",
    "What does the buffer display?",
]

for prompt in prompts:
    response = openai.Completion.create(
        model="./merged_model",
        prompt=prompt,
        max_tokens=60,
        temperature=0.6
    )
    print(f"Prompt: {prompt}")
    print(f"Output: {response['choices'][0]['text'].strip()}")
