import { state, setCropCoordinates } from './state.js';

export function controlBlur() {
    state.blurPx = parseInt(document.getElementById("blurPx").value, 10);
}

export function imageBlur() {
    if(!state.cropCoordinates) return;
    
    let x = state.cropCoordinates.startX;
    let y = state.cropCoordinates.startY;
    let w = state.cropCoordinates.width;
    let h = state.cropCoordinates.height;

    state.context.putImageData(state.cleanImageData, 0, 0);

    if (state.blurPx > 0) {
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = state.canvas.width;
        tempCanvas.height = state.canvas.height;
        const tempCtx = tempCanvas.getContext('2d');

        tempCtx.putImageData(state.cleanImageData, 0, 0);

        state.context.save();
        state.context.beginPath();
        state.context.rect(x, y, w,  h);
        state.context.clip();

        state.context.filter = 'blur('+ state.blurPx +'px)';
        state.context.drawImage(state.canvas, 0, 0);
        
        state.context.restore();
    }

    setCropCoordinates(null);
    state.cleanImageData = state.context.getImageData(0, 0, state.canvas.width, state.canvas.height);
}