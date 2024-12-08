import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import RandomForestClassificationModel
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

# Load configuration from the dynamically mounted file
with open('/app/config/config.json', 'r') as config_file:
    config = json.load(config_file)

# AWS Credentials
aws_access_key = config["aws"]["access_key"]
aws_secret_key = config["aws"]["secret_key"]
aws_session_token = config["aws"]["session_token"]

# S3 Paths
model_s3_path = config["s3_paths"]["model_path"]
test_data_s3_path = config["s3_paths"]["test_data_path"]

# Initialize SparkSession
spark = SparkSession.builder \
    .appName("WineQualityPrediction") \
    .getOrCreate()

# Set AWS credentials in Hadoop configuration for S3 access
spark._jsc.hadoopConfiguration().set("fs.s3a.access.key", aws_access_key)
spark._jsc.hadoopConfiguration().set("fs.s3a.secret.key", aws_secret_key)
spark._jsc.hadoopConfiguration().set("fs.s3a.session.token", aws_session_token)

# Load and process the test data
test_data = spark.read.options(header='true', inferSchema='true', sep=';').csv(test_data_s3_path)

def clean_columns(df):
    cleaned_columns = [col(c).alias(c.strip().replace('"', '').lower()) for c in df.columns]
    return df.select(cleaned_columns)

test_data = clean_columns(test_data)

# Prepare feature columns (excluding "residual sugar" and "free sulfur dioxide")
columns_to_drop = ["residual sugar", "free sulfur dioxide"]
feature_columns = [col for col in test_data.columns[:-1] if col not in columns_to_drop]
assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")
test_data = assembler.transform(test_data)

# Load model from S3 and make predictions
model = RandomForestClassificationModel.load(model_s3_path)
predictions = model.transform(test_data)

# Evaluate the model using F1 score
evaluator = MulticlassClassificationEvaluator(labelCol="quality", predictionCol="prediction", metricName="f1")
f1_score = evaluator.evaluate(predictions)

# Print the F1 score
print("\n\n")
print("*"*50)
print("\nModel Evaluation Results:")
print(f"F1 Score: {f1_score:.4f}")
print("\n")
print("*"*50)
print("\n\n")
# Stop the Spark session
spark.stop()