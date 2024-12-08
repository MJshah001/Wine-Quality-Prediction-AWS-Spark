from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
import boto3
from datetime import datetime
import os



# Initialize SparkSession
spark = SparkSession.builder \
    .appName("WineQualityModelTraining_HyperparameterTuning") \
    .getOrCreate()

# Generate a unique timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Define S3 paths
train_path = "s3a://winequalitydata/train/TrainingDataset.csv"
validation_path = "s3a://winequalitydata/validation/ValidationDataset.csv"
output_model_path = "s3a://winequalitydata/outputs/WineQualityRandomForestModel"
metrics_output_path = f"/tmp/metrics_{timestamp}.txt"
s3_bucket = "winequalitydata"
s3_metrics_path = f"outputs/metrics_{timestamp}.txt"


# Helper function to clean column names
def clean_columns(df):
    """
    Cleans column names by removing extra quotes, leading/trailing spaces, 
    and standardizes the names.
    """
    cleaned_columns = [col(c).alias(c.strip().replace('"', '').lower()) for c in df.columns]
    return df.select(cleaned_columns)

# Load datasets and clean column names
train_df = spark.read.options(header='true', inferSchema='true', sep=';').csv(train_path)
train_df = clean_columns(train_df)

validation_df = spark.read.options(header='true', inferSchema='true', sep=';').csv(validation_path)
validation_df = clean_columns(validation_df)

# Assemble features
feature_columns = train_df.columns[:-1]  # All columns except the last one
label_column = train_df.columns[-1]      # The last column

assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")
train_df = assembler.transform(train_df).select("features", label_column)
validation_df = assembler.transform(validation_df).select("features", label_column)

# Define a Random Forest classifier
rf = RandomForestClassifier(featuresCol="features", labelCol=label_column)

# Build a parameter grid for hyperparameter tuning
param_grid = ParamGridBuilder() \
    .addGrid(rf.numTrees, [50, 100, 200]) \
    .addGrid(rf.maxDepth, [5, 10, 15]) \
    .build()

# Define an evaluator for F1 score
evaluator = MulticlassClassificationEvaluator(labelCol=label_column, predictionCol="prediction", metricName="f1")

# Set up cross-validation
crossval = CrossValidator(estimator=rf,
                          estimatorParamMaps=param_grid,
                          evaluator=evaluator,
                          numFolds=3)  # 3-fold cross-validation

# Train the model with cross-validation
cv_model = crossval.fit(train_df)

# Save the best model to S3
cv_model.bestModel.write().overwrite().save(output_model_path)

# Evaluate the best model on the validation dataset
predictions = cv_model.bestModel.transform(validation_df)
f1_score = evaluator.evaluate(predictions)


# Extract the best hyperparameters 
best_model_params = cv_model.bestModel.extractParamMap()
best_params = {}

# Map the parameters to readable key-value pairs
for param, value in best_model_params.items():
    param_name = param.name  
    if "RandomForestClassifier" in str(param):  # Only keep RF params
        best_params[param_name] = value

# Write metrics to a local file
with open(metrics_output_path, "w") as f:
    f.write("\nBest Hyperparameters:\n")
    for param, value in best_params.items():
        f.write(f"{param}: {value}\n")

# Upload metrics file to S3
s3_client = boto3.client('s3')
s3_client.upload_file(metrics_output_path, s3_bucket, s3_metrics_path)

print(f"Best model saved to: {output_model_path}")
print(f"F1 Score: {f1_score}")
print(f"Metrics uploaded to: s3://{s3_bucket}/{s3_metrics_path}")

# Stop SparkSession
spark.stop()
