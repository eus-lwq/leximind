from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# 设置模型路径（支持原 HuggingFace 或本地 merged_model）
model_path = "./merged_model"

# 使用 float16 加载模型（适配 RTX6000）
tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=True)
model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float16).cuda()
model.eval()

# 测试样本
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

def format_prompt(sample):
    return f"Instruction: {sample['instruction']}\nInput: {sample['input']}\nOutput:"

# 推理参数
max_new_tokens = 64
temperature = 0.6

# 执行推理
for sample in samples:
    prompt = format_prompt(sample)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=True,
            top_p=0.9,
            top_k=50,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.pad_token_id,
        )

    decoded = tokenizer.decode(output[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
    print(f"{prompt}\n{decoded.strip()}\n{'-'*50}")
