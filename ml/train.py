import os
from ultralytics import YOLO
from split_data import split_data

BASE_DIR = os.path.dirname(__file__)
YAML_PATH = os.path.join(BASE_DIR, "data.yaml")

os.chdir(BASE_DIR)

# dataset: https://www.kaggle.com/datasets/lylmsc/wider-face-for-yolo-training
split_data() # 데이터 준비

model = YOLO("yolo26n.pt")

results = model.train(
    data=YAML_PATH,
    epochs=10,
    imgsz=640,
    batch=16,
    project=os.path.join(BASE_DIR, "runs"),
    name="face_detector",
    exist_ok=True,
    device=0,
    workers=0
)

best_model_path = os.path.join(BASE_DIR, "runs", "face_detector", "weights", "best.pt")

print(f"Model saved to: {best_model_path}")