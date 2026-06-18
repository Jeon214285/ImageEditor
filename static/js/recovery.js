import { state, setCropCoordinates } from './state.js';

export function imageRecovery(){
    if (!state.originalImageData) return;

    try {
        state.canvas.width = state.originalImageData.width;
        state.canvas.height = state.originalImageData.height;

        state.context.putImageData(state.originalImageData, 0, 0);

        state.canvas.style.marginLeft = "0px";
        state.canvas.style.marginTop = "0px";

        setCropCoordinates(null);
        state.cleanImageData = state.originalImageData;
        
        state.faceSetConf = null;
        state.plateSetConf = null;

        state.detectFaces = null;
        state.detectPlates = null;

        fetch('/api/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                level: 'INFO',
                action: 'RECOVERY_IMAGE_SUCCESS',
                details: `RESOLUTION=${state.canvas.width}x${state.canvas.height}px`
            })
        }).catch(err => console.error("로그 전송 실패", err));
    } catch(error) {
        fetch('/api/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                level: 'ERROR',
                action: 'RECOVERY_IMAGE_ERROR',
                details: `RESOLUTION=${state.canvas.width}x${state.canvas.height}px | ERROR=${error.message}`
            })
        }).catch(err => console.error("에러 로그 전송 실패", err));
        
        alert("이미지 복구 중 오류가 발생했습니다.")
    }
}