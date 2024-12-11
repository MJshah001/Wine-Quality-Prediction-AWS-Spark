# CS 643 Programming Assignment 2: Wine Quality Prediction in AWS

## Overview
This project demonstrates how to develop a parallel machine learning (ML) application using Apache Spark on AWS. It includes:
1. Parallel training of a wine quality prediction model using Spark MLlib across multiple EC2 instances.
2. A prediction application that evaluates wine quality, with and without Docker.
3. Deployment of the prediction model using Docker for portability.

## GitHub Repository
- [GitHub Repository Link](https://github.com/MJshah001/cs643-851-pa2-mjs283)

## DockerHub Repository
- [DockerHub Repository Link](https://hub.docker.com/r/mjshah001/wine-quality-prediction)


---

## Features
- **Parallel Model Training:** Trains the model in parallel across 4 EC2 instances using Apache Spark.
- **Prediction Application:** Predicts wine quality on a single EC2 instance using the trained model.
- **Docker Integration:** Containerizes the prediction application for seamless deployment.
- **Performance Evaluation:** Outputs the F1 score to evaluate the prediction accuracy.

---

## Architecture
### Components
1. **S3 Bucket:** 
   - Stores datasets, scripts, and the trained model.
   - Folder structure:
     ```
     winequalitydata/
     ├── train/
     │   └── TrainDataset.csv
     ├── validation/
     │   └── ValidationDataset.csv
     ├── test/
     │   └── TestDataset.csv
     ├── scripts/
     │   └── install_boto3.sh
     └── output/
         └── model/ (Saved trained models)
     ```

2. **EMR Cluster for Training:**
   - **Configuration:**
     - EMR Version: `emr-5.36.0`
     - Installed Applications: Hadoop 2.10.1, Spark 2.4.8, Zeppelin 0.10.0
     - Cluster Capacity: 1 Primary + 4 Core Nodes
   - Bootstrap Script: `install_boto3.sh` (from S3 `scripts/` folder)
   - IAM Roles:
     - Service Role: `EMR_DefaultRole`
     - Instance Profile: `EMR_EC2_DefaultRole`

3. **EC2 Instance for Prediction:** 
   - Used for both Docker-based and non-Docker-based prediction applications.

---

## Setup Instructions

### Step 1: S3 Bucket Configuration
1. Create an S3 bucket named `winequalitydata`.
2. Upload the datasets:
   - `TrainDataset.csv` → `train/`
   - `ValidationDataset.csv` → `validation/`
   - `TestDataset.csv` → `test/`
3. Upload the bootstrap script (`install_boto3.sh`) to the `scripts/` folder.

---

### Step 2: Model Training in parallel
1. **Create an EMR Cluster:**
   - Follow the above EMR configuration.
2. **Train the Model:**
   - SSH into the master node.
   - Create a script file `train_rf.py` and copy the training code into it.
   - Run the training job using:
     ```bash
     spark-submit --master yarn --deploy-mode cluster --executor-memory 10G --executor-cores 3 --num-executors 8 --driver-memory 6G --conf spark.yarn.executor.memoryOverhead=1G train_rf.py
     ```
   - The trained model will be saved in the `output/` folder in S3.

---

### Step 3: Prediction Without Docker

#### Option 1: Using `setup_spark_ec2.sh` Script

1. **Launch an EC2 Instance:**
   - AMI: `Ubuntu Server 24.04 LTS`
   - Instance Type: `t2.medium`

2. **Add Spark environment variables to `~/.bashrc`**:
     ```bash
     echo "export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64" >> ~/.bashrc
     echo "export SPARK_HOME=~/spark" >> ~/.bashrc
     echo "export PATH=\$SPARK_HOME/bin:\$SPARK_HOME/sbin:\$PATH" >> ~/.bashrc
     source ~/.bashrc
     ```

3. **Run Setup Script:**
   - Upload the `setup_spark_ec2.sh` script to your EC2 instance.
   - SSH into your EC2 instance and run the following commands to give execution permission and run the setup script:
     ```bash
     chmod +x setup_spark_ec2.sh
     ./setup_spark_ec2.sh
     ```

4. **Run Prediction:**
   - After the setup completes, create a file `app.py` and copy the prediction code into it. 
   - Create a `config.json` file with AWS credentials and S3 paths in `/app/config/config.json` directory.
      Replicate sample_config.json in this repository. Replicate sample_config.json in this repository (incase your `config.json` is in different directory or in home directory update the path in app.py in line 9 )
   - Run the prediction application:
     ```bash
     spark-submit --master local[*] --packages org.apache.hadoop:hadoop-aws:3.3.6 app.py
     ```
   - The F1 score will be displayed on the console.

---

#### Option 2: Manual Installation

If you prefer not to use the `setup_spark_ec2.sh` script, follow these steps to install Spark and dependencies manually:

1. **Launch an EC2 Instance:**
   - AMI: `Ubuntu Server 24.04 LTS`
   - Instance Type: `t2.medium`

2. **Install Java:**
   - Install OpenJDK 11:
     ```bash
     sudo apt update && sudo apt install -y openjdk-11-jdk
     java -version
     ```

3. **Install Python and pip:**
   - Install Python 3 and pip:
     ```bash
     sudo apt install -y python3 python3-pip
     python3 --version
     pip3 --version
     ```

4. **Install NumPy:**
   - Install NumPy:
     ```bash
     pip3 install numpy --break-system-packages
     ```

5. **Install Apache Spark:**
   - Download and install Apache Spark:
     ```bash
     wget https://dlcdn.apache.org/spark/spark-3.5.3/spark-3.5.3-bin-hadoop3.tgz
     tar -xzf spark-3.5.3-bin-hadoop3.tgz
     mv spark-3.5.3-bin-hadoop3 spark
     ```

6. **Configure Spark Environment:**
   - Add Spark environment variables to `~/.bashrc`:
     ```bash
     echo "export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64" >> ~/.bashrc
     echo "export SPARK_HOME=~/spark" >> ~/.bashrc
     echo "export PATH=\$SPARK_HOME/bin:\$SPARK_HOME/sbin:\$PATH" >> ~/.bashrc
     source ~/.bashrc
     ```

7. **Verify Spark Installation:**
   - Verify that Spark is installed:
     ```bash
     spark-shell --version
     ```

8. **Add S3A Connector:**
   - Download the necessary Hadoop AWS jars:
     ```bash
     wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.2.0/hadoop-aws-3.2.0.jar
     wget https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.11.375/aws-java-sdk-bundle-1.11.375.jar
     mkdir -p ~/spark/jars
     mv aws-java-sdk-bundle-1.11.375.jar hadoop-aws-3.2.0.jar ~/spark/jars
     ```

9. **Run Prediction:**
   - Create a file `app.py` and copy the prediction code into it.
   - Create a `config.json` file with AWS credentials and S3 paths in `/app/config/config.json` directory.
      Replicate sample_config.json in this repository (incase your `config.json` is in different directory or in home directory update the path in app.py in line 9 )
   - Run the prediction application:
     ```bash
     spark-submit --master local[*] --packages org.apache.hadoop:hadoop-aws:3.3.6 app.py
     ```
   - The F1 score will be displayed on the console.


---


### Step 4: Prediction with Docker

#### Option 1: Using `setup_docker.sh` Script

1. **Launch an EC2 Instance:**

   - AMI: `Amazon Linux 2`
   - Instance Type: `t2.medium`

2. **Run Docker Setup Script:**

   - Upload the `setup_docker.sh` script to your EC2 instance.
   - SSH into your EC2 instance and run the following commands to give execution permission and run the setup script:
     ```bash
     chmod +x setup_docker.sh

     ./setup_docker.sh
     ```
    - Log out and back in.

3. **Verify Docker Installation:**

   - Once the script completes, verify Docker is installed correctly by checking the version:
     ```bash
     docker --version
     ```

4. **Run Prediction:**

   - Create a `config.json` file with AWS credentials and S3 paths.
      Replicate sample_config.json in this repository
     
    - Run the container:
     ```bash
     docker run --rm -v /home/ec2-user/config.json:/app/config/config.json mjshah001/wine-quality-prediction:latest
     ```
   - The F1 score will be displayed in the container's logs.

---

#### Option 2: Manual Installation

If you prefer not to use the `setup_docker.sh` script, follow these steps to install Docker manually:

1. **Launch an EC2 Instance:**

   - AMI: `Amazon Linux 2`
   - Instance Type: `t2.medium`

2. **Update the System and Install Dependencies:**

   - Update the package list:
     ```bash
     sudo yum update -y
     ```
   - Install the required dependencies:
     ```bash
     sudo yum install -y yum-utils
     ```

3. **Install Docker:**

   - Add Docker's official repository and install Docker:
     ```bash
     sudo amazon-linux-extras install -y docker
     ```
   - Log out and back in, then start the Docker service:
     ```bash
     sudo service docker start
     docker login
   

4. **Start Docker Service:**

   - Start the Docker service:
     ```bash
     sudo service docker start
     ```

5. **Enable Docker to Start on Boot:**

   - Enable Docker to start automatically when the system boots:
     ```bash
     sudo systemctl enable docker
     ```

6. **Add User to Docker Group:**

   - Add the `ec2-user` to the Docker group so you don't need to use `sudo` for Docker commands:
     ```bash
     sudo usermod -aG docker ec2-user
     ```
   - Log out and back in.

7. **Verify Docker Installation:**

   - Verify Docker is installed correctly by checking the version:
     ```bash
     docker --version
     ```

8. **Run Prediction:**

   - Create a `config.json` file with AWS credentials and S3 paths.
      Replicate sample_config.json in this repository
   - Run the container:
     ```bash
     docker run --rm -v /home/ec2-user/config.json:/app/config/config.json mjshah001/wine-quality-prediction:latest
     ```
   - The F1 score will be displayed in the container's logs.

---
