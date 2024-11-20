from flask import Flask, request, jsonify
import subprocess
import os
import textwrap
import json

app = Flask(__name__)

# Generate the Terraform and Ansible code and save them to files
@app.route('/generate-code', methods=['POST'])
def generate_code():
    params = request.get_json()

    # Generate the Terraform and Ansible code
    terraform_code = generate_terraform_code(params)
    ansible_playbook = generate_ansible_playbook(params)

    # Save the generated code to files
    save_to_file('terraform.tf', terraform_code)
    save_to_file('postgresql_playbook.yml', ansible_playbook)

    # Return the generated code in the response
    return jsonify({
        'message': 'Terraform and Ansible code generated successfully',
        'terraform_code': terraform_code,
        'ansible_playbook': ansible_playbook
    }), 200

# Function to save generated code to a file
def save_to_file(filename, content):
    with open(filename, 'w') as f:
        f.write(content)

# Function to generate Terraform code
def generate_terraform_code(params):
    terraform_code = textwrap.dedent(f"""
    provider "aws" {{
        region = "us-west-2"
    }}

    variable "vpc_id" {{
        default = "vpc-088e27c25dc5bdb09"
    }}

    variable "subnet_id" {{
        default = "subnet-08608834300b6a90d"  # Your existing Subnet ID
    }}

    resource "aws_security_group" "all_open_sg" {{
        name        = "all-open-sg"
        description = "Security Group that allows all inbound and outbound traffic"
        vpc_id      = var.vpc_id

        # Allow all inbound traffic
        ingress {{
            from_port   = 0
            to_port     = 65535
            protocol    = "tcp"
            cidr_blocks = ["0.0.0.0/0"]
        }}

        # Allow all outbound traffic
        egress {{
            from_port   = 0
            to_port     = 65535
            protocol    = "tcp"
            cidr_blocks = ["0.0.0.0/0"]
        }}
    }}

    resource "aws_instance" "primary_postgresql" {{
        ami                  = "ami-0b8c6b923777519db"  # Your AMI ID
        instance_type        = "{params['instance_type']}"  # Interpolate dynamic value
        subnet_id            = var.subnet_id
        vpc_security_group_ids = [aws_security_group.all_open_sg.id]
        key_name             = "ubuntu-key"
        tags = {{
            Name = "Primary PostgreSQL"
        }}
    }}

    resource "aws_instance" "replica_postgresql" {{
        count                = "{params['num_replicas']}"
        ami                  = "ami-0b8c6b923777519db"  # Your AMI ID
        instance_type        = "{params['instance_type']}"  # Interpolate dynamic value
        subnet_id            = var.subnet_id
        vpc_security_group_ids = [aws_security_group.all_open_sg.id]
        key_name             = "ubuntu-key"
        tags = {{
            Name = "Replica PostgreSQL"
        }}
    }}

    output "primary_postgresql_ip" {{
        value       = aws_instance.primary_postgresql.public_ip
        description = "IP address of the primary PostgreSQL EC2 instance"
    }}

    output "replica_postgresql_ips" {{
        value = [for r in aws_instance.replica_postgresql : r.public_ip]
        description = "IP addresses of the replica PostgreSQL EC2 instances"
    }}
    """)

    return terraform_code

# Function to generate Ansible playbook code
def generate_ansible_playbook(params):
    ansible_playbook = textwrap.dedent(f"""
    ---
    - name: Install PostgreSQL
      hosts: all
      become: yes
      vars:
        version: "{params.get('postgresql_version', '17')}"
        max_connections: "{params.get('max_connections', '100')}"
      tasks:
        - name: Remove the old PostgreSQL repository list file
          file:
            path: /etc/apt/sources.list.d/pgdg.list
            state: absent

        - name: Update apt repositories
          apt:
            update_cache: yes

        - name: Install required packages (wget and ca-certificates)
          apt:
            name:
              - wget
              - ca-certificates
            state: present

        - name: Add the PostgreSQL GPG key
          apt_key:
            url: https://www.postgresql.org/media/keys/ACCC4CF8.asc
            state: present

        - name: Add the PostgreSQL APT repository to sources list
          shell: echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" | tee -a /etc/apt/sources.list.d/pgdg.list
          args:
            creates: /etc/apt/sources.list.d/pgdg.list

        - name: Update apt repositories after adding PostgreSQL repo
          apt:
            update_cache: yes

        - name: Install PostgreSQL and its contrib package
          apt:
            name:
              - postgresql-{{{{ version }}}}
              - postgresql-contrib-{{{{ version }}}}
            state: present
        
        - name: Ensure postgresql.conf is configured with max_connections
          lineinfile:
            path: "/etc/postgresql/{{{{ version }}}}/main/postgresql.conf"
            regexp: '^#?max_connections ='
            line: "max_connections = {{{{ max_connections }}}}"
        
        - name: Restart PostgreSQL service if max_connections was changed
          service:
            name: postgresql
            state: restarted                                   
    """)

    return ansible_playbook

# Function to create hosts.ini inventory file
@app.route('/create-inventory', methods=['POST'])
def create_inventory():
    params = request.get_json()
    key_path = params.get('key-path')
    user = params.get('user')

    if not key_path or not user:
        return jsonify({'error': 'key-path and user are required'}), 400

    try:
        # Get Terraform output (assumes 'terraform output' returns JSON)
        terraform_output = subprocess.check_output(["terraform", "output", "-json"])
        terraform_output = json.loads(terraform_output)

        primary_ip = terraform_output['primary_postgresql_ip']['value']
        replica_ips = terraform_output['replica_postgresql_ips']['value']

        # Generate the hosts.ini content
        inventory_content = generate_inventory_content(primary_ip, replica_ips, key_path, user)

        # Save to hosts.ini file
        save_to_file('hosts.ini', inventory_content)

        return jsonify({'message': 'Inventory file created successfully'}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e), 'message': 'Error retrieving Terraform output'}), 500

# Function to generate hosts.ini file content
def generate_inventory_content(primary_ip, replica_ips, key_path, user):
    # Create the primary section with the main PostgreSQL instance IP
    inventory = f"""
[primary]
{primary_ip} ansible_ssh_user={user} ansible_ssh_private_key_file={key_path}
"""
    
    # Add the replica section with multiple IPs
    inventory += "[replica]\n"
    for ip in replica_ips:
        inventory += f"{ip} ansible_ssh_user={user} ansible_ssh_private_key_file={key_path}\n"

    return inventory

# Apply infrastructure using Terraform
@app.route('/apply-infrastructure', methods=['POST'])
def apply_infrastructure():
    try:
        subprocess.check_call(["terraform", "init"])
        subprocess.check_call(["terraform", "plan"])
        subprocess.check_call(["terraform", "apply", "-auto-approve"])
        return jsonify({'message': 'Terraform infrastructure applied successfully'}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e), 'message': 'Error while applying Terraform infrastructure'}), 500

# Configure PostgreSQL using Ansible
@app.route('/configure-postgresql', methods=['POST'])
def configure_postgresql():
    try:
        # Ensure that the 'hosts.ini' file exists in the current directory
        if not os.path.exists('hosts.ini'):
            return jsonify({'error': 'hosts.ini file not found, please ensure it exists'}), 400

        # Run the ansible-playbook command
        subprocess.check_call(["ansible-playbook", "-i", "hosts.ini", "postgresql_playbook.yml"])
        return jsonify({'message': 'PostgreSQL configuration applied successfully'}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e), 'message': 'Error while configuring PostgreSQL'}), 500

# Health check route to ensure the server is up and running
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True)
