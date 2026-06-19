import os
import pathlib
import time
import mlflow
from mlflow.tracking import MlflowClient
from ultralytics import YOLO, settings
from split_data import split_data
from model_promoter import promote_if_better

class YOLOModelWrapper(mlflow.pyfunc.PythonModel):
    pass

BASE_DIR = os.path.dirname(__file__)
FACE_YAML_PATH = os.path.join(BASE_DIR, "face_data.yaml")
PLATE_YAML_PATH = os.path.join(BASE_DIR, "plate_data.yaml")
PROJECT_DIR = os.path.join(BASE_DIR, "runs") 
# MLFLOW_TRACKING_URI = "sqlite:///mlflow.db"
MLFLOW_TRACKING_URI = "https://skinning-outburst-storm.ngrok-free.dev"

model_info = []
model_info.append({'model_name': 'face-detector', 'experiment_name': 'face_detector-server',
                   'artifact_uri': "models:/face-detector@challenger/artifacts/last.pt",
                   'yaml_path': FACE_YAML_PATH, 'model_path': 'face_detector'})
model_info.append({'model_name': 'plate-detector', 'experiment_name': 'plate_detector-server',
                   'artifact_uri': "models:/plate-detector@challenger/artifacts/last.pt",
                   'yaml_path': PLATE_YAML_PATH, 'model_path': 'plate_detector'})

split_data() # 데이터 준비

os.chdir(BASE_DIR)  # ml 폴더에 학습 결과를 저장하기 위함

client = MlflowClient()

for info in model_info:
    best_map = -1.0
    best_version = None
    new_map = -1.0
    experiment_name = info['experiment_name']

    # 환경변수와 MLflow에 절대 경로 URI 주입
    os.environ["MLFLOW_TRACKING_URI"] = MLFLOW_TRACKING_URI
    os.environ["MLFLOW_EXPERIMENT_NAME"] = experiment_name
    settings.update({"mlflow": False})  # YOLO 내부에서 run을 강제 종료하는 것을 방지

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_registry_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(experiment_name)

    # dataset: https://www.kaggle.com/datasets/lylmsc/wider-face-for-yolo-training
    #          https://www.kaggle.com/datasets/fareselmenshawii/license-plate-dataset
    try:
        weight_path = mlflow.artifacts.download_artifacts(
            artifact_uri=info['artifact_uri']
        )
        is_resume = True
        print("INFO: LOADED last.pt")
    except Exception as e:
        weight_path = "yolo26n.pt"
        is_resume = False
        print(f"INFO: LOADED yolo26n.pt | EXCEPTION={e}")

    model = YOLO(weight_path)

    with mlflow.start_run() as run:
        results = model.train(
            resume=is_resume,
            data=info['yaml_path'],
            epochs=5,
            imgsz=640,
            batch=16,
            project=PROJECT_DIR,
            name=info['model_path'],
            exist_ok=True,
            device=0,
            workers=0
        )

        # 학습 기록 저장
        if hasattr(results, 'results_dict'):
            sanitized_metrics = {}
            for key, value in results.results_dict.items():
                # 괄호 '(' 를 '_'로 바꾸고, ')'는 없애기
                safe_key = key.replace('(', '_').replace(')', '')
                sanitized_metrics[safe_key] = value
            new_map = sanitized_metrics.get('metrics/mAP50-95_B', -1.0)
            mlflow.log_metrics(sanitized_metrics)
            print("INFO: MLflow에 지표(Metrics) 기록 완료")
            
        best_model_path = os.path.join(PROJECT_DIR, info['model_path'], "weights", "best.pt")
        last_model_path = os.path.join(PROJECT_DIR, info['model_path'], "weights", "last.pt")
        print(f"Model saved to: {best_model_path}")

        best_model_uri = pathlib.Path(best_model_path).resolve().as_uri()
        last_model_uri = pathlib.Path(last_model_path).resolve().as_uri()

        # 모델 저장 (best & last)
        logged_model = mlflow.pyfunc.log_model(
            name=info['model_name'],
            python_model=YOLOModelWrapper(),
            artifacts={"best.pt": best_model_uri, "last.pt": last_model_uri},
            registered_model_name=info['model_name']
        )

        print(f"Wait 60 seconds")
        time.sleep(60)  # 60초 대기

        latest_version = int(logged_model.registered_model_version)

        client.set_registered_model_alias(
            name=info['model_name'],
            alias='challenger',
            version=str(latest_version)
        )

        if new_map > best_map:
            best_map = new_map
            best_version = latest_version

        if best_version is not None:
            promote_if_better(best_version, best_map, model_name=info['model_name'])

        # mlflow.log_artifact(best_model_path, artifact_path="weights")  # artifact 저장  # 중복 저장을 방지하여 사용X