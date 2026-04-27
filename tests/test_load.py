import pytest
from playwright.sync_api import Page
import cv2
import subprocess, time

test_image_path = "tests/test.png"

@pytest.fixture(scope="session", autouse=True)
def start_test_server():
    server_process = subprocess.Popen(["uvicorn", "app.main:app", "--port", "8000"])
    time.sleep(2)
    yield
    server_process.terminate()

def test_image_upload(page: Page):
    img = cv2.imread(test_image_path)
    original_height, original_width, _ = img.shape

    page.goto("http://localhost:8000")
    page.wait_for_timeout(500)

    with page.expect_file_chooser() as fc_info:
        page.get_by_role("button", name="이미지 업로드").click()

    file_chooser = fc_info.value
    file_chooser.set_files(test_image_path)
    page.wait_for_timeout(500)

    canvas = page.locator('#Canvas')
    width = canvas.evaluate("el => el.width")
    height = canvas.evaluate("el => el.height")

    assert width == original_width
    assert height == original_height

def test_image_download(page: Page):
    page.goto("http://localhost:8000")
    page.set_input_files("#imageInput", test_image_path)
    page.wait_for_timeout(500)

    with page.expect_download() as download_info:
        page.get_by_role("button", name="이미지 다운로드").click()
    
    download = download_info.value

    assert download.suggested_filename == "image.png"

def test_image_download_without_image(page: Page):
    page.goto("http://localhost:8000")
    page.wait_for_timeout(500)

    dialog_messages = []

    def handle_dialog(dialog):
        dialog_messages.append(dialog.message) # 메시지 저장
        dialog.accept() # 확인 버튼 누르기

    page.on("dialog", handle_dialog)

    page.get_by_role("button", name="다운로드").click()
    page.wait_for_timeout(200)

    assert dialog_messages[0] == "다운로드할 이미지가 없습니다."