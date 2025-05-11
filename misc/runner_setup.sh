#!/bin/bash

# Exit on error
set -e

### MINICONDA INSTALLATION ###
echo "🛠️ Checking Miniconda installation..."
if [ -x "$HOME/miniconda/bin/conda" ]; then
    echo "✅ Miniconda is already installed."
else
    echo "🔽 Installing Miniconda..."
    MINICONDA=Miniconda3-latest-Linux-x86_64.sh
    wget https://repo.anaconda.com/miniconda/$MINICONDA -O ~/miniconda.sh
    bash ~/miniconda.sh -b -p $HOME/miniconda
    eval "$($HOME/miniconda/bin/conda shell.bash hook)"
    conda init
    source ~/.bashrc
    # Ensure conda is in PATH for this script
    eval "$($HOME/miniconda/bin/conda shell.bash hook)"
    
    echo "✅ Miniconda installed and initialized."
fi
### END MINICONDA INSTALLATION ###

### RCLONE INSTALLATION ###
# Check if rclone is installed
if command -v rclone &> /dev/null
then
    echo "✅ rclone is already installed."
else
    echo "🔽 Installing rclone..."
    # Install rclone
    curl https://rclone.org/install.sh | sudo bash
    echo "✅ rclone installed."
fi

# this line makes sure user_allow_other is un-commented in /etc/fuse.conf
sudo sed -i '/^#user_allow_other/s/^#//' /etc/fuse.conf

# Create rclone configuration
mkdir -p ~/.config/rclone && cat <<EOF > ~/.config/rclone/rclone.conf
[chi_uc]
type = swift
user_id = []
application_credential_id = []
application_credential_secret = []
auth = https://chi.uc.chameleoncloud.org:5000/v3
region = CHI@UC
EOF

# Create mounting point
sudo mkdir -p /mnt/ece9183/project/terraform-state
# Set permissions
sudo chown -R $USER:$USER /mnt/ece9183/project/terraform-state
sudo chgrp -R $USER /mnt/ece9183/project/terraform-state

# Mount the remote storage
rclone mount chi_uc:leximind-project6-terraform-state /mnt/ece9183/project/terraform-state --daemon --allow-other --vfs-cache-mode writes
##### EXPLAINATION OF THE COMMAND #####
# --vfs-cache-mode writes
#   This setting enables caching of write operations (uploads, modifications, deletions) locally before they are synced to the remote storage. Specifically:
#   Files are first written to a local cache (stored in ~/.cache/rclone/vfs/ by default).
#   Later, they are uploaded to the remote storage (in this case, chi_uc:leximind-project6-terraform-state) in the background.
#   This improves performance for write-heavy workloads (like Terraform state operations) because the application (Terraform) doesn't have to wait for the remote storage to acknowledge every write.

# Other Possible Modes:
#   off – No caching (slow, but ensures immediate sync).
#   full – Caches both reads and writes (useful for frequently accessed files).
#   minimal – Only caches metadata (not file contents).
#   writes (what you're using) – Only caches writes (good for write-heavy workloads).

# Why Use writes Here?
#   For Terraform state files, this is a good choice because:
#   Terraform frequently modifies state files, and waiting for remote storage on every write could slow it down.
#   The cache ensures durability – even if the network drops, writes are stored locally and synced later.
#   Reduces API calls to the remote storage (important if using a provider like S3 with request limits).
##### END EXPLAINATION OF THE COMMAND #####

rclone ls /mnt/ece9183/project/terraform-state

### END OF RCLONE INSTALLATION ###



conda create -n leximind python=3.12 -y
conda activate leximind
pip install python-openstackclient
pip install git+https://github.com/ChameleonCloud/python-blazarclient.git@chameleoncloud/xena
