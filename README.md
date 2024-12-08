# CS 643 Programming Assignment 2: Wine Quality Prediction in AWS

## Overview
This project demonstrates how to develop a parallel machine learning (ML) application using Apache Spark on AWS. It includes:
1. Parallel training of a wine quality prediction model using Spark MLlib across multiple EC2 instances.
2. A prediction application that evaluates wine quality, with and without Docker.
3. Deployment of the prediction model using Docker for portability.

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

### Step 2: Model Training
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
1. **Launch an EC2 Instance:**
   - AMI: `Ubuntu Server 24.04 LTS`
   - Instance Type: `t2.medium`
2. **Install Spark:**
   - Create a `setup_spark_ec2.sh` script with the installation commands.
   - Run the script:
     ```bash
     chmod +x setup_spark_ec2.sh
     ./setup_spark_ec2.sh
     ```
3. **Run Prediction:**
   - Create a file `app.py` and copy the prediction code into it.
   - Run the application:
     ```bash
     spark-submit --master local[*] --packages org.apache.hadoop:hadoop-aws:3.3.6 app.py
     ```
   - The F1 score will be displayed on the console.

---

### Step 4: Prediction With Docker
 **Docker Hub:**  
   - [Docker Image](https://hub.docker.com/r/mjshah001/wine-quality-prediction) : https://hub.docker.com/r/mjshah001/wine-quality-prediction

1. **Set Up Docker:**
   - If Docker is not installed, use the `setup_docker.sh` script:
     ```bash
     chmod +x setup_docker.sh
     ./setup_docker.sh
     ```
   - Log out and back in, then start the Docker service:
     ```bash
     sudo service docker start
     docker login
     ```
2. **Run Dockerized Application:**
   - Pull the Docker image:
     ```bash
     docker pull mjshah001/wine-quality-prediction:latest
     ```
   - Create a `config.json` file with AWS credentials and S3 paths.
      Replicate sample_config.json in this repository
   - Run the container:
     ```bash
     docker run --rm -v /home/ec2-user/config.json:/app/config/config.json mjshah001/wine-quality-prediction:latest
     ```

---
