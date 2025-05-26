from calendar_module import display_calendar_view
from storage_module import get_df, save_df
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

def send_friend_request(current_user, target_user):
    if current_user == target_user:
        return "不能傳送好友申請給自己"

    df = get_df()

    if target_user not in df["user_id"].values:
        return "該使用者不存在"

    curr_friends_raw = df.loc[df["user_id"] == current_user, "friends"].values[0]
    curr_friends_set = set(f.strip() for f in curr_friends_raw.split(",") if f.strip())

    if target_user in curr_friends_set:
        return "對方已經是你的好友"

    target_requests = df.loc[df["user_id"] == target_user, "friend_requests"].values[0]
    target_requests_set = set(target_requests.split(",")) if target_requests else set()

    if current_user in target_requests_set:
        return "已送出好友申請 請等待對方回應"

    target_requests_set.add(current_user)
    df.loc[df["user_id"] == target_user, "friend_requests"] = ",".join(sorted(target_requests_set))
    save_df(df)
    return "好友申請已送出"

def accept_friend_request(user_id, requester):
    df = get_df()
    idx = df[df['user_id'] == user_id].index[0]
    friends = set(df.at[idx, 'friends'].split(',')) if df.at[idx, 'friends'] else set()
    friends.add(requester)
    df.at[idx, 'friends'] = ','.join(sorted(friends))

    req_idx = df[df['user_id'] == requester].index[0]
    req_friends = set(df.at[req_idx, 'friends'].split(',')) if df.at[req_idx, 'friends'] else set()
    req_friends.add(user_id)
    df.at[req_idx, 'friends'] = ','.join(sorted(req_friends))

    requests = set(df.at[idx, 'friend_requests'].split(',')) if df.at[idx, 'friend_requests'] else set()
    requests.discard(requester)
    df.at[idx, 'friend_requests'] = ','.join(sorted(requests))

    save_df(df)
    return "您已與對方成為好友"

def reject_friend_request(user_id, requester):
    df = get_df()
    idx = df[df['user_id'] == user_id].index[0]
    requests = set(df.at[idx, 'friend_requests'].split(',')) if df.at[idx, 'friend_requests'] else set()
    requests.discard(requester)
    df.at[idx, 'friend_requests'] = ','.join(sorted(requests))
    save_df(df)
    return "已拒絕好友申請"

def list_friend_requests(user_id):
    df = get_df()
    idx = df[df['user_id'] == user_id].index[0]
    requests = df.at[idx, 'friend_requests']
    return sorted(list(filter(None, requests.split(','))))

def list_friends(user_id):
    df = get_df()
    idx = df[df['user_id'] == user_id].index[0]
    friends = df.at[idx, 'friends']
    return sorted(list(filter(None, friends.split(','))))

def show_friends_availability(user_id):
    df = get_df()
    idx = df[df['user_id'] == user_id].index[0]
    friends = df.at[idx, 'friends']
    friends = list(filter(None, friends.split(',')))
    if not friends:
        st.info("目前尚無好友")
        return

    st.subheader("好友的空閒日期")
    if "friend_view_states" not in st.session_state:
        st.session_state.friend_view_states = {}

    today = datetime.today()
    next_30_days = [today + timedelta(days=i) for i in range(30)]
    date_labels = [d.strftime("%Y-%m-%d") for d in next_30_days]

    for friend in friends:
        if friend not in st.session_state.friend_view_states:
            st.session_state.friend_view_states[friend] = False

        with st.expander(f"{friend}", expanded=st.session_state.friend_view_states[friend]):
            friend_data = df[df['user_id'] == friend]
            if not friend_data.empty:
                dates = friend_data.iloc[0]['available_dates']
                available_set = set(d.strip() for d in dates.split(',') if d.strip())

                calendar_df = pd.DataFrame({
                    "日期": date_labels,
                    "可用": ["是" if d in available_set else "否" for d in date_labels]
                })
                st.table(calendar_df)

                fig = go.Figure(go.Bar(
                    x=date_labels,
                    y=[1 if d in available_set else 0 for d in date_labels],
                    marker_color=["green" if d in available_set else "lightgray" for d in date_labels],
                ))
                fig.update_layout(
                    title="未來可用日",
                    xaxis_title="日期",
                    yaxis=dict(showticklabels=False),
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)

def show_friend_list_with_availability(user_id):
    df = get_df()
    friends = list_friends(user_id)

    if not friends:
        st.info("您目前尚無好友")
    else:
        selected_friend = st.selectbox("選擇好友查看空閒時間", friends)

        if selected_friend:
            friend_data = df[df["user_id"] == selected_friend]

            try:
                display_calendar_view(selected_friend)
            except Exception as e:
                st.error(f"{selected_friend} 的日曆顯示失敗：{e}")

            if not friend_data.empty:
                dates = friend_data.iloc[0].get("available_dates", "")
                if not isinstance(dates, str):
                    dates = ""
                date_list = [d.strip() for d in dates.split(",") if d.strip()]
                if date_list:
                    st.markdown(f"**空閒時間**：{'、'.join(date_list)}")
                else:
                    st.info("尚未登記可用時間")
            else:
                st.warning("找不到該使用者資料")
                date_list = [d.strip() for d in dates.split(',')] if dates else []
                st.markdown(f" **空閒時間**：{'、'.join(date_list) if date_list else '尚未登記'}")
