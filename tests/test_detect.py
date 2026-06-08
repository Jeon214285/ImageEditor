# test_detect.py
import time
from playwright.sync_api import Page, expect
import subprocess, pytest
import json

test_image_path = "tests/test.png"

@pytest.fixture(scope="session", autouse=True)
def start_test_server():
    server_process = subprocess.Popen(["uvicorn", "app.main:app", "--port", "8000"])
    time.sleep(2)
    yield
    server_process.terminate()

def get_canvas_data(page: Page):
    return page.evaluate('document.getElementById("Canvas").toDataURL()')

def test_detect_ui(page: Page):
    # 이미지 불러오기(이미지가 있어야 실행되기 때문)
    page.goto("http://localhost:8000")
    page.set_input_files("#imageInput", test_image_path)
    page.wait_for_timeout(500)

    # 탐지 버튼 클릭 및 로딩시간 고려
    with page.expect_response("**/api/detect") as response_info:
        page.get_by_role("button", name="얼굴 탐지").click()

        # 마우스 커서 로딩중인지 확인
        expect(page.locator("body")).to_have_css("cursor", "wait")
        expect(page.locator("#Canvas")).to_have_css("cursor", "wait")

        # 버튼 비활성화 확인
        expect(page.get_by_role("button", name="얼굴 탐지")).to_be_disabled()

    # 정상(200)인지 확인
    assert response_info.value.ok

    # 마우스 커서 돌아왔는지 확인
    expect(page.locator("body")).to_have_css("cursor", "default")
    expect(page.locator("#Canvas")).to_have_css("cursor", "default")

    # 버튼 돌아왔는지 확인
    expect(page.locator("body")).to_have_css("cursor", "default")
    expect(page.get_by_role("button", name="얼굴 탐지")).to_be_enabled()

def test_face_detect(page: Page):
    page.goto("http://localhost:8000")
    page.set_input_files("#imageInput", "tests/test.png")
    page.wait_for_timeout(500)

    pure_image_data = get_canvas_data(page)

    # stub: 서버가 가짜 좌표를 반환하도록 조작
    def stub_success_response(route):
        # 변경된 부분: 실제 API가 반환하는 형태(dict)로 맞춰줍니다.
        fake_response = {
            "faces": [{"x": 50, "y": 50, "w": 100, "h": 100}],
            "count": 1
        }
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(fake_response)
        )
    page.route("**/api/detect", stub_success_response)

    # 탐지 버튼 클릭
    page.get_by_role("button", name="얼굴 탐지").click()
    page.wait_for_timeout(100) # 그릴 시간 대기

    after_image_data = get_canvas_data(page)

    # 캔버스가 변했는지 확인
    assert pure_image_data != after_image_data

def test_no_detect(page: Page):
    page.goto("http://localhost:8000")
    page.set_input_files("#imageInput", test_image_path)
    page.wait_for_timeout(500)

    pure_image_data = get_canvas_data(page)

    # 탐지 실패 상황
    page.route("**/api/detect", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body=json.dumps([]) # 빈 배열 반환
    ))

    page.get_by_role("button", name="얼굴 탐지").click()
    page.wait_for_timeout(100)

    after_image_data = get_canvas_data(page)

    # 이미지가 변하지 않아야 함
    assert pure_image_data == after_image_data

@pytest.mark.parametrize("status_code, expected_alert", [
     (415, "유효하지 않"),
     (500, "서버 내부 오류"),
     (418, "알 수 없는 오류")
])
def test_detect_error(page: Page, status_code, expected_alert):
    page.goto("http://localhost:8000")
    page.set_input_files("#imageInput", test_image_path)
    page.wait_for_timeout(500)

    # error 검증
    page.route("**/api/detect", lambda route: route.fulfill(status=status_code))
    
    with page.expect_event("dialog") as dialog_info:
        page.get_by_role("button", name="얼굴 탐지").click()
    
    actual_message = dialog_info.value.message  # 메시지 저장
    dialog_info.value.accept()  # 닫기

    assert expected_alert in actual_message  # 저장된 메시지로 검증

    # 에러 후 UI 복구 상태 검증
    expect(page.locator("body")).to_have_css("cursor", "default")
    expect(page.get_by_role("button", name="얼굴 탐지")).to_be_enabled()
