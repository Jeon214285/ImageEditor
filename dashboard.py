import os
import json
import numpy as np
from pathlib import Path
import gspread
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

load_dotenv()

SCOPE = {
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
}

GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "google_key.json")

@st.cache_resource
def get_spreadsheet():
    credentials = Credentials.from_service_account_file(
        GOOGLE_SERVICE_ACCOUNT_FILE,
        scopes=SCOPE
    )

    client = gspread.authorize(credentials)
    return client.open (GOOGLE_SHEET_NAME)

def load_sheet(sheet_name: str) -> pd.DataFrame:
    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet(sheet_name)
    records = worksheet.get_all_records()
    return pd.DataFrame(records)

def parse_score(score_val):
    if pd.isna(score_val) or str(score_val).strip() == "":
        return np.nan
    try:
        # JSON 문자열인 경우
        if isinstance(score_val, str) and score_val.startswith("["):
            scores = json.loads(score_val)
            if isinstance(scores, list) and len(scores) > 0:
                return np.mean(scores) # 한 프레임 내 객체들의 평균 confidence
        # 단일 숫자인 경우
        return float(score_val)
    except Exception:
        return np.nan

st.set_page_config(page_title="MLOps Dashboard", layout="wide")
st.title("MLOps Monitoring Dashboard")

if not GOOGLE_SHEET_NAME:
    st.error("GOOGLE_SHEET_NAME 환경변수가 설정되지 않았습니다.")
    st.stop()

if not Path(GOOGLE_SERVICE_ACCOUNT_FILE).exists():
    st.error(f"서비스 계정 파일을 찾을 수 없습니다: {GOOGLE_SERVICE_ACCOUNT_FILE}")
    st.stop()

try:
    pred_df = load_sheet("prediction_logs")
    feedback_df = load_sheet("feedback_logs")
except Exception as e:
    st.error(f"Google Sheet를 읽는 중 오류가 발생했습니다: {e}")
    st.stop()

st.subheader("운영 지표")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Requests", len(pred_df))

if len(pred_df) > 0:
    pred_df["mean_score"] = pred_df["score"].apply(parse_score)

    valid_scores = pred_df["mean_score"].dropna()
    avg_confidence = valid_scores.mean() if not valid_scores.empty else 0
    low_confidence_count = len(valid_scores[valid_scores < 0.70])

    col2.metric("Average Confidence", round(avg_confidence, 4))
    col3.metric("Low Confidence", low_confidence_count)

    if "serving_model" in pred_df.columns:
        canary_count = len(pred_df[pred_df["serving_model"] == "challenger"])
    else:
        canary_count = 0
    col4.metric("Canary Requests", canary_count)
    
    st.subheader("Confidence Trend")
    trend_df = pred_df.reset_index()
    st.line_chart(trend_df, x="index", y="mean_score")

    st.subheader("Serving Model Count")
    if "serving_model" in pred_df.columns:
        st.bar_chart(pred_df["serving_model"].value_counts())

    st.subheader("Recent Predictions")
    st.dataframe(pred_df.tail(20), use_container_width=True)

else:
  col2.metric("Average Confidence", "-")
  col3.metric("Low Confidence", 0)
  col4.metric("Canary Requests", 0)
  st.info("아직 예측 로그가 없습니다.")

st.subheader("User Feedback")

col5, col6, col7 = st.columns(3)
col5.metric("Feedback Count", len(feedback_df))

if len(feedback_df) > 0:
    fp_count = len(feedback_df[feedback_df["reason"].str.contains("Positive", na=False, case=False)])
    fn_count = len(feedback_df[feedback_df["reason"].str.contains("Negative", na=False, case=False)])
    
    col6.metric("False Positives", fp_count)
    col7.metric("False Negatives", fn_count)

    st.subheader("Feedback by Serving Model")
    st.bar_chart(feedback_df["serving_model"].value_counts())

    st.subheader("Feedback Label Distribution")
    st.bar_chart(feedback_df["reason"].value_counts())

    st.subheader("Recent Feedback")
    st.dataframe(feedback_df.tail(20), use_container_width=True)
        
else:
    col6.metric("False Positives", 0)
    col7.metric("False Negatives", 0)
    st.info("아직 사용자 피드백이 없습니다.")