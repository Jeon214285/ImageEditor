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

def test_drag(page: Page):
    page.goto("http://localhost:8000")
    page.set_input_files("#imageInput", test_image_path)
    page.wait_for_timeout(500)

    canvas = page.locator("#Canvas")
    box = canvas.bounding_box()
    assert box is not None

    # 임의의 탐지 결과가 있다고 가정
    page.evaluate("""
        if (window.state) {
            window.state.detectFaces = [{x: 10, y: 10, w: 50, h: 50}];
            window.state.detectPlates = [{x: 20, y: 20, w: 60, h: 30}];
        }
    """)

    # 임의의 박스 드래그
    page.mouse.move(box['x'] + 50, box['y'] + 50)
    page.mouse.down()
    page.mouse.move(box['x'] + 200, box['y'] + 150)
    page.mouse.up()

    coords = page.evaluate("cropCoordinates")

    detect_faces = page.evaluate("window.state ? window.state.detectFaces : undefined")
    detect_plates = page.evaluate("window.state ? window.state.detectPlates : undefined")

    assert coords is not None
    assert coords["startX"] == 50
    assert coords["startY"] == 50
    assert coords["width"] == 150
    assert coords["height"] == 100

    # 드래그 시 탐지 결과가 정상적으로 초기화되는지 확인
    assert detect_faces is None
    assert detect_plates is None

    # 두 번째 박스 드래그
    page.mouse.move(box['x'] + 100, box['y'] + 50)
    page.mouse.down()
    page.mouse.move(box['x'] + 120, box['y'] + 80)
    page.mouse.up()

    coords = page.evaluate("cropCoordinates")

    assert coords is not None
    assert coords["startX"] == 100
    assert coords["startY"] == 50
    assert coords["width"] == 20
    assert coords["height"] == 30

    # 세 번째 박스 드래그 (드래그 X)
    page.mouse.move(box['x'] + 100, box['y'] + 50)
    page.mouse.down()
    page.mouse.move(box['x'] + 100, box['y'] + 50)
    page.mouse.up()

    coords = page.evaluate("cropCoordinates")

    assert coords is None