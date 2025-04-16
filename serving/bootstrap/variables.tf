variable "private_key_path" {
  description = "Path to the private key file"
  type        = string
  # default     = "id_rsa" // Update with the default path if applicable
}

variable "public_key_path" {
  description = "Path to the public key file"
  type        = string
  # default     = "id_rsa.pub" // Update with the default path if applicable
}