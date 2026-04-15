from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from app.grabcut import router as grabcut_router

# Fast 기반 웹 생성
app = FastAPI(title="ImageEditor")

# 정적 HTML 서빙
app.mount("/static", StaticFiles(directory="static"), name="static")

# GrabCut
app.include_router(grabcut_router)

# 메인 체이지 (/) 처리
@app.get("/", response_class=HTMLResponse)
def home():
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/IE_favicon.ico")

# uvicorn app.main:app --reload