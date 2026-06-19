import time
from playwright.sync_api import Page
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

def test_control(page: Page):
    page.goto("http://localhost:8000")

    slider = page.locator("id=blurPx")
    slider.wait_for(state="visible")

    initial_slider_value = int(slider.input_value())
    initial_state_value = page.evaluate("() => window.state.blurPx")

    assert initial_slider_value == initial_state_value

    slider.fill(str(80))

    updated_slider_value = int(slider.input_value())
    updated_state_value = page.evaluate("() => window.state.blurPx")

    assert updated_slider_value == 80
    assert updated_state_value == 80

def test_blur_with_selection(page: Page):
    # 이미지 불러오기
    page.goto("http://localhost:8000")
    page.set_input_files("#imageInput", test_image_path)
    page.wait_for_timeout(500)

    canvas = page.locator("#Canvas")
    box = canvas.bounding_box()
    assert box is not None

    initial_info = page.evaluate("""() => {
        const c = document.getElementById('Canvas');
        return { width: c.width, height: c.height };
    }""")
    initial_w = initial_info['width']
    initial_h = initial_info['height']
                                 
    pure_image_data = get_canvas_data(page)

    # 임의의 박스 드래그
    page.mouse.move(box['x'] + 50, box['y'] + 60)
    page.mouse.down()
    page.mouse.move(box['x'] + 650, box['y'] + 340)
    page.mouse.up()

    boxed_image_data = get_canvas_data(page)

    # 흐리게 버튼 클릭
    page.get_by_role("button", name="흐리게", exact=True).click()

    page.wait_for_timeout(100)

    # 캔버스 정보 불러오기
    final_info = page.evaluate("""() => {
        const c = document.getElementById('Canvas');
        return {
            width: c.width, height: c.height
        };
    }""")

    after_image_data = get_canvas_data(page)

    assert final_info['width'] == initial_w
    assert final_info['height'] == initial_h

    assert after_image_data != pure_image_data  # 원본이랑 동일한지
    assert after_image_data != boxed_image_data

def test_blur_with_detection(page: Page):
    # 이미지 불러오기
    page.goto("http://localhost:8000")
    page.set_input_files("#imageInput", test_image_path)
    page.wait_for_timeout(500)

    # 캔버스 정보 및 원본 이미지 데이터 저장
    initial_info = page.evaluate("""() => {
        const c = document.getElementById('Canvas');
        return { width: c.width, height: c.height };
    }""")
    pure_image_data = get_canvas_data(page)

    def stub_success_face_response(route):
        fake_response = {
            "faces": [{"x": 50, "y": 50, "w": 200, "h": 150}],
            "count": 1
        }
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(fake_response)
        )
    page.route("**/api/detect/face", stub_success_face_response)

    def stub_success_plate_response(route):
        fake_response = {
            "plates": [{"x": 250, "y": 200, "w": 200, "h": 150}],
            "count": 1
        }
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(fake_response)
        )
    page.route("**/api/detect/plate", stub_success_plate_response)

    # 얼굴 탐지
    with page.expect_response("**/api/detect/face"):
        page.get_by_role("button", name="얼굴 탐지").click()
    page.wait_for_timeout(500)  # 캔버스에 박스가 그려질 시간 대기

    # 번호판 탐지
    with page.expect_response("**/api/detect/plate"):
        page.get_by_role("button", name="차량 번호판 탐지").click()
    page.wait_for_timeout(500)  # 캔버스에 박스가 그려질 시간 대기

    # 모두 흐리게 선택
    page.get_by_role("button", name="모두 흐리게").click()    
    page.wait_for_timeout(500) # 블러 렌더링 대기

    # 6. 캔버스 상태 확인 및 최종 이미지 데이터 가져오기
    final_info = page.evaluate("""() => {
        const c = document.getElementById('Canvas');
        return { width: c.width, height: c.height };
    }""")
    after_image_data = get_canvas_data(page)

    # 캔버스 크기 유지 검증
    assert final_info['width'] == initial_info['width']
    assert final_info['height'] == initial_info['height']

    # 최종 결과물 이미지 데이터 검증
    assert after_image_data != pure_image_data  # 원본 이미지와 달라야 함 (블러 적용됨)

    # JS 상태(State) 값 초기화 검증
    # 블러 처리가 완료된 후 state의 탐지 배열들이 모두 null로 돌아갔는지 확인
    detect_faces = page.evaluate("window.state.detectFaces")
    detect_plates = page.evaluate("window.state.detectPlates")

    assert detect_faces is None
    assert detect_plates is None

def test_blur_without_selection(page: Page):
    page.goto("http://localhost:8000")
    page.set_input_files("#imageInput", test_image_path)
    page.wait_for_timeout(500)

    initial_info = page.evaluate("""() => {
        const c = document.getElementById('Canvas');
        return { width: c.width, height: c.height };
    }""")
    pure_image_data = get_canvas_data(page)

    page.get_by_role("button", name="흐리게", exact=True).click()
    page.wait_for_timeout(100)

    after_info = page.evaluate("""() => {
        const c = document.getElementById('Canvas');
        return { width: c.width, height: c.height };
    }""")
    after_image_data = get_canvas_data(page)

    assert initial_info["width"] == after_info["width"]
    assert initial_info["height"] == after_info["height"]
    assert pure_image_data == after_image_data