import { state, setCropCoordinates } from './state.js';

export function imageBlur() {
    if(!state.cropCoordinates) return;
    
    let x = state.cropCoordinates.startX;
    let y = state.cropCoordinates.startY;
    let w = state.cropCoordinates.width;
    let h = state.cropCoordinates.height;

    state.context.putImageData(state.cleanImageData, 0, 0);

    state.context.save();

    state.context.beginPath();
    state.context.rect(x, y, w,  h);
    state.context.clip();

    state.context.filter = 'blur(10px)';

    state.context.drawImage(state.canvas, 0, 0);
    
    state.context.restore();

    setCropCoordinates(null);
    state.cleanImageData = state.context.getImageData(0, 0, state.canvas.width, state.canvas.height);
}