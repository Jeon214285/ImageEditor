import { state } from './state.js';

export function imageDownload() {
    if (state.canvas.width === 0 || state.canvas.height === 0) {
        alert("다운로드할 이미지가 없습니다.");
        return;
    }

    if(state.cleanImageData) {
        state.context.putImageData(state.cleanImageData, 0, 0);
    }
    const dataURL = state.canvas.toDataURL('image/png');
    const link = document.createElement('a');
    link.href = dataURL;
    link.download = "image.png";
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}