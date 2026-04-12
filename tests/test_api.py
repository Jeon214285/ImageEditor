from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_page():
    # 접속 테스트
    response = client.get("/")
    assert response.status_code == 200

    assert "ImageEditor" in response.text
    assert "이미지 업로드" in response.text
    assert "이미지 다운로드" in response.text
