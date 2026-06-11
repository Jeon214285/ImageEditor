from ultralytics import YOLO
from app.config import MODEL_URI, MLFLOW_TRACKING_URI
import mlflow

_model = None

def load_model():
    global _model

    if _model is not None:
        return _model
    
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    weight_path = mlflow.artifacts.download_artifacts(
        artifact_uri=MODEL_URI+"/artifacts/best.pt"
    )
    
    _model = YOLO(weight_path)

    return _model