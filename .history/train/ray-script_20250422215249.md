1. using boostrap6 to set up the environment
2. create codeqa volume
3. compose data.yaml ray.yaml
4. cp llama-factory
5. docker pull ericyuanale/llama-env:llm-v1
6. cp llama-factory -> llama-env docker： 
docker cp ~/llama-factory vigilant_torvalds:/workspace/

7. apt update && apt install -y python3-dev build-essential

8. cd -> llama-factory  bash train.sh 可以训练
9. pip install wandb

可以普通训练 

10. (inside docker) pip install "ray[default]==2.42.1"

