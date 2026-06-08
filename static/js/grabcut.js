import { state } from './state.js';

export async function backgroundRemoval() {
    if (!state.cropCoordinates || document.body.style.cursor === "wait") return;

    const grabcutBtn = document.getElementById('grabcutBtn');

    state.context.putImageData(state.cleanImageData, 0, 0);  // 드래그 지우고 실행

    // 작업시간 고려 로딩 상태로 변경
    document.body.style.cursor = "wait";
    state.canvas.style.cursor = "wait";
    if (grabcutBtn) grabcutBtn.disabled = true;

    // 좌표/크기 정보 사전 추출
    const x = Math.floor(state.cropCoordinates.startX);
    const y = Math.floor(state.cropCoordinates.startY);
    const w = Math.floor(state.cropCoordinates.width);
    const h = Math.floor(state.cropCoordinates.height);

    state.canvas.toBlob(async (blob) => {
        if (!blob) {
            document.body.style.cursor = 'default';
            state.canvas.style.cursor = 'default';
            if (grabcutBtn) grabcutBtn.disabled = false;

            // 에러 로그
            fetch('/api/log', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    level: 'ERROR',
                    action: 'GRABCUT_BLOB_ERROR',
                    details: `COOR=(${x}, ${y}) | AREA=${w}x${h}px | ERROR=Blob 변환 실패`
                })
            }).catch(err => console.error("에러 로그 전송 실패", err));
            return;
        }

        const formData = new FormData();
        formData.append('image', blob, 'current_image.png');
        formData.append('x', x);
        formData.append('y', y);
        formData.append('w', w);
        formData.append('h', h);

        // 소요 시간 측정
        const startTime = performance.now()

        try {
            const response = await fetch('/api/grabcut', {
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
                        action: 'GRABCUT_API_ERROR',
                        details: `COOR=(${x}, ${y}) | AREA=${w}x${h}px | ERROR=API ERROR ${response.status}`
                    })
                }).catch(err => console.error("에러 로그 전송 실패", err));

                if (response.status === 415) {
                    alert("유효하지 않은 이미지입니다.");
                } else if (response.status === 422) {
                    alert("선택 영역이 너무 작거나 범위를 벗어났습니다.");
                } else if (response.status === 500) {
                    alert("서버 내부 오류가 발생했습니다.");
                } else {
                    alert(`알 수 없는 오류 발생: ${response.status}`);
                }
                return;
            }

            const resultBlob = await response.blob();
            const imgURL = URL.createObjectURL(resultBlob);

            const img = new Image();
            img.onload = () => {
                state.context.clearRect(0, 0, state.canvas.width, state.canvas.height);
                state.context.drawImage(img, 0, 0);
                state.cleanImageData = state.context.getImageData(0, 0, state.canvas.width, state.canvas.height);
                URL.revokeObjectURL(imgURL); // 메모리 누수 방지

                fetch('/api/log', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        level: 'INFO',
                        action: 'GRABCUT_SUCCESS',
                        details: `COOR=(${x}, ${y}) | AREA=${w}x${h}px | TIME=${duration}ms`
                    })
                }).catch(err => console.error("에러 로그 전송 실패", err));
            };
            img.src = imgURL;
            
        } catch(error) {
            const duration = Math.round(performance.now() - startTime);
            fetch('/api/log', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    level: 'ERROR',
                    action: 'GRABCUT_ERROR',
                    details: `COOR=(${x}, ${y}) | AREA=${w}x${h}px | ERROR=${error.message}`
                })
            }).catch(err => console.error("에러 로그 전송 실패", err));
        } finally {
            document.body.style.cursor = 'default';
            state.canvas.style.cursor = "default";
            if (grabcutBtn) grabcutBtn.disabled = false;
            state.cropCoordinates = null; // 2번 누름 방지
        }
    }, 'image/png');   
}