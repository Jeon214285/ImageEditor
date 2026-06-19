import os

# LOCAL_MODEL_PATH = "ml/runs/face_detector/weights/best.pt"
# MLFLOW_TRACKING_URI = "sqlite:///ml/mlflow.db"
MLFLOW_TRACKING_URI = "https://skinning-outburst-storm.ngrok-free.dev"
FACE_MODEL_URI = "models:/face-detector@champion"
PLATE_MODEL_URI = "models:/plate-detector@champion"
CANARY_ENABLED = True
CANARY_RATIO = 0.1
FACE_CHAMPION_MODEL_URI = "models:/face-detector@champion"
FACE_CHALLENGER_MODEL_URI = "models:/face-detector@challenger"
PLATE_CHAMPION_MODEL_URI = "models:/plate-detector@champion"
PLATE_CHALLENGER_MODEL_URI = "models:/plate-detector@challenger"

LOW_CONFIDENCE_THRESHOLD = 0.70
LOW_CONFIDENCE_LIMIT = 5