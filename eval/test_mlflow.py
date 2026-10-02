import mlflow

print("Tracking URI:", mlflow.get_tracking_uri())

with mlflow.start_run():
    mlflow.log_param("test_param", "hello")
    mlflow.log_metric("test_metric", 1.0)

print("Done.")