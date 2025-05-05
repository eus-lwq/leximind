import openai

# Connect to local vLLM OpenAI-compatible server
openai.api_key = "EMPTY"
openai.api_base = "http://localhost:8000/v1"

# Define the instruction prompt (Alpaca style)
instruction = (
    "Explain in depth why gold prices have risen recently. "
    "List at least three contributing factors, such as geopolitical risks or inflation, "
    "and elaborate on each point with specific context if possible."
)

# Build the full Alpaca-style prompt
prompt = f"### Instruction:\n{instruction}\n\n### Response:"

# Run inference
response = openai.Completion.create(
    model="/train/llama-factory/output/merged_model",  # Use your actual model name
    prompt=prompt,
    max_tokens=512,        # Allows longer, more detailed responses
    temperature=0.5,       # Lower temperature for more factual coherence
    top_p=0.95,
    stop=["###", "</s>"]   # Prevents over-generation or repetition
)

# Print result
print("\n=== Model Output ===\n")
print(response["choices"][0]["text"].strip())
