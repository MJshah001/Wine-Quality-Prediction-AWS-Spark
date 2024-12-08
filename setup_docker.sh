#!/bin/bash

# Update the package list
sudo yum update -y

# Install required dependencies
sudo yum install -y yum-utils

# Add Docker's official repository
sudo amazon-linux-extras install -y docker

# Start the Docker service
sudo service docker start

# Enable Docker to start on boot
sudo systemctl enable docker

# Add ec2-user to the docker group (no sudo required for Docker commands)
sudo usermod -aG docker ec2-user

# Verify the installation
docker --version

echo "Docker installation completed successfully!"
