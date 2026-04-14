import { state, setCropCoordinates } from './state.js';

// 마우스를 누를 때
function mouseDown(e) {
    if (!state.cleanImageData) {
        state.cleanImageData = state.context.getImageData(0, 0, state.canvas.width, state.canvas.height);
    }

    state.isDrawing = true;
    state.startX = e.offsetX;
    state.startY = e.offsetY;

    state.context.putImageData(state.cleanImageData, 0, 0);
    setCropCoordiates(null);
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
        return;
    }

    setCropCoordinates({
        startX: state.startX,
        startY: state.startY,
        width: width,
        height: height
    });
}

export function setupCanvasEvents() {
    state.canvas.addEventListener('mousedown', mouseDown);
    state.canvas.addEventListener('mousemove', mouseMove);
    state.canvas.addEventListener('mouseup', mouseUp);
}