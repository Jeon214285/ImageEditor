import { state } from './state.js'

export function sendFaceFeedback(reason) {
    if (!state.detectFaces) {
        alert("얼굴 탐지를 먼저 실행해주세요.");
        return;
    }

    fetch("/feedback", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            pred_class: "face",
            coordinate: state.detectFaces,
            score: state.faceScores,
            reason: reason,
            serving_model: state.serving_model
        })
    })
    .then(response => {
        if (response.ok) {
            alert(`피드백 전송이 완료되었습니다.`);
            console.log("피드백 전송 성공");
        } else {
            alert(`피드백 전송 실패 (상태 코드: ${response.status})`);
        }
    })
    .catch(error => {
        console.error("피드백 전송 중 통신 에러:", error);
        alert("서버와 통신 중 오류가 발생했습니다.");
    });
}

export function sendPlateFeedback(reason) {
    if (!state.detectPlates) {
        alert("차량 번호판 탐지를 먼저 실행해주세요.");
        return;
    }

    fetch("/feedback", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            pred_class: "plate",
            coordinate: state.detectPlates,
            score: state.plateScores,
            reason: reason,
            serving_model: state.serving_model
        })
    })
    .then(response => {
        if (response.ok) {
            alert(`피드백전송이 완료되었습니다.`);
            console.log("피드백 전송 성공");
        } else {
            alert(`피드백 전송 실패 (상태 코드: ${response.status})`);
        }
    })
    .catch(error => {
        console.error("피드백 전송 중 통신 에러:", error);
        alert("서버와 통신 중 오류가 발생했습니다.");
    });
}