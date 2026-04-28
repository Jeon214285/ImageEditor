import { state } from './state.js';

export async function backgroundRemoval() {
    if (!state.cropCoordinates || document.body.style.cursor === "wait") return;

    const grabcutBtn = document.getElementById('grabcutBtn');

    state.context.putImageData(state.cleanImageData, 0, 0);  // 드래그 지우고 실행
    // 작업시간 고려 로딩 상태로 변경
    document.body.style.cursor = "wait";
    state.canvas.style.cursor = "wait";
    if (grabcutBtn) grabcutBtn.disabled = true;

    state.canvas.toBlob(async (blob) => {
        if (!blob) {
            document.body.style.cursor = 'default';
            state.canvas.style.cursor = 'default';
            if (grabcutBtn) grabcutBtn.disabled = false;
            return;
        }

        const formData = new FormData();
        formData.append('image', blob, 'current_image.png');

        formData.append('x', Math.floor(state.cropCoordinates.startX));
        formData.append('y', Math.floor(state.cropCoordinates.startY));
        formData.append('w', Math.floor(state.cropCoordinates.width));
        formData.append('h', Math.floor(state.cropCoordinates.height));

        try{
            const response = await fetch('/api/grabcut', {
                method: 'POST',
                body: formData
            });
            
            // 에러 발생 시
            if (!response.ok) {
                if (response.status === 400) {
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
            };
            img.src = imgURL;
            
        } finally {
            document.body.style.cursor = 'default';
            state.canvas.style.cursor = "default";
            if (grabcutBtn) grabcutBtn.disabled = false;
            state.cropCoordinates = null; // 2번 누름 방지
        }
    }, 'image/png');   
}