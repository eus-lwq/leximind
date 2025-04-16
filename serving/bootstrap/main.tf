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

provider "openstack" {
  cloud = "KVM@TACC"
}

resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "openstack_networking_secgroup_v2" "security_group" {
  name        = "example-security-group"
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

resource "openstack_networking_secgroup_rule_v2" "allow_5000" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 5000
  port_range_max    = 5000
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

resource "openstack_networking_secgroup_rule_v2" "allow_8888" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 8888
  port_range_max    = 8888
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

resource "openstack_networking_secgroup_rule_v2" "allow_9090" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 9090
  port_range_max    = 9090
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
  name            = "example-vm-${random_string.suffix.result}"
  image_name      = "CC-Ubuntu24.04"
  flavor_name     = "m1.medium"
  availability_zone = "nova"
  key_pair        = "example-keypair-${random_string.suffix.result}"

  security_groups = [openstack_networking_secgroup_v2.security_group.name, "default"]

  network {
    name = "sharednet1"
  }
}

resource "openstack_compute_keypair_v2" "keypair" {
  name       = "example-keypair-${random_string.suffix.result}"
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
      "git clone https://github.com/teaching-on-testbeds/eval-online-chi",
      "curl -sSL https://get.docker.com/ | sudo sh",
      "sudo groupadd -f docker; sudo usermod -aG docker $USER",
    ]
  }
}

resource "null_resource" "prepare_data" {
  depends_on = [openstack_compute_floatingip_associate_v2.floating_ip_association]

  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      user        = "cc"
      private_key = file(var.private_key_path) // Path to your private key
      host        = openstack_networking_floatingip_v2.floating_ip.address
    }

    inline = [
      "docker volume create food11",
      "docker compose -f eval-online-chi/docker/docker-compose-data.yaml up -d",
      "while [ -n \"$(docker ps -q)\" ]; do echo \"Waiting for containers to stop...\"; sleep 1; done; echo \"All containers stopped.\"  ",

    ]
  }
}

