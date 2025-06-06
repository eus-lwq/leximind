# 🚀 Train LLaMA3-8b with LoRA using `llama-factory`

This repository provides a simple setup for fine-tuning LLaMA3 models using LoRA via the `llama-factory` framework.

Our llama-factory is customized and u can refer it from this link: https://github.com/Yuan-33/llama-factory

Run the environment and dependency setup scripts:

```bash
bash setup_train.sh
```

Use demo below if meets trouble:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

Next, set your Hugging Face token to access the model:

```bash
export HF_TOKEN=your_hf_token
```

Finally, start training:

```bash
bash train.sh
```

Training outputs, including model checkpoints and logs, will be saved to the `./outputs/` directory or the path specified in your configuration. Make sure `train.sh` is properly configured with your model path, dataset, LoRA/QLoRA settings, and training arguments. Wandb is used to track the whole training process.

Happy training! 🚀
