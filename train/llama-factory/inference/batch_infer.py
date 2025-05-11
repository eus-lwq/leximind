from vllm import LLM, SamplingParams

# Initialize the LLM with the path to the merged model
llm = LLM(model="/llama-factory/merged_model")

# Define the sampling parameters for generation
sampling_params = SamplingParams(
    temperature=0.6,
    max_tokens=64
)

# A batch of prompts to generate responses for
prompts = [
    "What is LoRA?",
    "Explain gradient accumulation.",
    "What is rotary position encoding?",
    "Compare bf16 and fp16."
]

# Run batch inference using vLLM
outputs = llm.generate(prompts, sampling_params)

# Print each prompt with its generated output
for prompt, output in zip(prompts, outputs):
    print(f"Prompt: {prompt}")
    print("Output:", output.outputs[0].text.strip())
    print("-" * 50)
