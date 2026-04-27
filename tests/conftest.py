import sys, json, uuid, pytest
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# js 파일 커버리지 계산
@pytest.fixture(autouse=True)
def js_coverage(page):
    cdp = page.context.new_cdp_session(page)
    cdp.send("Profiler.enable")
    cdp.send("Profiler.startPreciseCoverage",
             {"callCount": True, "detailed": True})
    
    yield

    # 커버리지 데이터 가져오기
    coverage = cdp.send("Profiler.takePreciseCoverage")

    project_root = Path(__file__).resolve().parents[1]
    coverage_dir = project_root / ".js_coverage"
    coverage_dir.mkdir(exist_ok=True)

    filtered_scripts = []
    
    for script in coverage.get("result", []):
        url = script.get("url", "")
        
        # 외부 라이브러리 제외, 로컬 서버의 .js 파일만 필터링
        if url.endswith(".js") and ("127.0.0.1" in url or "localhost" in url):
            parsed = urlparse(url)
            # URL(http://)을 실제 디스크의 절대 경로(file://)로 매핑
            local_path = project_root / parsed.path.lstrip("/") 
            
            script["url"] = f"file://{local_path.absolute()}"
            filtered_scripts.append(script)
    
    # 필터링된 데이터가 있으면 UUID를 부여하여 개별 JSON으로 저장
    if filtered_scripts:
        file_path = coverage_dir / f"coverage-{uuid.uuid4().hex}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({"result": filtered_scripts}, f)

    # 프로파일러 끄기
    cdp.send("Profiler.disable")