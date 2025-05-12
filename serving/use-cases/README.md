# Use Cases for Terraform Variable Files

This folder contains various `.tfvars` files, each representing a specific use case for deploying machine learning models and applications using Terraform. Below is a description of each file and its intended use case.

## Files and Their Use Cases

### [`fastapi.tfvars`](./fastapi.tfvars)
- **Use Case**: This file is used to test the deployment of a FastAPI application with RAG (Retrieval-Augmented Generation) on the `kvm@tacc` site.
- **Deployment Target**: KVM virtual machines at TACC.

---

### [`fastapi+lora_model.tfvars`](./fastapi+lora_model.tfvars)
- **Use Case**: This file is used to test the deployment of a FastAPI application integrated with a LoRA (Low-Rank Adaptation) model on the `kvm@tacc` site.
- **Deployment Target**: KVM virtual machines at TACC and Baremetal GPU resources at CHI@UC.

---

### [`fastapi+model.tfvars`](./fastapi+model.tfvars)
- **Use Case**: This file is used to test the deployment of a FastAPI application integrated with a full model on the `kvm@tacc` site.
- **Deployment Target**: KVM virtual machines at TACC and Baremetal GPU resources at CHI@UC.

---

### [`lora_model.tfvars`](./lora_model.tfvars)
- **Use Case**: This file is used to test the deployment of a small base model with a LoRA adapter on the `chi@uc` site.
- **Deployment Target**: Baremetal GPU resources at CHI@UC.

---

### [`model.tfvars`](./model.tfvars)
- **Use Case**: This file is used to test the deployment of a full model on baremetal GPU resources at the `chi@uc` site.
- **Deployment Target**: Baremetal GPU resources at CHI@UC.

---

## Summary Chart

| File Name                     | Use Case Description                                      | Deployment Target          |
|-------------------------------|----------------------------------------------------------|----------------------------|
| [`fastapi.tfvars`](./fastapi.tfvars)             | FastAPI + RAG deployment                                 | KVM @ TACC                 |
| [`fastapi+lora_model.tfvars`](./fastapi+lora_model.tfvars) | FastAPI + LoRA model deployment                          | KVM @ TACC +   Baremetal GPU @ CHI@UC             |
| [`fastapi+model.tfvars`](./fastapi+model.tfvars)         | FastAPI + Full model deployment                          | KVM @ TACC    +   Baremetal GPU @ CHI@UC             |
| [`lora_model.tfvars`](./lora_model.tfvars)       | Small base model + LoRA adapter deployment               | Baremetal GPU @ CHI@UC     |
| [`model.tfvars`](./model.tfvars)                | Full model deployment                                    | Baremetal GPU @ CHI@UC     |

