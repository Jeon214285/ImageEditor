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

    try{
        state.context.putImageData(state.cleanImageData, 0, 0);

        if (state.blurPx > 0) {  // 블러 정도를 0 이상으로 했을 경우만
            const tempCanvas = document.createElement('canvas');
            tempCanvas.width = state.canvas.width;
            tempCanvas.height = state.canvas.height;
            const tempCtx = tempCanvas.getContext('2d');

            tempCtx.putImageData(state.cleanImageData, 0, 0);

            state.context.save();
            state.context.beginPath();
            state.context.rect(x, y, w, h);
            state.context.clip();

            state.context.filter = 'blur('+ state.blurPx +'px)';
            state.context.drawImage(tempCanvas, 0, 0);
            
            state.context.restore();
        }

        setCropCoordinates(null);
        state.cleanImageData = state.context.getImageData(0, 0, state.canvas.width, state.canvas.height);

        // 로그 데이터 전송
        fetch('/api/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                level: 'INFO',
                action: 'BLUR_IMAGE_SUCCESS',
                details: `COOR=(${x}, ${y}) | AREA=${w}x${h}px | BLURPX=${state.blurPx}`
            })
        }).catch(err => console.error("로그 전송 실패", err));
    } catch(error) {
        fetch('/api/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                level: 'ERROR',
                action: 'BLUR_IMAGE_ERROR',
                details: `COOR=(${x}, ${y}) | AREA=${w}x${h}px | BLURPX=${state.blurPx} | ERROR: ${error.message}`
            })
        }).catch(err => console.error("에러 로그 전송 실패", err));
        
        alert("이미지를 흐리게 하는 중 오류가 발생했습니다.")
    }
}