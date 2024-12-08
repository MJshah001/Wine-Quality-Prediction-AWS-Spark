#!/bin/bash

set -e # Exit on error

# Function to check if the previous command was successful
check_success() {
    if [ $? -ne 0 ]; then
        echo "Error: $1 failed."
        exit 1
    fi
}

# Function to add a line to ~/.bashrc only if it doesn't already exist
add_to_bashrc() {
    local LINE=$1
    grep -qxF "$LINE" ~/.bashrc || echo "$LINE" >> ~/.bashrc
}

# Update the system
echo "Updating the system..."
sudo apt update && sudo apt upgrade -y
check_success "System update"

# Install Java
echo "Installing Java..."
sudo apt install -y openjdk-11-jdk
check_success "Java installation"
java -version
check_success "Java verification"

# Install Python and pip
echo "Installing Python and pip..."
sudo apt install -y python3 python3-pip
check_success "Python and pip installation"
python3 --version
check_success "Python verification"
pip3 --version
check_success "pip verification"

# Install NumPy
echo "Installing Numpy..."
pip3 install numpy --break-system-packages
check_success "NumPy installation"

# Install Spark
echo "Installing Apache Spark..."
wget https://dlcdn.apache.org/spark/spark-3.5.3/spark-3.5.3-bin-hadoop3.tgz
check_success "Spark download"
tar -xzf spark-3.5.3-bin-hadoop3.tgz
check_success "Spark extraction"
mv spark-3.5.3-bin-hadoop3 spark
check_success "Spark directory setup"

# Configure Spark environment
echo "Configuring Spark environment variables..."
add_to_bashrc "export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64"
add_to_bashrc "export SPARK_HOME=~/spark"
add_to_bashrc "export PATH=\$SPARK_HOME/bin:\$SPARK_HOME/sbin:\$PATH"

# Apply environment changes
echo "Applying environment changes..."
source ~/.bashrc
source ~/.bashrc # Sourcing twice to ensure proper propagation
check_success "Environment variables applied"

# Verify Spark installation
echo "Verifying Spark installation..."
spark-shell --version
check_success "Spark verification"

# Add S3A Connector
echo "Adding S3A Connector..."
wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.2.0/hadoop-aws-3.2.0.jar
check_success "hadoop-aws.jar download"
wget https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.11.375/aws-java-sdk-bundle-1.11.375.jar
check_success "aws-java-sdk-bundle.jar download"
mkdir -p ~/spark/jars
mv aws-java-sdk-bundle-1.11.375.jar hadoop-aws-3.2.0.jar ~/spark/jars
check_success "S3A Connector installation"

# Cleanup downloaded files
echo "Cleaning up..."
rm -f spark-3.5.3-bin-hadoop3.tgz
check_success "Cleanup of Spark archive"

echo "Setup completed successfully. You can now run your PySpark application."
