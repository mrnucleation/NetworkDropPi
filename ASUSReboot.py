import paramiko
import yaml
import logging

#========================================================================    
def load_config(yaml_path):
    # Load the YAML configuration file
    with open(yaml_path, 'r') as file:
        config = yaml.safe_load(file)
    return config
#========================================================================    
def reboot_router(yaml_input):
    hostname = yaml_input['hostname']
    username = yaml_input['username']
    password = yaml_input['password']

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hostname, username=username, password=password)
        stdin, stdout, stderr = client.exec_command("reboot")
        logging.info("Reboot command sent.")
        logging.info(stdout.read().decode())
        logging.info(stderr.read().decode())
    finally:
        client.close()
#========================================================================