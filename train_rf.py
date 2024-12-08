from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from datetime import datetime

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

# Assemble features, dropping 'residual sugar' and 'free sulfur dioxide'
columns_to_drop = ["residual sugar", "free sulfur dioxide"]
feature_columns = [col for col in train_df.columns[:-1] if col not in columns_to_drop]
label_column = train_df.columns[-1]  # The last column

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

# Define evaluators
f1_evaluator = MulticlassClassificationEvaluator(labelCol=label_column, predictionCol="prediction", metricName="f1")
accuracy_evaluator = MulticlassClassificationEvaluator(labelCol=label_column, predictionCol="prediction", metricName="accuracy")

# Set up cross-validation
crossval = CrossValidator(estimator=rf,
                          estimatorParamMaps=param_grid,
                          evaluator=f1_evaluator,
                          numFolds=5)  # 5-fold cross-validation

# Train the model with cross-validation
cv_model = crossval.fit(train_df)

# Save the best model to S3
cv_model.bestModel.write().overwrite().save(output_model_path)


print(f"Best model saved to: {output_model_path}")

# Stop SparkSession
spark.stop()
