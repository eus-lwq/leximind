from vllm import LLM, SamplingParams

llm = LLM(model="./merged_model")

samples = [
  {
    "instruction": "Where did the buffer display ?",
    "input": "@contextlib contextmanagerdef MockVimBuffers buffers current_buffer cursor_position 1 1 if current_buffer not in buffers raise RuntimeError u'Currentbuffermustbepartofthebufferslist ' with patch u'vim buffers' buffers with patch u'vim current buffer' current_buffer with patch u'vim current window cursor' cursor_position yield",
  },
  {
    "instruction": "What does the code make ?",
    "input": "def mountCgroups mounts quietRun 'cat/proc/mounts' cgdir '/sys/fs/cgroup'csdir cgdir + '/cpuset' if 'cgroup%s' % cgdir not in mounts and 'cgroups%s' % cgdir not in mounts raise Exception 'cgroupsnotmountedon' + cgdir if 'cpuset%s' % csdir not in mounts errRun 'mkdir-p' + csdir errRun 'mount-tcgroup-ocpusetcpuset' + csdir",
  },
]

def format_prompt(sample):
    return f"Instruction: {sample['instruction']}\nInput: {sample['input']}\nOutput:"

prompts = [format_prompt(s) for s in samples]
params = SamplingParams(max_tokens=64, temperature=0.6)

outputs = llm.generate(prompts, params)
for prompt, output in zip(prompts, outputs):
    print(f"{prompt}\n{output.outputs[0].text.strip()}\n{'-'*50}")
