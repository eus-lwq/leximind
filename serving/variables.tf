variable "private_key_path" {
  description = "Path to the private key file"
  type        = string
  default     = "" // Update with the default path if applicable
}

variable "public_key_path" {
  description = "Path to the public key file"
  type        = string
  default     = "" // Update with the default path if applicable
}

variable "reservation_id" {
  type        = string
  default     = "" // Update if needed
}

variable "model_name" {
  type        = string
  default     = "" // Update if needed
}

variable "lora_adapter_path" {
  type        = string
  default     = "" // Update if needed
}

variable "vol_uuid" {
  type        = string
  default     = "" // Update if needed
}

variable "python_path" {
  description = "Path to the Python executable (e.g., path to virtual environment's python)"
  type        = string
  default     = "" // Update if needed
}