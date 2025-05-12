locals {
  script_files = fileset("scripts", "*") # All files in scripts/
  create_kvm_resources = var.vol_uuid != "" ? 1 : 0
  create_chi_resources = var.reservation_id != "" ? 1 : 0
  mount_point = "/mnt/block"
  is_destroy = terraform.workspace == "destroy"
  is_lora = (var.lora_adapter_path != "" && var.model_name != "" && var.reservation_id != "") ? 1 : 0
  is_full_model = (var.lora_adapter_path == "" && var.model_name != "" && var.reservation_id != "") ? 1 : 0
}

resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

