import time
from playwright.sync_api import Page
import subprocess, pytest

test_image_path = "tests/test.png"

@pytest.fixture(scope="session", autouse=True)
def start_test_server():
    server_process = subprocess.Popen(["uvicorn", "app.main:app", "--port", "8000"])
    time.sleep(2)
    yield
    server_process.terminate()

# 자르기 후 복구하는 기능에 대한 테스트
def test_cut_recovery(page: Page):
    # 이미지 불러오기
    page.goto("http://localhost:8000")
    page.set_input_files("#imageInput", test_image_path)
    page.wait_for_timeout(500)

    # 현재 상태 저장
    original_state = page.evaluate("""() => {
        const c = document.getElementById('Canvas');
        return { width: c.width, height: c.height };
    }""")

    #이미지 자르기
    canvas = page.locator("#Canvas")
    box = canvas.bounding_box()
    assert box is not None
    
    # 임의의 박스 드래그
    page.mouse.move(box["x"] + 20, box["y"] + 20)
    page.mouse.down()
    page.mouse.move(box["x"] + 70, box["y"] + 70)
    page.mouse.up()
    
    # 자르기 버튼 클릭
    page.get_by_role("button", name="자르기").click()

    # 복구 버튼 클릭
    page.get_by_role("button", name="원래대로").click()

    # 복구 후 상태 저장
    recovered_state = page.evaluate("""() => {
        const c = document.getElementById('Canvas');
        return {
            width: c.width,
            height: c.height,
            marginLeft: c.style.marginLeft,
            marginTop: c.style.marginTop
        };
    }""")

    # 캔버스 크기가 처음에 저장해둔 원본 크기로 돌아왔는가?
    assert recovered_state["width"] == original_state["width"]
    assert recovered_state["height"] == original_state["height"]

    # 마진이 0px로 초기화되었는가?
    assert recovered_state["marginLeft"] in ["0px", "0", ""]
    assert recovered_state["marginTop"] in ["0px", "0", ""]

    # null로 비워졌는가?
    coords = page.evaluate("window.cropCoordinates")
    assert coords is None

def test_cut_recovery_without_image(page: Page):
    page.goto("http://localhost:8000")
    page.wait_for_timeout(500)

    inital_state = page.evaluate("""() => {
        const c = document.getElementById('Canvas');
        return { width: c.width, height: c.height };
    }""")

    page.get_by_role("button", name="원래대로").click()
    page.wait_for_timeout(200)

    after_state = page.evaluate("""() => {
        const c = document.getElementById('Canvas');
        return { width: c.width, height: c.height };
    }""")

    assert inital_state['width'] == after_state['width']
    assert inital_state['height'] == after_state['height']