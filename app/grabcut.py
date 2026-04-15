from fastapi import APIRouter, UploadFile, File, Form, Response
import cv2
import numpy as np

router = APIRouter()

@router.post("/api/grabcut")
async def process_grabcut(
    image: UploadFile = File(...),
    x: int = Form(...),
    y: int = Form(...),
    w: int = Form(...),
    h: int = Form(...)
):
    try:
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # 이미지가 없을 경우
        if img is None:
            return Response(status_code=400,
                            content="유효하지 않은 이미지입니다.")
        
        img_h, img_w = img.shape[:2]

        # 크래시 방지
        x = max(0, x)
        y = max(0, y)
        w = min(w, img_w - x)
        h = min(h, img_h - y)

        if w <= 1 or h <= 1:
            return Response(status_code=400,
                            content="선택 영역이 너무 작거나 범위를 벗어났습니다.")
        
        rect = (x, y, w, h)

        # 초기화 및 실행
        mask = np.zeros(img.shape[:2], np.uint8)
        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)

        cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)

        # 마스크 처리 및 투명 적용
        mask2 = np.where((mask==2) |  (mask==0), 0, 1).astype('uint8')
        b, g, r = cv2.split(img)
        alpha = mask2 * 255
        rgba_img = cv2.merge((b, g, r, alpha))

        # PNG 변환
        success, encoded_img = cv2.imencode('.png', rgba_img)
        if not success:
            return Response(status_code=500,
                            content="이미지 인코딩에 실패했습니다.")
        
        return Response(content=encoded_img.tobytes(),
                        media_type='image/png')
    
    except Exception as e:
        print(f"GrabCut Error: {e}")
        return Response(status_code=500,
                        content="서버 내부 오류가 발생했습니다.")

