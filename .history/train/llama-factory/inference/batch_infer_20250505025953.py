from vllm import LLM, SamplingParams

# 初始化模型（路径为合并后的模型目录）
llm = LLM(model="/llama-factory/merged_model")

# 设置采样参数
sampling_params = SamplingParams(
    temperature=0.6,
    max_tokens=64
)

# 提供批量 prompt
prompts = [
    "What is LoRA?",
    "Explain gradient accumulation.",
    "What is rotary position encoding?",
    "Compare bf16 and fp16."
]

# 执行 batch inference
outputs = llm.generate(prompts, sampling_params)

# 打印结果
for prompt, output in zip(prompts, outputs):
    print(f"Prompt: {prompt}")
    print("Output:", output.outputs[0].text.strip())
    print("-" * 50)
