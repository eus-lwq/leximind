# Define required providers
terraform {
  required_version = ">= 0.14.0"
    required_providers {
      openstack = {
        source  = "terraform-provider-openstack/openstack"
        version = "~> 1.53.0"
      }
    }
}

# Default provider configuration
provider "openstack" {
  cloud = "KVM@TACC"  # Default to CHI@UC
}

# Provider configurations with aliases
provider "openstack" {
  alias = "chi"
  cloud = "CHI@UC"
}

provider "openstack" {
  alias = "kvm"
  cloud = "KVM@TACC"
}