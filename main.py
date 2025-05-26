# Main application logic without UI
from ui_module import *

from group import create_group, invite_friend_to_group, list_groups_for_user, show_group_availability, render_group_management_ui
import streamlit as st
from auth import authenticate_user, register_user
from availability import update_availability, find_users_by_date
from friendship import send_friend_request, accept_friend_request, reject_friend_request, list_friend_requests, list_friends, show_friend_list_with_availability
from sheets import get_df
import pandas as pd
from datetime import date
from calendar_tools import display_calendar_view


# 初始化 session state

# 自動跳轉處理

# 功能選單
if st.session_state.get("user_id"):
    page_options = ["登記可用時間", "查詢可配對使用者", "送出好友申請", "回應好友申請", "查看好友清單", "群組管理", "登出"]
    page_options.insert(-1, "管理介面")
else:
    page_options = ["登入", "註冊"]

# 頁面對應
if selected_page == "註冊":
        success, msg = register_user(uid, pw)

elif selected_page == "登入":
    st.header("登入")

    uid = st.text_input("使用者 ID")
    pw = st.text_input("密碼", type="password")

    if st.button("登入"):
        if authenticate_user(uid, pw):
            st.success(f"歡迎回來，{uid}！")
            st.session_state["user_id"] = uid
            st.rerun()  # 重新整理頁面以更新狀態
        else:
            st.error("帳號或密碼錯誤，請重新輸入")

elif selected_page == "登記可用時間":
    date_range = pd.date_range(date.today(), periods=30).tolist()

elif selected_page == "查詢可配對使用者":
    df = get_df()
    display_calendar_view(target)
    date_range = pd.date_range(date.today(), periods=30).tolist()
    for d in selected:

elif selected_page == "送出好友申請":

elif selected_page == "回應好友申請":
    if not requests:
    for requester in requests:
        with col1:
        with col2:

elif selected_page == "查看好友清單":
    if not friends:



    df = get_df()
    for uid in df["user_id"]:
            display_calendar_view(uid)

elif selected_page == "群組管理":

elif selected_page == "登出":

