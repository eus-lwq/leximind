# Define required providers
terraform {
  required_version = ">= 0.14.0"
    required_providers {
      openstack = {
        source  = "terraform-provider-openstack/openstack"
        version = "~> 1.53.0"
      }
    }
  backend "local" {
    path = "/mnt/ece9183/project/terraform-state/monitoring/terraform.tfstate"
  }
}

provider "openstack" {
  cloud = "KVM@TACC"
}

locals {
  script_files = fileset("scripts", "*") # All files in scripts/
}

resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "openstack_networking_secgroup_v2" "security_group" {
  name        = "monitoring-security-group"
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

resource "openstack_networking_secgroup_rule_v2" "allow_8000" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 8000
  port_range_max    = 8000
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.security_group.id
}

resource "openstack_networking_secgroup_rule_v2" "allow_3000" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 3000
  port_range_max    = 3000
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.security_group.id
}

resource "openstack_networking_secgroup_rule_v2" "allow_8080" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 8080
  port_range_max    = 8080
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.security_group.id
}

resource "openstack_compute_instance_v2" "vm" {
  name            = "monitoring-vm-project6-${random_string.suffix.result}"
  image_name      = "CC-Ubuntu24.04"
  flavor_name     = "m1.medium"
  availability_zone = "nova"
  key_pair        = "monitoring-keypair-project6-${random_string.suffix.result}"

  security_groups = [openstack_networking_secgroup_v2.security_group.name, "default"]

  network {
    name = "sharednet1"
  }
}

resource "openstack_compute_keypair_v2" "keypair" {
  name       = "monitoring-keypair-project6-${random_string.suffix.result}"
  public_key = file(var.public_key_path)
}

resource "openstack_networking_floatingip_v2" "floating_ip" {
  pool = "public"
}

resource "openstack_compute_floatingip_associate_v2" "floating_ip_association" {
  floating_ip = openstack_networking_floatingip_v2.floating_ip.address
  instance_id = openstack_compute_instance_v2.vm.id
}

resource "null_resource" "setup_docker" {
  depends_on = [openstack_compute_floatingip_associate_v2.floating_ip_association]

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
      "mkdir -p /home/cc/scripts",
    ]
  }
}

resource "null_resource" "upload_scripts" {
  depends_on = [null_resource.setup_docker]
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

resource "null_resource" "setup_monitoring" {
  depends_on = [null_resource.setup_docker, null_resource.upload_scripts]
  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      user        = "cc"
      private_key = file(var.private_key_path) // Path to your private key
      host        = openstack_networking_floatingip_v2.floating_ip.address
    }

    inline = [
      "cd /home/cc/scripts && docker compose up -d",
    ]
  }
}

resource "null_resource" "wait_for_grafana" {
  depends_on = [null_resource.setup_monitoring]

  provisioner "local-exec" {
    command = <<EOT
    for i in {1..5}; do
      status=$(curl -s -o /dev/null -w "%%{http_code}" ${openstack_networking_floatingip_v2.floating_ip.address}:3000/api/health)
      if [ "$status" -eq 200 ]; then
        echo "Grafana is ready."
        exit 0
      fi
      echo "Waiting for Grafana... (attempt $i)"
      sleep 30
    done
    echo "Timeout waiting for Grafana."
    exit 1
    EOT
  }
}

resource "null_resource" "create_vllm_datasource" {
  count      = var.vllm_endpoint != "" ? 1 : 0
  depends_on = [null_resource.wait_for_grafana]
  provisioner "local-exec" {
    command = <<EOT
    curl -s -X POST ${openstack_networking_floatingip_v2.floating_ip.address}:3000/api/datasources \
      -H "Content-Type: application/json" \
      -u admin:admin \
      -d '{
        "name":"Prometheus",
        "type":"prometheus",
        "access":"proxy",
        "url":"http://${var.vllm_endpoint}:9090",
        "basicAuth": false,
        "isDefault": true
      }'
    EOT
  }
  provisioner "local-exec" {
    command = <<EOT
    curl -s -X POST ${openstack_networking_floatingip_v2.floating_ip.address}:3000/api/dashboards/import \
      -H "Content-Type: application/json" \
      -u admin:admin \
      -d @./scripts/vllm-dashboard.json
    EOT
  }
}

resource "null_resource" "create_fastapi_datasource" {
  count      = var.fastapi_endpoint != "" ? 1 : 0
  depends_on = [null_resource.wait_for_grafana]
  provisioner "local-exec" {
    command = <<EOT
    curl -s -X POST ${openstack_networking_floatingip_v2.floating_ip.address}:3000/api/datasources \
      -H "Content-Type: application/json" \
      -u admin:admin \
      -d '{
        "name":"Prometheus",
        "type":"prometheus",
        "access":"proxy",
        "url":"http://${var.fastapi_endpoint}:9090",
        "basicAuth": false,
        "isDefault": true
      }'
    EOT
  }
  provisioner "local-exec" {
    command = <<EOT
    curl -s -X POST ${openstack_networking_floatingip_v2.floating_ip.address}:3000/api/dashboards/import \
      -H "Content-Type: application/json" \
      -u admin:admin \
      -d @./scripts/fastapi-dashboard.json
    EOT
  }
}

output "instance_public_ip" {
  value = openstack_networking_floatingip_v2.floating_ip.address
}


