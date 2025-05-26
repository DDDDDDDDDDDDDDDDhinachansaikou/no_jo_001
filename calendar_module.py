import streamlit as st
import calendar
import time
from datetime import datetime
from sheets import get_df

def display_calendar_view(user_id):
    today = datetime.today()
    now = time.time()

    # 狀態 key 命名
    year_key = f"{user_id}_show_year"
    month_key = f"{user_id}_show_month"
    last_click_key = f"{user_id}_last_click"
    last_user_key = "last_display_user"

    # 初始化
    if last_user_key not in st.session_state or st.session_state[last_user_key] != user_id:
        st.session_state[year_key] = today.year
        st.session_state[month_key] = today.month
        st.session_state[last_click_key] = 0.0
        st.session_state[last_user_key] = user_id

    # 防止多次快速點擊
    can_click = now - st.session_state[last_click_key] > 1.0

    # 月份控制
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← 上一個月", key=f"prev_btn_{user_id}") and can_click:
            st.session_state[last_click_key] = now
            if st.session_state[month_key] == 1:
                st.session_state[month_key] = 12
                st.session_state[year_key] -= 1
            else:
                st.session_state[month_key] -= 1
    with col3:
        if st.button("下一個月 →", key=f"next_btn_{user_id}") and can_click:
            st.session_state[last_click_key] = now
            if st.session_state[month_key] == 12:
                st.session_state[month_key] = 1
                st.session_state[year_key] += 1
            else:
                st.session_state[month_key] += 1

    year = st.session_state[year_key]
    month = st.session_state[month_key]

    # 資料抓取與檢查
    df = get_df()
    user_data = df[df["user_id"] == user_id]
    if user_data.empty:
        st.warning(f"{user_id} 無資料")
        return

    available_raw = user_data.iloc[0].get("available_dates", "")
    if not isinstance(available_raw, str):
        available_raw = ""
    available = set(d.strip() for d in available_raw.split(",") if d.strip())

    cal = calendar.Calendar(firstweekday=0)
    month_days = list(cal.itermonthdays(year, month))

    week_headers = ['一', '二', '三', '四', '五', '六', '日']
    table = "<table style='border-collapse: collapse; width: 100%; text-align: center;'>"
    table += f"<caption style='text-align:center; font-weight:bold; padding: 8px'>{year} 年 {month} 月</caption>"
    table += "<tr>" + "".join(f"<th>{d}</th>" for d in week_headers) + "</tr><tr>"

    day_counter = 0
    for day in month_days:
        if day == 0:
            table += "<td></td>"
        else:
            date_str = f"{year}-{month:02d}-{day:02d}"
            if date_str in available:
                table += f"<td style='background-color:#b2fab4;border:1px solid #ccc;padding:5px'>{day}</td>"
            else:
                table += f"<td style='border:1px solid #ccc;padding:5px;color:#ccc'>{day}</td>"
        day_counter += 1
        if day_counter % 7 == 0:
            table += "</tr><tr>"
    table += "</tr></table>"

    st.markdown(table, unsafe_allow_html=True)
