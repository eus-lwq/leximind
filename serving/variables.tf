variable "private_key_path" {
  description = "Path to the private key file"
  type        = string
  default     = "id_rsa" // Update with the default path if applicable
}

variable "public_key_path" {
  description = "Path to the public key file"
  type        = string
  default     = "id_rsa.pub" // Update with the default path if applicable
}

variable "reservation_id" {
  type        = string
  # default     = ""
  default     = "33a99b88-c200-48e8-a100-244025e0ba53" // Update with the default value if applicable
}

variable "model_ver" {
  type        = string
  default     = "whole_model" // Update with the default value if applicable
}

variable "vol_uuid" {
  type        = string
  # default     = ""
  # default     = "d5160a9b-3c25-453d-b798-1f96c1adb0ec"
  default     = "0189c2f5-7a72-4738-a5b4-3741510dc472" // Update with the default value if applicable
}

variable "python_path" {
  description = "Path to the Python executable (e.g., path to virtual environment's python)"
  type        = string
  default     = "/Users/xf/CondaEnvs/terraform/bin/python"
}