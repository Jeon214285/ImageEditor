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

def test_cut(page: Page):
    # 이미지 불러오기
    page.goto("http://localhost:8000")
    page.set_input_files("#imageInput", test_image_path)
    page.wait_for_timeout(500)

    canvas = page.locator("#Canvas")
    box = canvas.bounding_box()
    assert box is not None

    # 임의의 박스 드래그
    page.mouse.move(box['x'] + 50, box['y'] + 60)
    page.mouse.down()
    page.mouse.move(box['x'] + 200, box['y'] + 160)
    page.mouse.up()

    # 자르기 버튼 클릭
    page.get_by_role("button", name="자르기").click()

    # 캔버스 정보 불러오기
    result = page.evaluate("""() => {
        const c = document.getElementById('Canvas');
        return {
            width: c.width,
            height: c.height,
            marginLeft: c.style.marginLeft,
            marginTop: c.style.marginTop
        };
    }""")

    # 캔버스 크기가 잘린 영역만큼 줄어들었는가?
    assert result["width"] == 150
    assert result["height"] == 100
    
    # 잘린 이미지가 원래 위치를 유지하는가?
    assert result["marginLeft"] == "50px"
    assert result["marginTop"] == "60px"