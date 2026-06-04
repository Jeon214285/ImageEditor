import { state } from './state.js';

export function imageDownload() {
    if (state.canvas.width === 0 || state.canvas.height === 0) {
        alert("다운로드할 이미지가 없습니다.");
        return;
    }

    try {
        if (state.cleanImageData) {
            state.context.putImageData(state.cleanImageData, 0, 0);
        }
        const dataURL = state.canvas.toDataURL('image/png');

        // 로그를 위한 용량 및 해상도 계산
        const sizeInBytes = Math.round(dataURL.length * 0.75);
        const sizeInKB = (sizeInBytes / 1024).toFixed(2);

        const resWidth = state.canvas.width;
        const resHeight = state.canvas.height;

        const link = document.createElement('a');
        link.href = dataURL;
        link.download = "image.png";
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        // 로그 데이터 전송
        fetch('/api/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                level: 'INFO',
                action: 'DOWNLOAD_IMAGE_SUCCESS',
                details: `FILE=${link.download} | SIZE==${sizeInKB}KB | RESOLUTION=${resWidth}x${resHeight}px`
            })
        }).catch(err => console.error("로그 전송 실패", err));
    } catch (error) {
        fetch('/api/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                level: 'ERROR',
                action: 'DOWNLOAD_IMAGE_ERROR',
                details: `ERROR=${error.message}`
            })
        }).catch(err => console.error("에러 로그 전송 실패", err));
        
        alert("다운로드 중 오류가 발생했습니다.")
    }
}