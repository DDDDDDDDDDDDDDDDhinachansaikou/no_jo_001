import pandas as pd
import time
import streamlit as st
import gspread
from google.oauth2 import service_account

SHEET_NAME = "meeting_records"
secrets = st.secrets["gspread"]
credentials = service_account.Credentials.from_service_account_info(secrets)
scoped_credentials = credentials.with_scopes([
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
])
client = gspread.authorize(scoped_credentials)
sheet = client.open(SHEET_NAME).sheet1

@st.cache_data(ttl=60)
def get_df():
    records = sheet.get_all_records()
    df = pd.DataFrame(records)
    if df.empty:
        df = pd.DataFrame(columns=['row_type', 'user_id', 'password', 'available_dates', 'friends', 'friend_requests', 'groups', 'group_members', 'group_name', 'event_title', 'event_date', 'created_by', 'participants_yes', 'participants_no'])
    else:
        # 確保所有欄位齊全
        for col in ['row_type', 'user_id', 'password', 'available_dates', 'friends', 'friend_requests', 'groups', 'group_members', 'group_name', 'event_title', 'event_date', 'created_by', 'participants_yes', 'participants_no']:
            if col not in df.columns:
                df[col] = ''
        df = df.fillna("")
    return df

def save_df(df, cooldown=2.0):
    # 強制所有日期欄位為字串
    for col in df.columns:
        if df[col].dtype == 'datetime64[ns]' or df[col].dtype == 'datetime64[ns, UTC]':
            df[col] = df[col].dt.strftime('%Y-%m-%d')
        elif df[col].apply(lambda x: isinstance(x, (pd.Timestamp, datetime, date))).any():
            df[col] = df[col].apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, (pd.Timestamp, datetime, date)) else x)

    now = time.time()
    if now - st.session_state.get("last_save_timestamp", 0) < cooldown:
        st.warning("操作太頻繁，請稍候再試")
        return False
    df = df.fillna("")
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
    st.session_state.last_save_timestamp = now
    return True


# 活動資料操作輔助
def get_event_rows(group_name=None):
    df = get_df()
    events = df[df['row_type'] == 'event']
    if group_name is not None:
        events = events[events['group_name'] == group_name]
    return events

def add_event_row(group_name, event_title, event_date, created_by, event_summary):
    df = get_df()
    # 建議補欄位兼容
    for col in ["group_name", "event_title", "event_date", "created_by", "event_summary", "participants_yes", "participants_no"]:
        if col not in df.columns:
            df[col] = ""
    new_row = {
        "group_name": group_name,
        "event_title": event_title,
        "event_date": event_date,
        "created_by": created_by,
        "event_summary": event_summary,
        "participants_yes": "",
        "participants_no": ""
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_df(df)


def update_event_participation(event_idx, yes_list, no_list):
    df = get_df()
    df.at[event_idx, "participants_yes"] = ",".join(yes_list)
    df.at[event_idx, "participants_no"] = ",".join(no_list)
    save_df(df)
