# This use case demonstrates how to deploy a FastAPI application with a LoRA model using Terraform. 
# It is meant to be run in a computer that does not have powerful GPUs, as one could tell from the model size.


private_key_path = "id_rsa" # Update with the actual path to your private key file
public_key_path  = "id_rsa.pub" # Update with the actual path to your public key file
reservation_id = "0a63baa7-049c-4123-b5ff-d10ecb3ceba3" # Update if needed
model_name = "meta-llama/Meta-Llama-3-8B-Instruct" # Update with the desired model path
lora_adapter_path = "model/lora_adapter" # Update with the desired LoRA adapter path
vol_uuid = "0189c2f5-7a72-4738-a5b4-3741510dc472" # Update with the correct volume UUID
python_path = "python" # Update with the correct Python executable path