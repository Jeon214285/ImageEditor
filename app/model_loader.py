from ultralytics import YOLO
from app.config import MODEL_URI, MLFLOW_TRACKING_URI
import mlflow

_model = None

def load_model():
    weight_path = mlflow.artifacts.download_artifacts(
        artifact_uri=MODEL_URI+"/artifacts/best.pt"
    )

    global _model
    if _model is None:
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        _model = YOLO(weight_path)
    return