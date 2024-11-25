This API automates the setup of a PostgreSQL primary-read-replica architecture on AWS using **Terraform** and **Ansible**. It accepts configurable parameters to generate the required infrastructure (EC2 instances, security groups) and configure PostgreSQL replication between the primary and replica instances.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setup and Installation](#setup-and-installation)
3. [API Endpoints](#api-endpoints)
4. [Example Requests](#example-requests)
5. [Future Use Cases](#future-use-cases)

## Prerequisites

Before using this API, ensure you have the following installed on your machine:

- **Python 3.8+**
  - Download and install Python: [Python Official Website](https://www.python.org/downloads/)
  
- **Flask**: Flask is a web framework used to create the API.
  - To install Flask, use:
    ```bash
    pip install flask
    ```

- **Terraform**: Terraform is used to provision infrastructure on AWS.
  - Download and install Terraform: [Terraform Official Website](https://www.terraform.io/downloads.html)

- **Ansible**: Ansible is used to configure PostgreSQL on the provisioned EC2 instances.
  - Install Ansible: [Ansible Installation Guide](https://docs.ansible.com/ansible/latest/installation_guide/index.html)

- **AWS CLI**: The AWS CLI is required to configure AWS credentials.
  - Install AWS CLI: [AWS CLI Installation](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
  - Set up your AWS credentials using:
    ```bash
    aws configure
    ```
## Setup and Installation

Follow these steps to set up and run the API:

1. **Clone the Repository**
   - Clone this repository to your local machine:
     ```bash
     git clone https://github.com/your-repo/postgresql-terraform-ansible-api.git
     cd postgresql-terraform-ansible-api
     ```
2. **Terraform Setup**
   - Modify the Terraform configuration (`terraform.tf`) to ensure the **VPC ID** and **Subnet ID** match your environment. These values are necessary to deploy EC2 instances correctly.
   - Update the AMI ID in the Terraform script to match the operating system you are using (default is Ubuntu).
   - Ensure that the Terraform script has the proper AWS credentials configured.

3. **Run the Flask Application**
   - Start the Flask API server:
     ```bash
     python app.py
     ```
   - The API will be running on `http://127.0.0.1:5000`.
     <img width="910" alt="image" src="https://github.com/user-attachments/assets/b16ad8ab-ab60-47f0-ba6d-9f934570e78c">

## API Endpoints

### 1. Generate Terraform and Ansible Code

**Endpoint:** `POST /generate-code`

This endpoint generates the Terraform and Ansible configuration code based on the parameters provided in the request body.

#### Request Body Example:
```json
{
    "postgresql_version": "17",
    "instance_type": "t2.medium",
    "num_replicas": 2,
    "max_connections": "200",
    "shared_buffers": "256MB"
}
```
#### Response:
```json
{
    "message": "Terraform and Ansible code generated successfully",
    "terraform_code": "Generated Terraform code here",
    "ansible_playbook": "Generated Ansible playbook here"
}
```
<img width="1470" alt="image" src="https://github.com/user-attachments/assets/b0942d7a-5fbb-4373-a80e-cf07c3043b2e">

### 2. Apply Infrastructure

**Endpoint:** `POST /apply-infrastructure`

This endpoint triggers Terraform to initialize and apply the infrastructure defined in the configuration files, provisioning EC2 instances, security groups, and other necessary resources.
This endpoint runs terraform init to initialize Terraform, followed by terraform plan and terraform apply to create the infrastructure based on the generated configuration files.

#### Request Body : None

#### Response:
```json
{
    "message": "Terraform infrastructure applied successfully"
}
```
<img width="752" alt="image" src="https://github.com/user-attachments/assets/8272be38-b3a1-40a0-8a7a-d99137f59891">

### 3. Genenrate Inventory

**Endpoint:** `POST /create-inventory`

This endpoint generates the Ansible inventory file (hosts.ini), which lists the IP addresses of the primary and replica PostgreSQL instances. Ansible uses this inventory to connect to the EC2 instances.
This endpoint uses the Terraform outputs (EC2 instance IPs) to generate an inventory file that Ansible can use to execute commands on the instances. The inventory contains information about the primary and replica nodes, as well as the SSH details for accessing them.

#### Request Body Example:
```json
{
    "key-path": "/path/to/your/private-key.pem",
    "user": "ubuntu"
}
```
#### Response:
```json
{
    "message": "Inventory file created successfully"
}
```
<img width="832" alt="image" src="https://github.com/user-attachments/assets/eda8a052-941b-4ae2-aafb-c19eaacc17bc">


### 4. Configure PostgreSQL
**Endpoint:** `POST /configure-postgresql`

This endpoint triggers Ansible to configure PostgreSQL on the EC2 instances that were provisioned by Terraform. It sets up replication between the primary PostgreSQL instance and its replicas.

#### Request Body : None

#### Response:
```json
{
    "message": "PostgreSQL configuration applied successfully"
}
```

## Example Requests
#### Generate Code:
```json
curl -X POST http://127.0.0.1:5000/generate-code \
  -H "Content-Type: application/json" \
  -d '{"postgresql_version": "17", "instance_type": "t2.medium", "num_replicas": 2, "max_connections": "200", "shared_buffers": "256MB"}'
```
#### Provision Infra or Apply Terraform:
```json
curl -X POST http://127.0.0.1:5000/apply-infrastructure
```
#### Generate Inventory:
```json
curl -X POST http://127.0.0.1:5000/create-inventory \
  -H "Content-Type: application/json" \
  -d '{"key-path": "/path/to/your/private-key.pem", "user": "ubuntu"}'
```
#### Configure PostgresSQL:
```json
curl -X POST http://127.0.0.1:5000/configure-postgresql
```

## Future Use Cases

The current implementation of this API focuses on automating the setup of PostgreSQL primary-read-replica architecture using **Terraform** and **Ansible**. However, there are several potential future use cases and features that can further enhance the API's capabilities.

### 1. Multi-Region Support

In the future, the API can be extended to support multi-region PostgreSQL deployments. This would allow users to provision primary and replica PostgreSQL instances across multiple AWS regions, improving availability, fault tolerance, and reducing latency for users in different geographical locations.

#### Possible Enhancements:
- Allow users to specify the desired AWS regions for the primary and replica instances.
- Implement cross-region replication to ensure that the replica instances can sync with the primary across regions.

### 2. Enhanced Security Features

Security is always a top priority in production environments. Future enhancements could include features that help automate secure setups, such as setting up proper IAM roles, managing database encryption.

#### Possible Enhancements:
- Implement automatic creation of IAM roles and policies to securely grant permissions to EC2 instances.
- Integrate the API with **AWS Secrets Manager** to securely manage PostgreSQL credentials and reduce the risk of exposed credentials in configuration files.

### 3. Scaling and Auto-Scaling

To handle varying workloads, future updates could include the ability to scale the PostgreSQL setup based on traffic patterns. Auto-scaling the number of replica instances based on load or performance metrics could significantly improve the API's usability for large-scale applications.

#### Possible Enhancements:
- Integrate **AWS Auto Scaling** for PostgreSQL replicas, automatically adding or removing replicas based on resource utilization.
- Integrate with **CloudWatch** or other monitoring tools to collect and analyze metrics like CPU, memory, and disk usage to trigger auto-scaling actions.

### 4. Backup and Disaster Recovery

Ensuring that the PostgreSQL setup has proper backup and disaster recovery mechanisms is crucial for production environments. Future versions of the API can integrate automated backups and a robust recovery process for the PostgreSQL instances.

#### Possible Enhancements:
- Automate the creation of **AWS RDS snapshots** or **PostgreSQL backups** at regular intervals.
- Implement backup strategies, such as daily, weekly, or on-demand backups, and allow the user to configure retention policies.
- Integrate **AWS S3** for backup storage and retrieval, ensuring that backups are safely stored and can be restored easily.




