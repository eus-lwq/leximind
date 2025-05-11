# This use case demonstrates how to deploy a FastAPI application with a LoRA model using Terraform. 
# It is meant to be run in a computer that has powerful GPUs. The whole model is considered to be large size model.

private_key_path = "id_rsa" # Update with the actual path to your private key file
public_key_path  = "id_rsa.pub" # Update with the actual path to your public key file
reservation_id = "ff3c23e7-1d12-442a-9af0-05697e0bb273" # Update if needed
model_name = "model/whole_model" # Update with the desired model path
lora_adapter_path = "" # Update with the desired LoRA adapter path
vol_uuid = "0189c2f5-7a72-4738-a5b4-3741510dc472" # Update with the correct volume UUID
python_path = "python" # Update with the correct Python executable path