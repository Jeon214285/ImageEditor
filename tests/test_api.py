from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

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
    assert "얼굴 탐지" in response.text
    assert "차량 번호판 탐지" in response.text
    assert 'id="conf"' in response.text
    assert "모두 흐리게" in response.text
    assert "못 찾은 얼굴이 있음" in response.text
    assert "얼굴이 아닌 곳을 가리킴" in response.text
    assert "얼굴 위치가 안 맞음" in response.text
    assert "못 찾은 번호판이 있음" in response.text
    assert "번호판이 아닌 곳을 가리킴" in response.text
    assert "번호판 위치가 안 맞음" in response.text

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

@patch("app.main.append_prediction_log")
def test_detect_api(mock_append_log):
    _ = mock_append_log  # VSCODE상 어둡게 하는 것을 방지
    
    test_image_path = "tests/test.png"

    with open(test_image_path, "rb") as image_file:
        face_response = client.post(
            "/api/detect/face",
            files={"image": ("test.png", image_file, "image/png")}
        )

        plate_response = client.post(
            "/api/detect/plate",
            files={"image": ("test.png", image_file, "image/png")}
        )

    assert face_response.status_code == 200
    assert plate_response.status_code == 200
    face_response_data = face_response.json()
    plate_response_data = plate_response.json()

    assert isinstance(face_response_data, dict)  # json 형식으로 반환하는지 확인
    assert isinstance(plate_response_data, dict)  # json 형식으로 반환하는지 확인

    assert "count" in face_response_data
    assert "faces" in face_response_data
    assert "count" in plate_response_data
    assert "plates" in plate_response_data
    
    assert isinstance(face_response_data["faces"], list)
    assert isinstance(plate_response_data["plates"], list)
    # assert len(result) > 0  # 얼굴이 없을 수 있으므로 테스트 X