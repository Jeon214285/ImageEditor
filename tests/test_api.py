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
    assert "자르기" in response.text
    assert "배경 제거" in response.text
    assert "흐리게" in response.text
    assert 'id="blurPx"' in response.text
    assert "원래대로" in response.text

def test_favicon():
    response = client.get("/favicon.ico")
    assert response.status_code == 200

def test_grabcut_api():
    test_image_path = "tests/test.png"

    with open(test_image_path, "rb") as image_file:
        response = client.post(
            "/api/grabcut",
            files={"image": ("test.png", image_file, "image/png")},
            data={"x": 10, "y": 10, "w": 80, "h": 80}
        )

    assert response.status_code == 200
    assert len(response.content) > 0