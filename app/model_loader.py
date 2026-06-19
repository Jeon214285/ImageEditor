from ultralytics import YOLO
from app.config import FACE_MODEL_URI, PLATE_MODEL_URI, MLFLOW_TRACKING_URI
import mlflow

_face_model = None
_plate_model = None

def load_face_model():
    global _face_model

    if _face_model is not None:
        return _face_model
    
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    weight_path = mlflow.artifacts.download_artifacts(
        artifact_uri=FACE_MODEL_URI+"/artifacts/best.pt"
    )
    
    _face_model = YOLO(weight_path)

    return _face_model

def load_plate_model():
    global _plate_model

    if _plate_model is not None:
        return _plate_model
    
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    weight_path = mlflow.artifacts.download_artifacts(
        artifact_uri=PLATE_MODEL_URI+"/artifacts/best.pt"
    )
    
    _plate_model = YOLO(weight_path)

    return _plate_model