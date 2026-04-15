import time
from playwright.sync_api import Page, expect
import subprocess, pytest

test_image_path = "tests/test.png"

@pytest.fixture(scope="session", autouse=True)
def start_test_server():
    server_process = subprocess.Popen(["uvicorn", "app.main:app", "--port", "8000"])
    time.sleep(2)
    yield
    server_process.terminate()

def get_canvas_data(page: Page):
        return page.evaluate('document.getElementById("Canvas").toDataURL()')

def test_grabcut(page: Page):
    # 이미지 불러오기
    page.goto("http://localhost:8000")
    page.set_input_files("#imageInput", test_image_path)
    page.wait_for_timeout(500)

    canvas = page.locator("#Canvas")
    box = canvas.bounding_box()
    assert box is not None

    # 원본 이미지
    pure_image_data = get_canvas_data(page)

    # 임의의 박스 드래그
    page.mouse.move(box['x'] + 20, box['y'] + 80)
    page.mouse.down()
    page.mouse.move(box['x'] + 180, box['y'] + 110)
    page.mouse.up()

    # 드래그로 박스가 쳐진 이미지
    boxed_image_data = get_canvas_data(page)

    # 배경 제거 버튼 클릭
    # 로딩시간 고려
    with page.expect_response("**/api/grabcut") as response_info:
        page.get_by_role("button", name="배경 제거").click()

        # 마우스 커서 로딩중인지 확인
        expect(page.locator("body")).to_have_css("cursor", "wait")

    # 정상(200)인지 확인
    assert response_info.value.ok

    # 마우스 커서 돌아왔는지 확인
    expect(page.locator("body")).to_have_css("cursor", "default")

    # 이미지 그릴 대기시간
    page.wait_for_timeout(100)
    
    # 최종 이미지
    after_image_data = get_canvas_data(page)

    # 이미지가 변했는지 테스트
    assert pure_image_data != after_image_data
    assert boxed_image_data != after_image_data