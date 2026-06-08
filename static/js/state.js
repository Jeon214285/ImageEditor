export const state = {
    canvas: null,
    context: null,
    imageInput: null,

    originalImageData: null,
    cleanImageData: null,
    cropCoordinates: null,

    isDrawing: false,
    startX: 0,
    startY: 0,

    blurPx: 50,

    faceDetect: null,
};

window.state = state;

export function setCropCoordinates(coords){
    state.cropCoordinates = coords;
    window.cropCoordinates = coords;
}