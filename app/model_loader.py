from ultralytics import YOLO
from app.config import (
    MLFLOW_TRACKING_URI,
    FACE_CHAMPION_MODEL_URI, FACE_CHALLENGER_MODEL_URI,
    PLATE_CHAMPION_MODEL_URI, PLATE_CHALLENGER_MODEL_URI,
    CANARY_ENABLED, CANARY_RATIO
)
import random
import mlflow

_face_champion_model = None
_face_challenger_model = None
_plate_champion_model = None
_plate_challenger_model = None

def load_face_champion_model():
    global _face_champion_model
    if _face_champion_model is not None:
        return _face_champion_model
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    weight_path = mlflow.artifacts.download_artifacts(
        artifact_uri=FACE_CHAMPION_MODEL_URI+"/artifacts/best.pt"
    )
    _face_champion_model = YOLO(weight_path)
    return _face_champion_model

def load_face_challenger_model():
    global _face_challenger_model
    if _face_challenger_model is not None:
        return _face_challenger_model
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    weight_path = mlflow.artifacts.download_artifacts(
        artifact_uri=FACE_CHALLENGER_MODEL_URI+"/artifacts/best.pt"
    )
    _face_challenger_model = YOLO(weight_path)
    return _face_challenger_model

def load_plate_champion_model():
    global _plate_champion_model
    if _plate_champion_model is not None:
        return _plate_champion_model
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    weight_path = mlflow.artifacts.download_artifacts(
        artifact_uri=PLATE_CHAMPION_MODEL_URI+"/artifacts/best.pt"
    )
    _plate_champion_model = YOLO(weight_path)
    return _plate_champion_model

def load_plate_challenger_model():
    global _plate_challenger_model
    if _plate_challenger_model is not None:
        return _plate_challenger_model
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    weight_path = mlflow.artifacts.download_artifacts(
        artifact_uri=PLATE_CHALLENGER_MODEL_URI+"/artifacts/best.pt"
    )
    _plate_challenger_model = YOLO(weight_path)
    return _plate_challenger_model

def select_serving_model():
    if CANARY_ENABLED and random.random() < CANARY_RATIO:
        return "challenger"
    return "champion"