<img width="910" alt="image" src="https://github.com/user-attachments/assets/da8dfd28-0912-48d1-940b-805b5ea7d541"># PostgreSQL Deployment API

This API automates the setup of a PostgreSQL primary-read-replica architecture on AWS using **Terraform** and **Ansible**. It accepts configurable parameters to generate the required infrastructure (EC2 instances, security groups) and configure PostgreSQL replication between the primary and replica instances.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setup and Installation](#setup-and-installation)
3. [API Endpoints](#api-endpoints)
    - [Generate Terraform and Ansible Code](#generate-terraform-and-ansible-code)
    - [Apply Infrastructure](#apply-infrastructure)
    - [Configure PostgreSQL](#configure-postgresql)
    - [Create Inventory](#create-inventory)
    - [Health Check](#health-check)
4. [Example Requests](#example-requests)
5. [Error Handling](#error-handling)
6. [Future Use Cases](#future-use-cases)
7. [Assumptions](#assumptions)
8. [Contributing](#contributing)

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
    "postgresql_version": "13",
    "instance_type": "t2.medium",
    "num_replicas": 2,
    "max_connections": "200",
    "shared_buffers": "256MB"
}
```
<img width="1470" alt="image" src="https://github.com/user-attachments/assets/b0942d7a-5fbb-4373-a80e-cf07c3043b2e">


