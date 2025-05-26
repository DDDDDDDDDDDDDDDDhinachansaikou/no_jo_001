import streamlit as st
from storage_module import get_event_rows, add_event_row, update_event_participation

def render_group_events_ui(group_name, user_id):
    st.markdown("### 群組活動／日程表")

    # 新增活動
    with st.expander("建立新活動"):
        event_title = st.text_input("活動標題", key=f"event_title_{group_name}")
        event_date = st.date_input("活動日期", key=f"event_date_{group_name}")
        if st.button("建立活動", key=f"create_event_{group_name}"):
            if event_title:
                add_event_row(group_name, event_title, event_date, user_id)
                st.success("活動建立成功")
                st.rerun()
            else:
                st.warning("請輸入活動標題")

    # 列出活動
    group_events = get_event_rows(group_name)
    if group_events.empty:
        st.info("本群組目前沒有活動")
        return

    for idx, row in group_events.iterrows():
        st.markdown(f"**{row['event_title']}**（{row['event_date']}）")
        yes_list = [x for x in row['participants_yes'].split(",") if x]
        no_list = [x for x in row['participants_no'].split(",") if x]

        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button("參加", key=f"join_{group_name}_{idx}"):
                if user_id not in yes_list:
                    yes_list.append(user_id)
                if user_id in no_list:
                    no_list.remove(user_id)
                update_event_participation(idx, yes_list, no_list)
                st.success("已標記參加")
                st.rerun()
        with col2:
            if st.button("不參加", key=f"notjoin_{group_name}_{idx}"):
                if user_id not in no_list:
                    no_list.append(user_id)
                if user_id in yes_list:
                    yes_list.remove(user_id)
                update_event_participation(idx, yes_list, no_list)
                st.success("已標記不參加")
                st.rerun()
        with col3:
            st.markdown(f"✅ 參加：{', '.join(yes_list) if yes_list else '無'}")
            st.markdown(f"❌ 不參加：{', '.join(no_list) if no_list else '無'}")
