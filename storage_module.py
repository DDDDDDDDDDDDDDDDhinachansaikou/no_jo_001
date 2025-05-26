
import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
import time

SHEET_NAME = "meeting_records"

try:
    secrets = st.secrets["gspread"]
    credentials = service_account.Credentials.from_service_account_info(secrets)
    scoped_credentials = credentials.with_scopes([
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ])
    client = gspread.authorize(scoped_credentials)
    sheet = client.open(SHEET_NAME).sheet1
except Exception as e:
    st.error(f"❌ Google Sheets 初始化失敗：{e}")
    st.stop()


@st.cache_data(ttl=60)
def get_df():
    records = sheet.get_all_records()
    df = pd.DataFrame(records)
    if df.empty:
        df = pd.DataFrame(columns=['user_id', 'password', 'available_dates', 'friends', 'friend_requests'])
    else:
        for col in ['user_id', 'password', 'available_dates', 'friends', 'friend_requests']:
            if col not in df.columns:
                df[col] = ''
        df['user_id'] = df['user_id'].astype(str)
        df['password'] = df['password'].astype(str)
        df = df.fillna("")
    return df

def save_df(df, cooldown=2.0):
    now = time.time()
    if now - st.session_state.get("last_save_timestamp", 0) < cooldown:
        st.warning("操作太頻繁，請稍候再試")
        return False
    df = df.fillna("")
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
    st.session_state.last_save_timestamp = now
    return True
