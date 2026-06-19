import logging
from datetime import datetime
from app.config import LOW_CONFIDENCE_LIMIT
from issue import create_github_issue

logger = logging.getLogger(__name__)

_state = {
    "low_confidence_count": 0,
    "samples": [],
    "issue_created": False
}

def update_issue_state(score: float, threshold: float):
    if score < threshold:
        _state["low_confidence_count"] += 1
        _state['samples'].append({
            "score": score,
            "time": datetime.now().isoformat(timespec="seconds")
        })
    
    # threshold를 넘으면 issue 생성
    if (
        _state["low_confidence_count"] >= LOW_CONFIDENCE_LIMIT
        and not _state["issue_created"]
    ):
        create_drift_issue()
        _state["issue_created"] = True
    return _state

def create_drift_issue():
    samples = _state['samples'][-5:]
    title = "[MLOps] Drift suspected (low confidence accumulation)"
    body = f"""
            ## Drift Detection Report
            Low-confidence predictions accumulated
            - count: {_state['low_confidence_count']}
            - threshold: {LOW_CONFIDENCE_LIMIT}

            ## Recent Samples
            """
    for s in samples:
        body += f"- confidence score: {s['score']}\n"
    body += """
            ## Action
            - Please review data
            - Decide whether retraining is needed
            """
    create_github_issue(title, body, logger)