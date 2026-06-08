import { state } from './state.js';

function drawDetectedObjects(objects, color) {
    // 기존 상태 백업
    state.context.save();

    state.context.beginPath();
    state.context.strokeStyle = color; 
    state.context.lineWidth = 3;
    state.context.setLineDash([]);

    objects.forEach(obj => {
        // x, y 좌표와 너비, 높이를 이용해 사각형 그리기
        state.context.strokeRect(obj.x, obj.y, obj.w, obj.h);
    });

    // 기존 상태 복구
    state.context.restore();
}

export async function faceDetect() {
    if (document.body.style.cursor === "wait") return;

    const faceDetectBtn = document.getElementById('faceDetectBtn');

    state.context.putImageData(state.cleanImageData, 0, 0);  // 드래그 지우고 실행

    // 커서 로딩 상태로 변경
    document.body.style.cursor = "wait";
    state.canvas.style.cursor = "wait";
    if (faceDetectBtn) faceDetectBtn.disabled = true;

    state.canvas.toBlob(async (blob) => {
        if (!blob) {
            document.body.style.cursor = 'default';
            state.canvas.style.cursor = 'default';
            if (faceDetectBtn) faceDetectBtn.disabled = false;

        fetch('/api/log', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    level: 'ERROR',
                    action: 'FACE_DETECT_BLOB_ERROR',
                    details: `ERROR=Blob 변환 실패`
                })
            }).catch(err => console.error("에러 로그 전송 실패", err));
            return;
        }

        const formData = new FormData();
        formData.append('image', blob, 'current_image.png')

        const startTime = performance.now()

        try { 
            const response = await fetch('/api/detect', {
                method: 'POST',
                body: formData
            });

            const duration = Math.round(performance.now() - startTime);
        
            // 에러 발생 시
            if (!response.ok) {
                // 에러 로그
                fetch('/api/log', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        level: 'ERROR',
                        action: 'FACE_DETECT_API_ERROR',
                        details: `ERROR=API ERROR ${response.status}`
                    })
                }).catch(err => console.error("에러 로그 전송 실패", err));

                if (response.status === 415) {
                    alert("유효하지 않은 이미지입니다.");
                } else if (response.status === 500) {
                    alert("서버 내부 오류가 발생했습니다.");
                } else {
                    alert(`알 수 없는 오류 발생: ${response.status}`);
                }
                return;
            }

            // 받아온 얼굴 좌표 정보를 저장하는 부분
            const result = await response.json();
            const faces = result.faces;
            const count = result.count;

            state.detectFaces = faces;
            
            // 탐지된 그림이 있으면 그리기
            if (count > 0) {
               drawDetectedObjects(faces, '#00FF00');
            }
            
            // 로그 출력 포매팅 (여러개 일 수 있기 때문)
            const faceDetails = faces.map((f, index) => 
                `[${index + 1}] COOR=(${f.x}, ${f.y}) AREA=${f.width}x${f.height}px`
            ).join(' | ');


            fetch('/api/log', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    level: 'INFO',
                    action: 'FACE_DETECTOR_SUCCESS',
                    // 탐지한 얼굴 개수 정보 출력(개수, 좌표, 크기)
                    details: `FACES=${count} | ${faceDetails} | TIME=${duration}ms`
                })
            }).catch(err => console.error("에러 로그 전송 실패", err));

        } catch(error) {
            const duration = Math.round(performance.now() - startTime);
            fetch('/api/log', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    level: 'ERROR',
                    action: 'FACE_DETECT_ERROR',
                    details: `ERROR=${error.message}`
                })
            }).catch(err => console.error("에러 로그 전송 실패", err));
        } finally {
             document.body.style.cursor = 'default';
            state.canvas.style.cursor = 'default';
            if (faceDetectBtn) faceDetectBtn.disabled = false;
        }
    })
}