import { state, setCropCoordinates } from './state.js';

// 마우스를 누를 때
function mouseDown(e) {
    if (!state.cleanImageData) {
        // 탐지 결과 삭제
        state.detectFaces = null;
        state.detectPlates = null;
        state.cleanImageData = state.context.getImageData(0, 0, state.canvas.width, state.canvas.height);
    }

    state.isDrawing = true;
    state.startX = e.offsetX;
    state.startY = e.offsetY;

    state.context.putImageData(state.cleanImageData, 0, 0);
    setCropCoordinates(null);
}

// 마우스를 움직일 때
function mouseMove(e) {
    if (!state.isDrawing) return;

    state.context.putImageData(state.cleanImageData, 0, 0);

    const currentX = e.offsetX;
    const currentY = e.offsetY;
    const width = currentX - state.startX;
    const height = currentY - state.startY;

    state.context.beginPath();
    state.context.strokeStyle = '#808080';
    state.context.lineWidth = 2;
    state.context.setLineDash([6, 4]);
    state.context.strokeRect(state.startX, state.startY, width, height);
}

// 마우스를 뗄 때
function mouseUp(e) {
    if (!state.isDrawing) return;
    state.isDrawing = false;

    const endX = e.offsetX;
    const endY = e.offsetY;
    const width = Math.abs(endX - state.startX);
    const height = Math.abs(endY - state.startY);

    if (width === 0 || height === 0) {
        state.context.putImageData(state.cleanImageData, 0, 0);
        setCropCoordinates(null);
        return;
    }

    // 역방향 드래그로 해도 정상 작동하도록
    const finalStartX = Math.min(state.startX, endX);
    const finalStartY = Math.min(state.startY, endY);

    setCropCoordinates({
        startX: finalStartX,
        startY: finalStartY,
        width: width,
        height: height
    });

    fetch('/api/log', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            level: 'DEBUG',
            action: 'AREA_SELECTED',
            details: `COOR=(${finalStartX}, ${finalStartY}) | AREA=${width}x${height}px`
        })
    }).catch(err => console.error("로그 전송 실패", err));
}

export function setupCanvasEvents() {
    state.canvas.addEventListener('mousedown', mouseDown);
    state.canvas.addEventListener('mousemove', mouseMove);
    state.canvas.addEventListener('mouseup', mouseUp);
}