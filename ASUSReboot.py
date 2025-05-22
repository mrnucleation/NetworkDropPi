import paramiko
import json
import logging

#========================================================================    
def load_config(json_path):
    # Load the JSON configuration file
    with open(json_path, 'r') as f:
        config = json.load(f)
    return config
#========================================================================    
def reboot_router(json_input):
    hostname = json_input['hostname']
    username = json_input['username']
    password = json_input['password']

    print(f"Rebooting router at {hostname}...")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        logging.info(f"Connecting to {hostname}...")
        client.connect(hostname, username=username, password=password, timeout=2)
        stdin, stdout, stderr = client.exec_command("reboot")
        logging.info("Reboot command sent.")
        logging.info(stdout.read().decode())
        logging.info(stderr.read().decode())
    finally:
        client.close()
#========================================================================