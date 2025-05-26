import streamlit as st
import pandas as pd
from datetime import date, datetime
from storage_module import get_df, save_df
import uuid

# 建立活動
def add_event_row(group_name, event_title, event_date, created_by, event_summary):
    df = get_df()
    for col in ["row_type", "activity_id", "group_name", "event_title", "event_date", "created_by", "event_summary", "participants_yes", "participants_no"]:
        if col not in df.columns:
            df[col] = ""
    new_row = {
        "row_type": "event",
        "activity_id": str(uuid.uuid4()),
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

# 查詢活動（自動排除過期活動，並清理資料庫）
def get_event_rows(group_name=None, auto_clean=True):
    df = get_df()
    if 'row_type' not in df.columns:
        return pd.DataFrame()
    events = df[df['row_type'] == 'event']
    today_str = date.today().strftime("%Y-%m-%d")
    # 篩選群組
    if group_name is not None:
        events = events[events['group_name'] == group_name]
    # 自動移除過期活動
    if auto_clean:
        valid_idx = events[events["event_date"] >= today_str].index
        expired_idx = events[events["event_date"] < today_str].index
        if len(expired_idx) > 0:
            df = df.drop(expired_idx)
            save_df(df)
        return events.loc[valid_idx]
    else:
        return events

# 取得單一活動資料
def get_event_by_id(activity_id):
    df = get_df()
    rows = df[df['activity_id'] == activity_id]
    if rows.empty:
        return None
    return rows.iloc[0]

# 更新參加/不參加名單
def update_event_participation_by_id(activity_id, yes_list, no_list):
    df = get_df()
    idx_list = df[df['activity_id'] == activity_id].index
    if not idx_list.empty:
        idx = idx_list[0]
        df.at[idx, "participants_yes"] = ",".join(yes_list)
        df.at[idx, "participants_no"] = ",".join(no_list)
        save_df(df)

# 刪除活動
def delete_event_by_id(activity_id):
    df = get_df()
    df = df[df['activity_id'] != activity_id].reset_index(drop=True)
    save_df(df)
    return True

# UI: 活動清單渲染（for群組活動頁）
def render_group_events_ui(group_name, user_id):
    st.subheader(f"{group_name} 群組活動")
    # 活動建立 UI
    with st.expander("建立新活動"):
        event_title = st.text_input("活動名稱", key=f"title_{group_name}")
        event_date = st.date_input("活動日期", key=f"date_{group_name}")
        event_summary = st.text_area("活動概述", key=f"summary_{group_name}")
        if st.button("建立活動", key=f"add_{group_name}"):
            if event_title and event_date:
                add_event_row(
                    group_name,
                    event_title,
                    event_date.strftime("%Y-%m-%d"),
                    user_id,
                    event_summary
                )
                st.success("活動已建立")
                st.rerun()
            else:
                st.error("活動名稱與日期必填")

    # 活動清單（自動略過過期活動）
    events_to_show = get_event_rows(group_name)
    for idx, row in events_to_show.iterrows():
        activity_id = row['activity_id']
        st.markdown(f"**活動名稱：{row['event_title']}**")
        st.markdown(f"活動日期：{row['event_date']}")
        st.markdown(f"主辦人：{row['created_by']}")
        st.markdown(f"活動說明：{row['event_summary']}")
        yes_list = [x for x in str(row['participants_yes']).split(",") if x]
        no_list = [x for x in str(row['participants_no']).split(",") if x]
        is_owner = (row['created_by'] == user_id)

        # 主辦人可取消活動與下載名單
        if is_owner:
            c1, c2 = st.columns(2)
            with c1:
                if st.button("取消活動", key=f"cancel_{activity_id}"):
                    delete_event_by_id(activity_id)
                    st.success("活動已取消")
                    st.rerun()
            with c2:
                df_download = pd.DataFrame({
                    "參加者": yes_list,
                    "不參加者": no_list
                })
                st.download_button("下載CSV", df_download.to_csv(index=False).encode("utf-8"), file_name=f"{group_name}_{row['event_title']}_名單.csv")

        # 只有沒選過的人才能選
        if user_id not in yes_list and user_id not in no_list:
            c1, c2 = st.columns(2)
            with c1:
                if st.button("參加", key=f"join_{activity_id}"):
                    yes_list.append(user_id)
                    update_event_participation_by_id(activity_id, yes_list, no_list)
                    st.success("已標記參加")
                    st.rerun()
            with c2:
                if st.button("不參加", key=f"notjoin_{activity_id}"):
                    no_list.append(user_id)
                    update_event_participation_by_id(activity_id, yes_list, no_list)
                    st.success("已標記不參加")
                    st.rerun()
        elif user_id in yes_list:
            st.info("你已選擇參加")
            if st.button("取消參加", key=f"leave_yes_{activity_id}"):
                yes_list.remove(user_id)
                update_event_participation_by_id(activity_id, yes_list, no_list)
                st.success("已取消參加")
                st.rerun()
        elif user_id in no_list:
            st.info("你已選擇不參加")
            if st.button("重新選擇", key=f"leave_no_{activity_id}"):
                no_list.remove(user_id)
                update_event_participation_by_id(activity_id, yes_list, no_list)
                st.success("已取消不參加")
                st.rerun()

        # 展示名單
        with st.expander("目前參加名單"):
            st.write("參加：", yes_list if yes_list else "尚無人參加")
            st.write("不參加：", no_list if no_list else "尚無人標記不參加")
        st.markdown("---")
