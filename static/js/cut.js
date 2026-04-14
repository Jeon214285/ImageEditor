import { state, setCropCoordinates } from './state.js';

export function imageCut() {
    if(!state.cropCoordinates) return;
    
    let x = state.cropCoordinates.startX;
    let y = state.cropCoordinates.startY;
    let w = state.cropCoordinates.width;
    let h = state.cropCoordinates.height;

    state.context.putImageData(state.cleanImageData, 0, 0);
    let cutImageData = state.context.getImageData(x, y, w, h);

    state.canvas.width = w;
    state.canvas.height = h;

    state.context.putImageData(cutImageData, 0, 0);

    // 이미지 위치 조정
    let currentLeft = parseInt(state.canvas.style.marginLeft || 0);
    let currentTop = parseInt(state.canvas.style.marginTop || 0);

    state.canvas.style.marginLeft = (currentLeft + x) + "px";
    state.canvas.style.marginTop = (currentTop + y) + "px";

    setCropCoordinates(null);
    state.cleanImageData = state.context.getImageData(0, 0, state.canvas.width, state.canvas.height);
}