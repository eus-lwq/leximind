import openai

# 设置本地 vLLM 推理服务
openai.api_key = "EMPTY"
openai.api_base = "http://localhost:8000/v1"

# 一组指令 prompt（Alpaca 格式）
instructions = [
    "Explain in depth why gold prices have risen recently. List at least three contributing factors.",
    "Describe how the Transformer attention mechanism works. Include equations or visual analogies.",
    "Summarize the core differences between supervised and reinforcement learning.",
    "Explain how LoRA reduces GPU memory usage during LLM fine-tuning.",
    "Describe how gradient accumulation helps fit large batches on small GPUs."
]

# 推理参数
GEN_ARGS = dict(
    model="/train/llama-factory/output/merged_model",  # 修改为你的模型路径（本地 vLLM 加载名）
    max_tokens=512,
    temperature=0.5,
    top_p=0.95,
    stop=["###", "</s>"]
)

# 批量推理主逻辑
for idx, instruction in enumerate(instructions, 1):
    prompt = f"### Instruction:\n{instruction}\n\n### Response:"
    response = openai.Completion.create(prompt=prompt, **GEN_ARGS)
    output = response["choices"][0]["text"].strip()

    print(f"\n=== [Prompt {idx}] ===\n{instruction}\n---\n{output}\n")
