# Use an official Apache Spark image as the base
FROM bitnami/spark:3.5.3

# Set environment variables
ENV JAVA_HOME=/opt/bitnami/java
ENV SPARK_HOME=/opt/bitnami/spark
ENV PATH=$SPARK_HOME/bin:$SPARK_HOME/sbin:$PATH
ENV SPARK_JARS_DIR=$SPARK_HOME/jars

# Install Python and essential dependencies
USER root
RUN apt-get update && \
    apt-get install -y python3 python3-pip wget tar && \
    apt-get clean

# Install Python dependencies
COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Download Hadoop AWS and AWS SDK jars (for S3 support)
RUN mkdir -p $SPARK_JARS_DIR && \
    wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.6/hadoop-aws-3.3.6.jar -P $SPARK_JARS_DIR && \
    wget https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.526/aws-java-sdk-bundle-1.12.526.jar -P $SPARK_JARS_DIR

# Copy your application code into the container
WORKDIR /app
COPY app.py /app/

# Define a placeholder for config.json (to be mounted dynamically)
VOLUME /app/config

# Default command to run the application
CMD ["spark-submit", "--master", "local[*]", "--jars", "/opt/bitnami/spark/jars/hadoop-aws-3.3.6.jar,/opt/bitnami/spark/jars/aws-java-sdk-bundle-1.12.526.jar", "app.py"]
