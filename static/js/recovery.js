import { state, setCropCoordinates } from './state.js';

export function imageRecovery(){
    if (!state.originalImageData) return;

    state.canvas.width = state.originalImageData.width;
    state.canvas.height = state.originalImageData.height;

    state.context.putImageData(state.originalImageData, 0, 0);

    state.canvas.style.marginLeft = "0px";
    state.canvas.style.marginTop = "0px";

    setCropCoordinates(null);
    state.cleanImageData = state.originalImageData;
}