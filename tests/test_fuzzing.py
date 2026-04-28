from hypothesis import given, strategies as st
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

VALID_FORM_DATA = {  # 422 error 방지
    "x": 10,
    "y": 10,
    "w": 100,
    "h": 100
}

@given(st.binary(min_size=1, max_size=50000))
def test_hypothesis_fuzzung(raw_bytes):
    response = client.post(
        "/api/grabcut",
        files={"image": ("fuzz_test.png", raw_bytes, "image/png")},
        data=VALID_FORM_DATA
    )

    assert response.status_code == 400
    assert response.text == "유효하지 않은 이미지입니다."