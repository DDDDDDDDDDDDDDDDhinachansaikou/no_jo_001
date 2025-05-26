import streamlit as st
import pandas as pd
from datetime import date, datetime
from storage_module import get_event_rows, add_event_row, update_event_participation, get_df, save_df

def delete_event(event_idx):
    df = get_df()
    df = df.drop(index=event_idx).reset_index(drop=True)
    save_df(df)
    return True

def render_group_events_ui(group_name, user_id):
    st.markdown("### 群組活動／日程表")

    # 活動建立區（新增活動時包含活動概述）
    with st.form(key=f"event_form_{group_name}"):
        event_title = st.text_input("活動標題", key=f"event_title_{group_name}")
        event_summary = st.text_area("活動概述", key=f"event_summary_{group_name}")
        event_date = st.date_input("活動日期", key=f"event_date_{group_name}")
        submit_btn = st.form_submit_button("建立活動")
        if submit_btn:
            if event_title:
                add_event_row(group_name, event_title, event_date, user_id, event_summary)
                st.success("活動建立成功")
                st.rerun()
            else:
                st.warning("請輸入活動標題")

    # 列出活動，並自動過濾掉過期活動
    group_events = get_event_rows(group_name)
    if group_events.empty:
        st.info("本群組目前沒有活動")
        return

    today_str = date.today().strftime("%Y-%m-%d")
    # 篩選未過期活動
    def not_expired(event_row):
        # 支援 event_date 為 datetime 或字串
        if isinstance(event_row['event_date'], datetime):
            event_date_str = event_row['event_date'].strftime("%Y-%m-%d")
        else:
            event_date_str = str(event_row['event_date'])
        return event_date_str >= today_str

    events_to_show = group_events[group_events.apply(not_expired, axis=1)]
    if events_to_show.empty:
        st.info("本群組目前沒有活動")
        return

    for idx, row in events_to_show.iterrows():
        st.markdown(f"**{row['event_title']}**（{row['event_date']}）")
        # 顯示活動概述
        st.markdown(f"**活動概述：**{row.get('event_summary', '')}")

        yes_list = [x for x in str(row['participants_yes']).split(",") if x]
        no_list = [x for x in str(row['participants_no']).split(",") if x]
        user_is_yes = user_id in yes_list
        user_is_no = user_id in no_list

        col1, col2, col3, col4 = st.columns([1, 1, 2, 2])
        # 主辦人可取消活動
        with col1:
            if row["created_by"] == user_id:
                if st.button("取消活動", key=f"cancel_{group_name}_{idx}"):
                    delete_event(idx)
                    st.success("活動已取消")
                    st.rerun()
        # 兩個按鈕永遠可切換
        with col2:
            if st.button("參加", key=f"join_{group_name}_{idx}"):
                if not user_is_yes:
                    yes_list.append(user_id)
                if user_id in no_list:
                    no_list.remove(user_id)
                update_event_participation(idx, yes_list, no_list)
                st.success("已標記參加")
                st.rerun()
        with col3:
            if st.button("不參加", key=f"notjoin_{group_name}_{idx}"):
                if not user_is_no:
                    no_list.append(user_id)
                if user_id in yes_list:
                    yes_list.remove(user_id)
                update_event_participation(idx, yes_list, no_list)
                st.success("已標記不參加")
                st.rerun()
        with col4:
            st.markdown(f"參加：{', '.join(yes_list) if yes_list else '無'}")
            st.markdown(f"不參加：{', '.join(no_list) if no_list else '無'}")

        # 顯示自己目前狀態
        if user_is_yes:
            st.info("你已選擇參加此活動")
        elif user_is_no:
            st.warning("你已選擇不參加此活動")
        else:
            st.markdown("尚未表態參加與否")

        # 主辦人可下載完整名單
        if row["created_by"] == user_id:
            st.markdown("---")
            st.markdown("#### 參加名單下載/檢視")

            yes_df = pd.DataFrame({"user_id": yes_list}) if yes_list else pd.DataFrame({"user_id": ["無"]})
            no_df = pd.DataFrame({"user_id": no_list}) if no_list else pd.DataFrame({"user_id": ["無"]})

            st.markdown("##### 參加者")
            st.dataframe(yes_df, use_container_width=True)
            st.download_button(
                label="下載參加者名單 (csv)",
                data=yes_df.to_csv(index=False).encode("utf-8"),
                file_name=f"{row['event_title']}_participants_yes.csv",
                mime="text/csv",
                key=f"dl_yes_{group_name}_{idx}"
            )

            st.markdown("##### 不參加者")
            st.dataframe(no_df, use_container_width=True)
            st.download_button(
                label="下載不參加者名單 (csv)",
                data=no_df.to_csv(index=False).encode("utf-8"),
                file_name=f"{row['event_title']}_participants_no.csv",
                mime="text/csv",
                key=f"dl_no_{group_name}_{idx}"
            )

    # 自動刪除過期活動
    expired_idx = group_events[~group_events.apply(not_expired, axis=1)].index
    if not expired_idx.empty:
        df = get_df()
        df = df.drop(index=expired_idx).reset_index(drop=True)
        save_df(df)
