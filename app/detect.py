from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Response
from fastapi.responses import JSONResponse
import cv2
import numpy as np
import logging
import time
from ultralytics import YOLO
from app.model_loader import load_model

logger = logging.getLogger(__name__)

router = APIRouter()

try:
    model = load_model()
    logger.info("MODEL_LOAD_SUCCESS | LOADED YOLO MODEL FROM MLFLOW")
except Exception as e:
    model = YOLO('yolo26n.pt')  # 모델이 없으면 기본모델(CI/CD 대비)
    logger.warning(f"MODEL_LOAD_FAILED | EXCEPTION={e} | LOADED DEFAULT YOLO MODEL")

@router.post("/api/detect")
async def process_face_detect(
    image: UploadFile = File(...)
):
    api_start_time = time.time()

    try:
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # 이미지가 없을 경우
        if img is None:
            logger.warning("FACE_DETECT_FAILED | WARINIG=Invalid Image Format or Corrupted data.")
            return Response(status_code=415,
                            content="유효하지 않은 이미지입니다.")
        
        # 얼굴 탐지 로직
        algo_start_time = time.time()

        # 모델 추론
        # results = model.predict(source=img, imgsz=640, conf=0.5, verbose=False)
        results = model([img])

        # 탐지된 객체 정보 추출
        faces_count = 0
        boxes = results[0].boxes
        
        detected_faces = []
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            detected_faces.append({"x": x1, "y": y1, "w": x2 - x1, "h": y2 - y1})
            
            faces_count += 1

        algo_duration = (time.time() - algo_start_time) * 1000 # ms 단위


        total_duration = (time.time() - api_start_time) * 1000 # ms 단위

        # 탐지된 얼굴 개수 + 정보 로그에 출력
        logger.info(f"FACE_DETECT_SUCCESS | FACES={faces_count} | ALGOTIME={algo_duration:.0f}ms | TOTALTIME={total_duration:.0f}ms")

        return JSONResponse(content={"faces": detected_faces, "count": len(detected_faces)})
    
    except Exception as e:
        logger.error(f"FACE_DETECT_SERVER_ERROR | ERROR={str(e)}")
        return Response(status_code=500,
                        content="서버 내부 오류가 발생했습니다.")