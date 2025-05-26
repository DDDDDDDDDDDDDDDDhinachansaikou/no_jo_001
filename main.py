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
    st.header("查詢可配對使用者")
    
    df = get_df()
    user_id = st.session_state.get("user_id")

    if user_id is None:
        st.warning("請先登入")
    else:
        user_row = df[df["user_id"] == user_id]
        if user_row.empty:
            st.error("無法找到登入使用者")
        else:
            my_dates = user_row.iloc[0]["available_dates"]
            if pd.isna(my_dates) or my_dates == "":
                st.info("你尚未登記任何可用時間")
            else:
                my_dates = set(my_dates.split(","))
                st.write(f"你的可用日期：{', '.join(my_dates)}")
                st.subheader("以下是與你有相同可用日期的使用者：")

                for i, row in df.iterrows():
                    if row["user_id"] == user_id:
                        continue  # 跳過自己

                    other_dates = row.get("available_dates", "")
                    if not isinstance(other_dates, str) or not other_dates.strip():
                        continue

                    overlap = set(other_dates.split(",")) & my_dates
                    if overlap:
                        st.markdown(f"✅ **{row['user_id']}**（共同可用日：{', '.join(sorted(overlap))}）")
                        display_calendar_view(row["user_id"])


elif selected_page == "送出好友申請":
    st.header("送出好友申請")

    target_id = st.text_input("輸入對方的使用者 ID")

    if st.button("送出好友申請"):
        if not target_id:
            st.warning("請輸入對方 ID")
        elif target_id == st.session_state.get("user_id"):
            st.warning("不能對自己送出好友申請")
        else:
            success, msg = send_friend_request(st.session_state["user_id"], target_id)
            if success:
                st.success(f"已送出好友申請給 {target_id}")
            else:
                st.error(f"送出失敗：{msg}")


elif selected_page == "回應好友申請":
    st.header("回應好友申請")

    df = get_df()
    user_id = st.session_state.get("user_id")
    user_row = df[df["user_id"] == user_id]

    if user_row.empty:
        st.warning("找不到使用者資料")
    else:
        requests_str = user_row.iloc[0].get("friend_requests", "")
        requests = [r for r in requests_str.split(",") if r.strip()]

        if not requests:
            st.info("你目前沒有任何好友申請")
        else:
            st.write("你收到的好友申請：")
            for requester in requests:
                col1, col2 = st.columns([3, 2])

                with col1:
                    st.write(f"使用者 `{requester}` 想加你好友")

                with col2:
                    accept = st.button("接受", key=f"accept_{requester}")
                    reject = st.button("拒絕", key=f"reject_{requester}")

                if accept:
                    success, msg = respond_to_request(user_id, requester, accept=True)
                    if success:
                        st.success(f"已接受 {requester} 的好友申請")
                        st.rerun()

                if reject:
                    success, msg = respond_to_request(user_id, requester, accept=False)
                    if success:
                        st.info(f"已拒絕 {requester} 的好友申請")
                        st.rerun()

elif selected_page == "查看好友清單":
    st.header("好友清單")

    df = get_df()
    user_id = st.session_state.get("user_id")
    user_row = df[df["user_id"] == user_id]

    if user_row.empty:
        st.warning("找不到使用者資料")
    else:
        friends_str = user_row.iloc[0].get("friends", "")
        friends = [f for f in friends_str.split(",") if f.strip()]

        if not friends:
            st.info("你目前尚未有好友")
        else:
            for fid in friends:
                st.subheader(f"好友：{fid}")
                display_calendar_view(fid)

elif selected_page == "群組管理":
    st.header("群組管理")
    user_id = st.session_state.get("user_id")

    render_group_management_ui(user_id)

elif selected_page == "登出":
    st.session_state.clear()
    st.success("你已成功登出")
    st.rerun()
