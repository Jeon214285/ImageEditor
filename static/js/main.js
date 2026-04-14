// main.js
import { state } from './state.js';
import { setupCanvasEvents } from './events.js';

// 기존 actions.js 대신 기능별 파일에서 임포트
import { imageUpload, setupImageInput } from './upload.js';
import { imageDownload } from './download.js';
import { imageCut } from './cut.js';
import { imageRecovery } from './recovery.js';

// 1. DOM 요소들을 State에 등록
document.addEventListener('DOMContentLoaded', () => {
    state.canvas = document.getElementById('Canvas');
    state.context = state.canvas.getContext('2d');
    state.imageInput = document.getElementById("imageInput");

    // 2. 이벤트 리스너 세팅
    setupImageInput();
    setupCanvasEvents();
});

// 3. HTML의 onclick 속성 및 Playwright 테스트를 위해 window 객체에 연결
window.imageUpload = imageUpload;
window.imageDownload = imageDownload;
window.imageCut = imageCut;
window.imageRecovery = imageRecovery;