import { state } from './state.js';

export function imageUpload() {
    state.imageInput.click();
}

export function setupImageInput() {
    // input의 파일이 변경되었을 때(이미지를 선택했을 때)
    state.imageInput.addEventListener('change', function(changeEvt) {
        try {
            let file = changeEvt.target.files[0];
            if (!file) return;
            
            let reader = new FileReader();

            reader.onload = function(loadEvt) {
                let img = new Image();
                
                // 이미지 로드 완료시 canvas에 그림
                img.onload = function() {
                    // 캔버스 크기를 이미지 크기로
                    state.canvas.width = img.width;
                    state.canvas.height = img.height;

                    // 이미지 그리기
                    state.context.drawImage(img, 0, 0);

                    state.canvas.style.marginLeft = "0px";
                    state.canvas.style.marginTop = "0px";

                    state.originalImageData = state.context.getImageData(0, 0, state.canvas.width, state.canvas.height);
                    state.cleanImageData = state.context.getImageData(0, 0, state.canvas.width, state.canvas.height);

                     // 이미지 업로드 완료시 로그 전송
                    fetch('/api/log', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            level: 'INFO',
                            action: 'UPLOAD_IMAGE_SUCCESS',
                            details: `FILE=${file.name} | SIZE=${(file.size / 1024).toFixed(2)}KB | RESOLUTION=${img.width}x${img.height}px`
                        })
                    }).catch(err => console.error("로그 전송 실패", err));
                }

                // 이미지를 데이터 URL로 설정하여 로드
                img.src = loadEvt.target.result;
            }
            // 파일을 읽어서 DataURL 형식으로 변환
            reader.readAsDataURL(file);
        } catch(error) {
            fetch('/api/log', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    level: 'ERROR',
                    action: 'UPLOAD_IMAGE_ERROR',
                    details: `ERROR=${error.message}`  // 에러시 정보가 없을 수 있음
                })
            }).catch(err => console.error("에러 로그 전송 실패", err));
            
            alert("이미지 업로드 중 오류가 발생했습니다.")
        }
    });
}