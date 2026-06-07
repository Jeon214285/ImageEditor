import os
import numpy as np
from pathlib import Path
from ultralytics import YOLO

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "ml" / "runs" / "face_detector" / "weights" / "best.pt"

# GitHub Actions를 위한 임시 pt파일 생성
TEST_MODEL_PATH = MODEL_PATH if MODEL_PATH.exists() else "yolov8n.pt"

# def test_trained_model_exists():
#     assert MODEL_PATH.exists()

def test_model_can_predict():
    model = YOLO(TEST_MODEL_PATH)

    # 테스트용 더미 이미지 생성 (640x640 크기의 빈 검은색 이미지)
    dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)

    # 예측 수행
    results = model.predict(source=dummy_image, imgsz=640, verbose=False)

    # 검증 (Assertion)
    assert len(results) > 0
    
    # YOLO의 결과 객체(results[0])에 bounding box 정보가 담기는지 확인
    assert hasattr(results[0], 'boxes')
    assert type(results[0].boxes.data.tolist()) == list