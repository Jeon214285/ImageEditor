from ultralytics import YOLO
from app.config import LOCAL_MODEL_PATH

_model = None

def load_model():
    global _model
    if _model is None:
        _model = YOLO(LOCAL_MODEL_PATH)
    return