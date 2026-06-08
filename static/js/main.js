// main.js
import { state } from './state.js';
import { setupCanvasEvents } from './events.js';
import { imageUpload, setupImageInput } from './upload.js';
import { imageDownload } from './download.js';
import { imageCut } from './cut.js';
import { imageRecovery } from './recovery.js';
import { backgroundRemoval } from './grabcut.js';
import { controlBlur, imageBlur } from './blur.js';
import { faceDetect } from './detect.js';

// DOM 요소들을 State에 등록
document.addEventListener('DOMContentLoaded', () => {
    state.canvas = document.getElementById('Canvas');
    state.context = state.canvas.getContext('2d', { willReadFrequently: true });
    state.imageInput = document.getElementById("imageInput");

    // 이벤트 리스너 세팅
    setupImageInput();
    setupCanvasEvents();
});

// HTML의 onclick 속성 및 Playwright 테스트를 위해 window 객체에 연결
window.imageUpload = imageUpload;
window.imageDownload = imageDownload;
window.imageCut = imageCut;
window.imageRecovery = imageRecovery;
window.backgroundRemoval = backgroundRemoval;
window.imageBlur = imageBlur;
window.controlBlur = controlBlur;
window.faceDetect = faceDetect;