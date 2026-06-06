from fastapi import APIRouter, UploadFile, File, Form, Response
import cv2
import numpy as np
import logging
import time

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/api/grabcut")
async def process_grabcut(
    image: UploadFile = File(...),
    x: int = Form(...),
    y: int = Form(...),
    w: int = Form(...),
    h: int = Form(...)
):
    api_start_time = time.time()

    try:
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # 이미지가 없을 경우
        if img is None:
            logger.warning("GRABCUT_FAILED | WARINIG=Invalid Image Format or Corrupted data.")
            return Response(status_code=400,
                            content="유효하지 않은 이미지입니다.")
        
        img_h, img_w = img.shape[:2]

        logger.info(f"GRABCUT_START | COOR=({x}, {y}) | AREA={w}x{h}px")

        # 크래시 방지
        x = max(0, x)
        y = max(0, y)
        w = min(w, img_w - x)
        h = min(h, img_h - y)

        if w <= 1 or h <= 1:
            logger.warning(f"GRABCUT_BAD_REQUEST | COOR=({x}, {y}) | AREA={w}x{h}px | WARNING=Rect Too Small or Out of Bounds.")
            return Response(status_code=400,
                            content="선택 영역이 너무 작거나 범위를 벗어났습니다.")
        
        rect = (x, y, w, h)

        # 초기화 및 실행
        mask = np.zeros(img.shape[:2], np.uint8)
        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)

        algo_start_time = time.time()
        cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
        algo_duration = (time.time() - algo_start_time) * 1000 # ms 단위

        # 마스크 처리 및 투명 적용
        mask2 = np.where((mask==2) |  (mask==0), 0, 1).astype('uint8')
        b, g, r = cv2.split(img)
        alpha = mask2 * 255
        rgba_img = cv2.merge((b, g, r, alpha))

        # PNG 변환
        success, encoded_img = cv2.imencode('.png', rgba_img)
        if not success:
            logger.error("GRABCUT_ENCODE_ERROR | ERROR=Failed to Encode cv2 Image")
            return Response(status_code=500,
                            content="이미지 인코딩에 실패했습니다.")
        
        total_duration = (time.time() - api_start_time) * 1000 # ms 단위

        logger.info(f"GRABCUT_SUCCESS | COOR=({x}, {y}) | AREA={w}x{h}px | ALGOTIME={algo_duration:.0f}ms | TOTALTIME={total_duration:.0f}ms")

        return Response(content=encoded_img.tobytes(),
                        media_type='image/png')
    
    except Exception as e:
        logger.error(f"GRABCUT_SERVER_ERROR | ERROR={str(e)}", exc_info=True)
        return Response(status_code=500,
                        content="서버 내부 오류가 발생했습니다.")