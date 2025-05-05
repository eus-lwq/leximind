from vllm import LLM, SamplingParams

llm = LLM(model="./merged_model")

samples = [
    {
        "instruction": "What does the code get  ?",
        "input": "def get_volume_type_qos_specs volume_type_id ctxt context get_admin_context res db volume_type_qos_specs_get ctxt volume_type_id return res"
    },
    {
        "instruction": "How do a kext unload ?",
        "input": "def UninstallDriver bundle_name km objc KextManager cf_bundle_name km PyStringToCFString bundle_name status km iokit KextManagerUnloadKextWithIdentifier cf_bundle_name km dll CFRelease cf_bundle_name return status"
    }
]

def format_prompt(sample):
    return f"Instruction: {sample['instruction']}\nInput: {sample['input']}\nOutput:"

prompts = [format_prompt(s) for s in samples]
params = SamplingParams(max_tokens=64, temperature=0.6)

outputs = llm.generate(prompts, params)
for prompt, output in zip(prompts, outputs):
    print(f"{prompt}\n{output.outputs[0].text.strip()}\n{'-'*50}")
