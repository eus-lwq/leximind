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

locals {
  script_files = fileset("scripts", "*") # All files in scripts/
}

provider "openstack" {
  cloud = "CHI@UC"
}

resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "openstack_networking_secgroup_v2" "security_group" {
  name        = "serving-security-group"
  description = "Security group for allowing specific inbound traffic"
}

resource "openstack_networking_secgroup_rule_v2" "allow_ssh" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.security_group.id
}

resource "openstack_networking_secgroup_rule_v2" "allow_prometheus" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 9090
  port_range_max    = 9090
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.security_group.id
}

resource "openstack_compute_instance_v2" "vm" {
  name            = "serving-vm-${random_string.suffix.result}"
  image_name      = "CC-Ubuntu24.04-CUDA"
  flavor_name     = "baremetal"
  key_pair        = "serving-keypair-${random_string.suffix.result}"
  security_groups = [openstack_networking_secgroup_v2.security_group.name]

  network {
    name = "sharednet1"
  }
  scheduler_hints {
      additional_properties = {
      "reservation" = var.reservation_id
    }
  }
}

resource "openstack_compute_keypair_v2" "keypair" {
  name       = "serving-keypair-${random_string.suffix.result}"
  public_key = file(var.public_key_path)
}

resource "openstack_networking_floatingip_v2" "floating_ip" {
  pool = "public"
}

resource "openstack_compute_floatingip_associate_v2" "floating_ip_association" {
  floating_ip = openstack_networking_floatingip_v2.floating_ip.address
  instance_id = openstack_compute_instance_v2.vm.id
}

resource "null_resource" "setup" {
  depends_on = [openstack_compute_floatingip_associate_v2.floating_ip_association]

  # setup_docker
  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      user        = "cc"
      private_key = file(var.private_key_path) // Path to your private key
      host        = openstack_networking_floatingip_v2.floating_ip.address
    }

    inline = [
      "curl -sSL https://get.docker.com/ | sudo sh",
      "sudo groupadd -f docker; sudo usermod -aG docker $USER",
      "mkdir -p \"$HOME/scripts\"",
    ]
  }

  # setup_nvgpu
  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      user        = "cc"
      private_key = file(var.private_key_path) // Path to your private key
      host        = openstack_networking_floatingip_v2.floating_ip.address
    }

    inline = [
      "curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list",
      "sudo apt update",
      "sudo apt install -y python3-setuptools python3-wheel",
      "sudo apt-get install -y nvidia-container-toolkit",
      "sudo nvidia-ctk runtime configure --runtime=docker",
      "sudo jq 'if has(\"exec-opts\") then . else . + {\"exec-opts\": [\"native.cgroupdriver=cgroupfs\"]} end' /etc/docker/daemon.json | sudo tee /etc/docker/daemon.json.tmp > /dev/null && sudo mv /etc/docker/daemon.json.tmp /etc/docker/daemon.json",
      "sudo systemctl restart docker",
      "sudo apt update",
      "sudo apt -y install nvtop",
    ]
  }
}

resource "null_resource" "upload_scripts" {
  depends_on = [null_resource.setup]
  for_each = { for file in local.script_files : file => file }

  provisioner "file" {
    source      = "scripts/${each.key}"
    destination = "/home/cc/scripts/${each.key}"

    connection {
      type        = "ssh"
      user        = "cc"
      host        = openstack_networking_floatingip_v2.floating_ip.address
      private_key = file(var.private_key_path)
    }
  }
}

resource "null_resource" "run_server" {
  depends_on = [null_resource.upload_scripts]
  # setup_docker
  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      user        = "cc"
      private_key = file(var.private_key_path) // Path to your private key
      host        = openstack_networking_floatingip_v2.floating_ip.address
    }
    inline = [
      "chmod +x /home/cc/scripts/*.sh",
      "MODEL_VER=${var.model_ver} /home/cc/scripts/vllm_serving.sh",
      "cd /home/cc/scripts && docker compose up -d",
    ]
  }
}

output "instance_public_ip" {
  value = openstack_networking_floatingip_v2.floating_ip.address
}

