#!/usr/bin/env python3

import os
import sys
import json
import openstack
import time
from openstack import connection

def mount_volume(cloud_name, instance_id, volume_id):
    # Initialize OpenStack connection
    conn = connection.Connection(cloud=cloud_name)
    
    try:
        # Get the instance
        server = conn.compute.get_server(instance_id)
        if not server:
            raise Exception(f"Instance {instance_id} not found")
            
        # Get the volume
        volume = conn.block_storage.find_volume(volume_id)
        if not volume:
            raise Exception(f"Volume {volume_id} not found")
            
        # Check if volume is already attached to this instance
        if volume.attachments:
            for attachment in volume.attachments:
                if attachment.get('server_id') == server.id:
                    # Volume is already attached to this instance, return success
                    return {
                        "device": attachment.get('device')
                    }
        
        # Attach volume to instance
        try:
            conn.compute.create_volume_attachment(server, volume_id=volume_id)
        except Exception as e:
            if "already attached" in str(e).lower():
                # If volume is already attached, get the device and return success
                volume = conn.block_storage.get_volume(volume_id)
                if volume.attachments:
                    return {
                        "device": volume.attachments[0].get('device')
                    }
            raise e
        
        # Wait for volume to be attached
        max_retries = 30
        retry_count = 0
        while retry_count < max_retries:
            volume = conn.block_storage.get_volume(volume_id)
            if volume.attachments and volume.attachments[0].get('server_id') == server.id:
                break
            time.sleep(2)
            retry_count += 1
            
        if retry_count == max_retries:
            raise Exception("Timeout waiting for volume attachment")
            
        # Get the device name from the attachment
        device = volume.attachments[0].get('device')
        if not device:
            raise Exception("No device name found in volume attachment")
            
        # Return the device name
        return {
            "device": device
        }
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: mount_volume.py <cloud_name> <instance_id> <volume_id>", file=sys.stderr)
        sys.exit(1)
        
    cloud_name = sys.argv[1]
    instance_id = sys.argv[2]
    volume_id = sys.argv[3]
    
    result = mount_volume(cloud_name, instance_id, volume_id)
    print(json.dumps(result)) 