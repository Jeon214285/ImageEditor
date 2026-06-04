from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from app.grabcut import router as grabcut_router
import logging
from pydantic import BaseModel

# 로그 포맷
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d (%(funcName)s) | %(message)s"
)
logger = logging.getLogger("ImageEditor")

class LogData(BaseModel):
    level: str = 'INFO'  # 기본값 INFO
    action: str  # 예: "UPLOAD", "CROP", "GRABCUT"
    details: str # 예: "이미지 크기 1024x768"

# Fast 기반 웹 생성
app = FastAPI(title="ImageEditor")

# 정적 HTML 서빙
app.mount("/static", StaticFiles(directory="static"), name="static")

# GrabCut
app.include_router(grabcut_router)

# 메인 페이지 (/) 처리
@app.get("/", response_class=HTMLResponse)
def home():
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()

# favicon
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/IE_favicon.ico")

# 로그 수집
@app.post("/api/log")
async def collect_log(data: LogData):
    log_message = f"{data.action} | {data.details}"

    log_level = data.level.upper()

    if log_level == 'WARNING':
        logger.warning(log_message)
    elif log_level == "ERROR":
        logger.error(log_message)
    elif log_level == "CRITICAL":
        logger.critical(log_message)
    elif log_level == 'DEBUG':
        logger.debug(log_message)
    else:
        logger.info(log_message)

    return {'status': 'success'}

# uvicorn app.main:app --reload