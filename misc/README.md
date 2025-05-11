# Miscellaneous Scripts and Utilities

This folder contains various utility scripts and configuration files for managing resources and setting up the environment. Below is a description of each file and its purpose.

## Files and Their Descriptions

### [`mount_volume.py`](./mount_volume.py)
- **Description**: Python script to mount a volume for use in the `kvm@tacc` site.

### [`runner_setup.sh`](./runner_setup.sh)
- **Description**: Shell script to set up the self-hosted GitHub Action runner for running deployment tasks.
- **Note**: Before executing this script, ensure that the `rclone.conf` file is updated with the correct configuration for your environment.

### [`unmount_volume.py`](./unmount_volume.py)
- **Description**: Python script to unmount a volume and clean up resources for use in the `kvm@tacc` site.

---

## Notes
- Ensure you have the necessary permissions to execute these scripts.
- Refer to the individual script files for detailed usage instructions.
