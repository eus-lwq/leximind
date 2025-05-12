from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import time

# Model configuration
MODEL_PATH = "/home/cc/model/whole_model"  # Path to the model

# Inference parameters
MAX_NEW_TOKENS = 64
TEMPERATURE = 0.6

# Test samples
samples = [
    {
        "instruction": "Where did the buffer display ?",
        "input": "@contextlib contextmanagerdef MockVimBuffers buffers current_buffer cursor_position 1 1 if current_buffer not in buffers raise RuntimeError u'Currentbuffermustbepartofthebufferslist ' with patch u'vim buffers' buffers with patch u'vim current buffer' current_buffer with patch u'vim current window cursor' cursor_position yield",
    },
    {
        "instruction": "What does the code make ?",
        "input": "def mountCgroups mounts quietRun 'cat/proc/mounts' cgdir '/sys/fs/cgroup'csdir cgdir + '/cpuset' if 'cgroup%s' % cgdir not in mounts and 'cgroups%s' % cgdir not in mounts raise Exception 'cgroupsnotmountedon' + cgdir if 'cpuset%s' % csdir not in mounts errRun 'mkdir-p' + csdir errRun 'mount-tcgroup-ocpusetcpuset' + csdir",
    },
    {
        "instruction": "What does the new denying rule match  ?",
        "input": "private boolean checkRuleMatch ( ACLRule newRule ) { List < Integer > allowRuleList = new ArrayList < > ( ) ; for ( ACLRule existingRule : getRules ( ) ) { if ( newRule . match ( existingRule ) ) { return _BOOL ; } if ( existingRule . getAction ( ) == Action . ALLOW && newRule . getAction ( ) == Action . DENY ) { if ( existingRule . match ( newRule ) ) { allowRuleList . add ( existingRule . getId ( ) ) ; } } } deny2Allow . put ( newRule . getId ( ) , allowRuleList ) ; return _BOOL ; }",
    },
    {
        "instruction": "What list in an environment ?",
        "input": "def list_states saltenv 'base' return __context__['fileclient'] list_states saltenv",
    },
]

# Load model and tokenizer
print("Loading model and tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, use_fast=True)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, torch_dtype=torch.float16).cuda()
model.eval()


def format_prompt(sample):
    """
    Format the input prompt for the model.
    """
    return f"Instruction: {sample['instruction']}\nInput: {sample['input']}\nOutput:"


def run_serial_inference(samples):
    """
    Perform serial inference on the samples and measure performance.
    """
    start_time = time.time()
    for sample in samples:
        prompt = format_prompt(sample)
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

        with torch.no_grad():
            output = model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                temperature=TEMPERATURE,
                do_sample=True,
                top_p=0.9,
                top_k=50,
                eos_token_id=tokenizer.eos_token_id,
                pad_token_id=tokenizer.pad_token_id,
            )

        decoded = tokenizer.decode(output[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
        print(f"{prompt}\n{decoded.strip()}\n{'-'*50}")

    end_time = time.time()
    latency = (end_time - start_time) / len(samples)
    print(f"Serial Inference Metrics:\n  Total Time: {end_time - start_time:.2f}s\n  Latency per Sample: {latency:.2f}s\n")


def run_batched_inference(samples, batch_size=2):
    """
    Perform batched inference on the samples and measure performance.
    """
    start_time = time.time()
    for i in range(0, len(samples), batch_size):
        batch = samples[i:i + batch_size]
        prompts = [format_prompt(sample) for sample in batch]
        inputs = tokenizer(prompts, return_tensors="pt", padding=True, truncation=True).to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                temperature=TEMPERATURE,
                do_sample=True,
                top_p=0.9,
                top_k=50,
                eos_token_id=tokenizer.eos_token_id,
                pad_token_id=tokenizer.pad_token_id,
            )

        for j, output in enumerate(outputs):
            decoded = tokenizer.decode(output[inputs['input_ids'].shape[1]:], skip_special_tokens=True)
            print(f"{prompts[j]}\n{decoded.strip()}\n{'-'*50}")

    end_time = time.time()
    latency = (end_time - start_time) / len(samples)
    throughput = len(samples) / (end_time - start_time)
    print(f"Batched Inference Metrics:\n  Total Time: {end_time - start_time:.2f}s\n  Latency per Sample: {latency:.2f}s\n  Throughput: {throughput:.2f} samples/s\n")


if __name__ == "__main__":
    print("Running Serial Inference...")
    run_serial_inference(samples)

    print("Running Batched Inference...")
    run_batched_inference(samples, batch_size=2)