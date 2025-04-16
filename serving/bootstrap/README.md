# Terraform Setup Guide

This guide will help you set up Terraform on your local machine.

## Prerequisites

1. **Operating System**: Terraform supports Windows, macOS, and Linux.
2. **Installations**:
    - [Terraform](https://www.terraform.io/downloads.html)
    - [Git](https://git-scm.com/downloads) (optional, for version control)

## Installation Steps

- Visit the [Terraform Downloads Page](https://www.terraform.io/downloads.html).
- Download the appropriate binary for your operating system.

- **Windows**:
  1. Extract the downloaded `.zip` file.
  2. Move the `terraform.exe` file to a directory included in your system's `PATH` (e.g., `C:\Windows\System32`).
  3. Verify installation by running `terraform --version` in Command Prompt or PowerShell.
  
- **macOS/Linux**:
  1. Extract the downloaded `.zip` file.
  2. Move the `terraform` binary to `/usr/local/bin/` or another directory in your `PATH`.
  3. Verify installation by running `terraform --version` in the terminal.

- Create a working directory for your Terraform configuration files:
  ```bash
  mkdir terraform-project
  cd terraform-project

- Initialize Terraform in your project directory:

## Basic Usage
1. **Write Configuration**: Create a `.tf` file (e.g., `main.tf`) with your infrastructure configuration.
2. **Initialize**: Run `terraform init` to initialize the working directory.
3. **Plan**: Run `terraform plan` to preview changes.
4. **Apply**: Run `terraform apply` to create or update infrastructure.
5. **Destroy**: Run `terraform destroy` to tear down infrastructure.

## Chameleon setup in this 

1. Obtain cloud creds from Chameleon UI

2. Set the env variable that reference to the cloud creds file, for example:

``` bash
export OS_CLIENT_CONFIG_FILE=clouds.yaml
```

3. Obtain private and public keys

4. Update variable reference to the private and public keys