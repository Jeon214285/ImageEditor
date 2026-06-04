import { state, setCropCoordinates } from './state.js';

export function imageCut() {
    if(!state.cropCoordinates) return;
    
    let x = state.cropCoordinates.startX;
    let y = state.cropCoordinates.startY;
    let w = state.cropCoordinates.width;
    let h = state.cropCoordinates.height;

    try {
        state.context.putImageData(state.cleanImageData, 0, 0);
        let cutImageData = state.context.getImageData(x, y, w, h);

        state.canvas.width = w;
        state.canvas.height = h;

        state.context.putImageData(cutImageData, 0, 0);

        // 이미지 위치 조정
        let currentLeft = parseInt(state.canvas.style.marginLeft || 0);
        let currentTop = parseInt(state.canvas.style.marginTop || 0);

        state.canvas.style.marginLeft = (currentLeft + x) + "px";
        state.canvas.style.marginTop = (currentTop + y) + "px";

        setCropCoordinates(null);
        state.cleanImageData = state.context.getImageData(0, 0, state.canvas.width, state.canvas.height);

        // 로그 데이터 전송
        fetch('/api/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                level: 'INFO',
                action: 'CUT_IMAGE_SUCCESS',
                details: `COOR=(${x}, ${y}) | AREA=${w}x${h}px`
            })
        }).catch(err => console.error("로그 전송 실패", err));
    } catch(error) {
        fetch('/api/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                level: 'ERROR',
                action: 'CUT_IMAGE_ERROR',
                details: `COOR=(${x}, ${y}) | AREA=${w}x${h}px | ERROR=${error.message}`
            })
        }).catch(err => console.error("에러 로그 전송 실패", err));
        
        alert("이미지를 자르는 중 오류가 발생했습니다.")
    }
}