from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import logging

# 로그 포맷(모델 로드 시 로그 출력을 위해 import 전 설정)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d (%(funcName)s) | %(message)s"
)
logger = logging.getLogger()

from app.grabcut import router as grabcut_router
from app.detect import router as detect_router
from pydantic import BaseModel
from app.issue import *
from app.config import LOW_CONFIDENCE_THRESHOLD
from app.retrain_issue import update_issue_state

github_handler = GitHubIssueHandler()
github_handler.setLevel(logging.ERROR)  # ERROR 이상만 보냄
logger.addHandler(github_handler)

class DriftPayload(BaseModel):
    score: float

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

# Detect
app.include_router(detect_router)

# 메인 페이지 (/) 처리
@app.get("/", response_class=HTMLResponse)
def home():
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()

# favicon
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/IE_favicon.ico")

# drift
@app.post("/api/monitor/drift")
async def monitor_drift(
    payload: DriftPayload,
    background_tasks: BackgroundTasks  # 응답 지연 방지용
):
    background_tasks.add_task(update_issue_state, payload.score, LOW_CONFIDENCE_THRESHOLD)

    return {"status": "success"}

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