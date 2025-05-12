resource "openstack_networking_secgroup_v2" "kvm_security_group" {
  count       = local.create_kvm_resources
  provider    = openstack.kvm
  name        = "kvm-serving-secgroup-project6-${random_string.suffix.result}"
  description = "Security group for allowing specific inbound traffic"
}

resource "openstack_networking_secgroup_rule_v2" "kvm_allow_ssh" {
  count               = local.create_kvm_resources
  provider            = openstack.kvm
  direction           = "ingress"
  ethertype           = "IPv4"
  protocol            = "tcp"
  port_range_min      = 22
  port_range_max      = 22
  remote_ip_prefix    = "0.0.0.0/0"
  security_group_id   = openstack_networking_secgroup_v2.kvm_security_group[0].id
}

resource "openstack_networking_secgroup_rule_v2" "kvm_allow_prometheus" {
  count               = local.create_kvm_resources
  provider            = openstack.kvm
  direction           = "ingress"
  ethertype           = "IPv4"
  protocol            = "tcp"
  port_range_min      = 9090
  port_range_max      = 9090
  remote_ip_prefix    = "0.0.0.0/0"
  security_group_id   = openstack_networking_secgroup_v2.kvm_security_group[0].id
}

resource "openstack_networking_secgroup_rule_v2" "kvm_allow_fastapi" {
  count               = local.create_kvm_resources
  provider            = openstack.kvm
  direction           = "ingress"
  ethertype           = "IPv4"
  protocol            = "tcp"
  port_range_min      = 8080
  port_range_max      = 8080
  remote_ip_prefix    = "0.0.0.0/0"
  security_group_id   = openstack_networking_secgroup_v2.kvm_security_group[0].id
}

resource "openstack_compute_instance_v2" "kvm_vm" {
  count             = local.create_kvm_resources
  provider          = openstack.kvm
  name              = "kvm-serving-vm-project6-${random_string.suffix.result}"
  image_name        = "CC-Ubuntu24.04"
  flavor_name       = "m1.medium"
  availability_zone = "nova"
  key_pair          = "kvm-serving-keypair-project6-${random_string.suffix.result}"

  security_groups = [openstack_networking_secgroup_v2.kvm_security_group[0].name, "default"]

  network {
    name = "sharednet1"
  }
}

resource "openstack_compute_keypair_v2" "kvm_keypair" {
  count       = local.create_kvm_resources
  provider    = openstack.kvm
  name        = "kvm-serving-keypair-project6-${random_string.suffix.result}"
  public_key  = file(var.public_key_path)
}

resource "openstack_networking_floatingip_v2" "kvm_floating_ip" {
  count     = local.create_kvm_resources
  provider  = openstack.kvm
  pool      = "public"
}

resource "openstack_compute_floatingip_associate_v2" "kvm_floating_ip_association" {
  count         = local.create_kvm_resources
  provider      = openstack.kvm
  floating_ip   = openstack_networking_floatingip_v2.kvm_floating_ip[0].address
  instance_id   = openstack_compute_instance_v2.kvm_vm[0].id
}

resource "null_resource" "kvm_setup_docker" {
  count     = local.create_kvm_resources
  depends_on = [openstack_compute_floatingip_associate_v2.kvm_floating_ip_association]

  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      user        = "cc"
      private_key = file(var.private_key_path)
      host        = openstack_networking_floatingip_v2.kvm_floating_ip[0].address
    }

    inline = [
      "curl -sSL https://get.docker.com/ | sudo sh",
      "sudo groupadd -f docker; sudo usermod -aG docker $USER",
      "mkdir -p /home/cc/scripts",
    ]
  }
}

resource "null_resource" "kvm_upload_scripts" {
  for_each   = local.create_kvm_resources > 0 ? { for file in local.script_files : file => file } : {}
  depends_on = [null_resource.kvm_setup_docker]

  triggers = {
    file_content_md5 = filemd5("scripts/${each.key}")  # Detects changes in the file
  }

  provisioner "file" {
    source      = "scripts/${each.key}"
    destination = "/home/cc/scripts/${each.key}"

    connection {
      type        = "ssh"
      user        = "cc"
      host        = openstack_networking_floatingip_v2.kvm_floating_ip[0].address
      private_key = file(var.private_key_path)
    }
  }
}

resource "null_resource" "kvm_run_server" {
  count      = local.create_kvm_resources
  depends_on = [null_resource.kvm_upload_scripts]

  triggers = {
    file_content_md5 = filemd5("scripts/fastapi_serving.sh")  # Detects changes in the file
  }
  
  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      user        = "cc"
      private_key = file(var.private_key_path)
      host        = openstack_networking_floatingip_v2.kvm_floating_ip[0].address
    }
    inline = [
      "tmux kill-server",
      "chmod +x /home/cc/scripts/*.sh",
      "/home/cc/scripts/fastapi_serving.sh",
      "cd /home/cc/scripts && docker compose up -d --quiet-pull",
    ]
  }
}

output "kvm_instance_public_ip" {
  value = local.create_kvm_resources > 0 ? openstack_networking_floatingip_v2.kvm_floating_ip[0].address : null
}

output "kvm_volume_mount_info" {
  value = local.create_kvm_resources > 0 ? data.external.kvm_mount_volume[0].result : null
  description = "Information about the mounted volume, including device name and any status messages"
}

data "external" "kvm_mount_volume" {
  depends_on = [null_resource.kvm_upload_scripts]
  count   = local.create_kvm_resources > 0 && !local.is_destroy ? 1 : 0
  program = [var.python_path, "${path.module}/../misc/mount_volume.py", "KVM@TACC", openstack_compute_instance_v2.kvm_vm[0].id, var.vol_uuid]
}

resource "null_resource" "kvm_mount_volume" {
  count      = local.create_kvm_resources
  depends_on = [data.external.kvm_mount_volume]

  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      user        = "cc"
      host        = openstack_networking_floatingip_v2.kvm_floating_ip[0].address
      private_key = file(var.private_key_path)
    }

    inline = [
      "sudo mkdir -p ${local.mount_point}",
      # We added 1 after the device path 
      "sudo mount ${data.external.kvm_mount_volume[0].result.device}1 ${local.mount_point}",
      "sudo chown -R cc ${local.mount_point}",
      "sudo chgrp -R cc ${local.mount_point}",
    ]
  }
}

# Add local DNS entry for LLM endpoint
resource "null_resource" "kvm_add_dns_entry" {
  count      = local.create_kvm_resources > 0 && local.create_chi_resources > 0 ? 1 : 0
  depends_on = [
    openstack_compute_floatingip_associate_v2.kvm_floating_ip_association,
    openstack_compute_floatingip_associate_v2.chi_floating_ip_association
  ]

  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      user        = "cc"
      host        = openstack_networking_floatingip_v2.kvm_floating_ip[0].address
      private_key = file(var.private_key_path)
    }

    inline = [
      "echo '${openstack_networking_floatingip_v2.chi_floating_ip[0].address} llmendpoint' | sudo tee -a /etc/hosts"
    ]
  }
}



