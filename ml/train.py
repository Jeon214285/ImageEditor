import os
from pathlib import Path
from ultralytics import YOLO, settings
from split_data import split_data
from app.config import MODEL_URI, MLFLOW_TRACKING_URI
import mlflow

class YOLOModelWrapper(mlflow.pyfunc.PythonModel):
    pass

BASE_DIR = os.path.dirname(__file__)
YAML_PATH = os.path.join(BASE_DIR, "data.yaml")
PROJECT_DIR = os.path.join(BASE_DIR, "runs") 

experiment_name = "face_detector-local"

os.chdir(BASE_DIR)  # ml 폴더에 학습 결과를 저장하기 위함

# 환경변수와 MLflow에 절대 경로 URI 주입
os.environ["MLFLOW_TRACKING_URI"] = MLFLOW_TRACKING_URI
os.environ["MLFLOW_EXPERIMENT_NAME"] = experiment_name
settings.update({"mlflow": True})

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(experiment_name)

# dataset: https://www.kaggle.com/datasets/lylmsc/wider-face-for-yolo-training
split_data() # 데이터 준비

try:
    weight_path = mlflow.artifacts.download_artifacts(
        artifact_uri="models:/face-detector@challenger/artifacts/last.pt"
    )
    is_resume = True
    print("INFO: LOADED last.pt")
except:
    weight_path = "yolo26n.pt"
    is_resume = False
    print("INFO: LOADED yolo26n.pt")

model = YOLO(weight_path)

with mlflow.start_run() as run:
    results = model.train(
        resume=is_resume,
        data=YAML_PATH,
        epochs=10,
        imgsz=640,
        batch=16,
        project=PROJECT_DIR,
        name="face_detector",
        exist_ok=True,
        device=0,
        workers=0
    )

    best_model_path = os.path.join(PROJECT_DIR, "face_detector", "weights", "best.pt")
    last_model_path = os.path.join(PROJECT_DIR, "face_detector", "weights", "last.pt")
    print(f"Model saved to: {best_model_path}")

    # 모델 저장 (best & last)
    best_model_info = mlflow.pyfunc.log_model(
        name="best_model",
        python_model=YOLOModelWrapper(),
        artifacts={"best.pt": best_model_path},
        registered_model_name='face-detector'
    )

    # 추후 이어서 학습하기 위해서 저장
    last_model_info = mlflow.pyfunc.log_model(
        name="last_model",
        python_model=YOLOModelWrapper(),
        artifact_path={"last.pt": last_model_path},
        registered_model_name='face-detector'
    )

    # mlflow.log_artifact(best_model_path, artifact_path="weights")  # artifact 저장  # 중복 저장을 방지하여 사용X