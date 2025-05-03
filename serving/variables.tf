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
  default     = "" // Update with the default value if applicable
}

variable "model_ver" {
  type        = string
  default     = "whole_model" // Update with the default value if applicable
}