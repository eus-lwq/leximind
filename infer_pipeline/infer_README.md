# LexiMind Inference

LexiMind is a code assistant chatbot for developers. This Docker setup supports both GPU (vLLM) and CPU modes.

## 🐳 Quick Start

# Optionally: pull the image manually
docker pull ericyuanale/leximind-infer:latest

### GPU Mode (requires NVIDIA GPU)

```bash
docker-compose -f docker-compose.gpu.yml up -d
```


### CPU Mode 

```bash
docker-compose -f docker-compose.cpu.yml up -d
```
