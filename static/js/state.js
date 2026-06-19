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
    conf: 0.80,
    faceSetConf: null,
    plateSetConf: null,
    minConf: 1.00,
    modelType: null,

    detectFaces: null,
    detectPlates: null,
    
    faceScores: null,
    plateScores: null,
};

window.state = state;

export function setCropCoordinates(coords){
    state.cropCoordinates = coords;
    window.cropCoordinates = coords;
}