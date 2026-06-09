import os
from pathlib import Path
from ultralytics import YOLO, settings
from split_data import split_data
import mlflow

BASE_DIR = os.path.dirname(__file__)
YAML_PATH = os.path.join(BASE_DIR, "data.yaml")

experiment_name = "face_detector-local"

os.chdir(BASE_DIR)  # ml 폴더에 학습 결과를 저장하기 위함

# 환경변수와 MLflow에 절대 경로 URI 주입
os.environ["MLFLOW_TRACKING_URI"] = "sqlite:///mlflow.db"
os.environ["MLFLOW_EXPERIMENT_NAME"] = experiment_name
settings.update({"mlflow": True})

mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment(experiment_name)

# dataset: https://www.kaggle.com/datasets/lylmsc/wider-face-for-yolo-training
split_data() # 데이터 준비

model = YOLO("yolo26n.pt")

results = model.train(
    data=YAML_PATH,
    epochs=1,
    imgsz=640,
    batch=16,
    project="runs",
    name="face_detector",
    exist_ok=True,
    device=0,
    workers=0
)

best_model_path = os.path.join(BASE_DIR, "runs", "face_detector", "weights", "best.pt")
print(f"Model saved to: {best_model_path}")