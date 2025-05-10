resource "openstack_networking_secgroup_v2" "chi_security_group" {
  count       = local.create_chi_resources
  provider    = openstack.chi
  name        = "chi-serving-security-group"
  description = "Security group for allowing specific inbound traffic"
}

resource "openstack_networking_secgroup_rule_v2" "chi_allow_ssh" {
  count               = local.create_chi_resources
  provider            = openstack.chi
  direction           = "ingress"
  ethertype           = "IPv4"
  protocol            = "tcp"
  port_range_min      = 22
  port_range_max      = 22
  remote_ip_prefix    = "0.0.0.0/0"
  security_group_id   = openstack_networking_secgroup_v2.chi_security_group[0].id
}

resource "openstack_networking_secgroup_rule_v2" "chi_allow_prometheus" {
  count               = local.create_chi_resources
  provider            = openstack.chi
  direction           = "ingress"
  ethertype           = "IPv4"
  protocol            = "tcp"
  port_range_min      = 9090
  port_range_max      = 9090
  remote_ip_prefix    = "0.0.0.0/0"
  security_group_id   = openstack_networking_secgroup_v2.chi_security_group[0].id
}

resource "openstack_networking_secgroup_rule_v2" "chi_allow_vllm" {
  count               = local.create_chi_resources
  provider            = openstack.chi
  direction           = "ingress"
  ethertype           = "IPv4"
  protocol            = "tcp"
  port_range_min      = 8080
  port_range_max      = 8080
  remote_ip_prefix    = "0.0.0.0/0"
  security_group_id   = openstack_networking_secgroup_v2.chi_security_group[0].id
}

resource "openstack_networking_secgroup_rule_v2" "chi_allow_simpleui" {
  count               = local.create_chi_resources
  provider            = openstack.chi
  direction           = "ingress"
  ethertype           = "IPv4"
  protocol            = "tcp"
  port_range_min      = 8081
  port_range_max      = 8081
  remote_ip_prefix    = "0.0.0.0/0"
  security_group_id   = openstack_networking_secgroup_v2.chi_security_group[0].id
}

resource "openstack_compute_instance_v2" "chi_vm" {
  count             = local.create_chi_resources
  provider          = openstack.chi
  name              = "chi-serving-vm-${random_string.suffix.result}"
  image_name        = "CC-Ubuntu24.04-CUDA"
  flavor_name       = "baremetal"
  key_pair          = "chi-serving-keypair-${random_string.suffix.result}"
  security_groups   = [openstack_networking_secgroup_v2.chi_security_group[0].name]

  network {
    name = "sharednet1"
  }
  scheduler_hints {
    additional_properties = {
      "reservation" = var.reservation_id
    }
  }
}

resource "openstack_compute_keypair_v2" "chi_keypair" {
  count       = local.create_chi_resources
  provider    = openstack.chi
  name        = "chi-serving-keypair-${random_string.suffix.result}"
  public_key  = file(var.public_key_path)
}

resource "openstack_networking_floatingip_v2" "chi_floating_ip" {
  count     = local.create_chi_resources
  provider  = openstack.chi
  pool      = "public"
}

resource "openstack_compute_floatingip_associate_v2" "chi_floating_ip_association" {
  count         = local.create_chi_resources
  provider      = openstack.chi
  floating_ip   = openstack_networking_floatingip_v2.chi_floating_ip[0].address
  instance_id   = openstack_compute_instance_v2.chi_vm[0].id
}

resource "null_resource" "chi_setup" {
  count     = local.create_chi_resources
  depends_on = [openstack_compute_floatingip_associate_v2.chi_floating_ip_association]

  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      user        = "cc"
      private_key = file(var.private_key_path)
      host        = openstack_networking_floatingip_v2.chi_floating_ip[0].address
    }

    inline = [
      "curl -sSL https://get.docker.com/ | sudo sh",
      "sudo groupadd -f docker; sudo usermod -aG docker $USER",
      "mkdir -p /home/cc/scripts",
    ]
  }

  # setup_nvgpu
  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      user        = "cc"
      private_key = file(var.private_key_path)
      host        = openstack_networking_floatingip_v2.chi_floating_ip[0].address
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

resource "null_resource" "chi_upload_scripts" {
  for_each   = local.create_chi_resources > 0 ? { for file in local.script_files : file => file } : {}
  depends_on = [null_resource.chi_setup]

  triggers = {
    file_content_md5 = filemd5("scripts/${each.key}")  # Detects changes in the file
  }

  provisioner "file" {
    source      = "scripts/${each.key}"
    destination = "/home/cc/scripts/${each.key}"

    connection {
      type        = "ssh"
      user        = "cc"
      host        = openstack_networking_floatingip_v2.chi_floating_ip[0].address
      private_key = file(var.private_key_path)
    }
  }
}

resource "null_resource" "chi_run_server" {
  count      = local.create_chi_resources
  depends_on = [null_resource.chi_upload_scripts]
  
  triggers = {
    file_content_md5 = filemd5("scripts/vllm_serving.sh")  # Detects changes in the file
  }
  
  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      user        = "cc"
      private_key = file(var.private_key_path)
      host        = openstack_networking_floatingip_v2.chi_floating_ip[0].address
    }
    inline = [
      "tmux kill-server",
      "chmod +x /home/cc/scripts/*.sh",
      "MODEL_VER=${var.model_ver} /home/cc/scripts/vllm_serving.sh",
      "cd /home/cc/scripts && docker compose up -d --quiet-pull",
    ]
  }
}

output "chi_instance_public_ip" {
  value = local.create_chi_resources > 0 ? openstack_networking_floatingip_v2.chi_floating_ip[0].address : null
}

output "vllm_endpoint" {
  value = local.create_chi_resources > 0 ? "http://${openstack_networking_floatingip_v2.chi_floating_ip[0].address}:8080/v1" : null
  description = "The vLLM endpoint URL"
}

output "simple_chatui_endpoint" {
  value = local.create_chi_resources > 0 ? "http://${openstack_networking_floatingip_v2.chi_floating_ip[0].address}:8081" : null
  description = "The Simple Chat UI endpoint URL"
}
