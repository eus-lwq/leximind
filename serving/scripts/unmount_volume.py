#!/usr/bin/env python3

import os
import sys
import json
import openstack
import time
from openstack import connection

def unmount_volume(cloud_name, instance_id, volume_id):
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
            
        # Check if volume is attached
        if not volume.attachments:
            return {"status": "not_attached"}
            
        # Find the attachment for this instance
        attachment = None
        for att in volume.attachments:
            if att.get('server_id') == server.id:
                attachment = att
                break
                
        if not attachment:
            return {"status": "not_attached_to_instance"}
            
        # Detach volume from instance
        conn.compute.delete_volume_attachment(attachment['id'], server)
        
        # Wait for volume to be detached
        max_retries = 30
        retry_count = 0
        while retry_count < max_retries:
            volume = conn.block_storage.get_volume(volume_id)
            if not volume.attachments:
                break
            time.sleep(2)
            retry_count += 1
            
        if retry_count == max_retries:
            raise Exception("Timeout waiting for volume detachment")
            
        return {
            "status": "detached",
            "volume_id": volume_id
        }
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: unmount_volume.py <cloud_name> <instance_id> <volume_id>", file=sys.stderr)
        sys.exit(1)
        
    cloud_name = sys.argv[1]
    instance_id = sys.argv[2]
    volume_id = sys.argv[3]
    
    result = unmount_volume(cloud_name, instance_id, volume_id)
    print(json.dumps(result)) 