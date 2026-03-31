from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# Fast 기반 웹 생성
app = FastAPI(title="ImageEditor")

# 정적 HTML 서빙
app.mount("/static", StaticFiles(directory="static"), name="static")

# 메인 체이지 (/) 처리
@app.get("/", response_class=HTMLResponse)
def home():
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()
    
# uvicorn app.main:app --reload