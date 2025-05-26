# This module contains UI rendering functions
st.title("NO_JO")
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = ""
if 'page' not in st.session_state:
    st.session_state.page = "登入"
if 'rerun_triggered' not in st.session_state:
    st.session_state.rerun_triggered = False
if st.session_state.page == "登入成功" and not st.session_state.rerun_triggered:
    st.session_state.page = "登記可用時間"
    st.session_state.rerun_triggered = True
    st.rerun()
if st.session_state.authenticated:
    if st.session_state.user_id == "GM":
selected_page = st.sidebar.radio("功能選單", page_options)
st.session_state.page = selected_page
    uid = st.text_input("新帳號")
    pw = st.text_input("密碼", type="password")
    if st.button("註冊"):
        st.success(msg) if success else st.error(msg)
    uid = st.text_input("帳號")
    pw = st.text_input("密碼", type="password")
    if st.button("登入"):
            st.session_state.authenticated = True
            st.session_state.user_id = uid
            st.success("登入成功")
            st.session_state.page = "登入成功"
            st.session_state.rerun_triggered = False
            st.rerun()
            st.error("帳號或密碼錯誤")
    selected = st.multiselect("選擇可用日期", date_range, format_func=lambda d: d.strftime("%Y-%m-%d"))
    if st.button("更新"):
        update_availability(st.session_state.user_id, [d.strftime("%Y-%m-%d") for d in selected])
    st.header("查詢使用者空閒日曆")
    other_users = df[df["user_id"] != st.session_state.user_id]["user_id"].tolist()
    target = st.selectbox("選擇使用者", other_users)
    selected = st.multiselect("查詢日期", date_range, format_func=lambda d: d.strftime("%Y-%m-%d"))
        users = find_users_by_date(d.strftime("%Y-%m-%d"), st.session_state.user_id)
        st.write(f"{d.strftime('%Y-%m-%d')}: {', '.join(users) if users else '無'}")
    target = st.text_input("輸入對方 ID")
    if st.button("送出好友申請"):
        msg = send_friend_request(st.session_state.user_id, target)
        st.info(msg)
    requests = list_friend_requests(st.session_state.user_id)
        st.info("目前沒有好友申請")
        col1, col2 = st.columns([2, 1])
            st.write(f"來自 {requester} 的好友申請")
            if st.button("接受", key=f"accept_{requester}"):
                msg = accept_friend_request(st.session_state.user_id, requester)
                st.success(msg)
                st.rerun()
            if st.button("拒絕", key=f"reject_{requester}"):
                msg = reject_friend_request(st.session_state.user_id, requester)
                st.info(msg)
                st.rerun()
    show_friend_list_with_availability(st.session_state.user_id)
    friends = list_friends(st.session_state.user_id)
        st.info("您目前尚無好友")
elif selected_page == "管理介面" and st.session_state.user_id == "GM":
    st.subheader("GM 管理介面：全員空閒日曆")
        with st.expander(uid):
    st.subheader("GM 管理介面")
    st.dataframe(df)
    render_group_management_ui(st.session_state.user_id)
    st.session_state.authenticated = False
    st.session_state.user_id = ""
    st.session_state.page = "登入"
    st.success("已登出")
    st.rerun()
