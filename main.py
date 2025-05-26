import streamlit as st
import time

# 每 10 秒自動刷新頁面
if "last_refresh_time" not in st.session_state:
    st.session_state.last_refresh_time = time.time()
elif time.time() - st.session_state.last_refresh_time > 10:
    st.session_state.last_refresh_time = time.time()
    st.experimental_rerun()

# 主畫面邏輯
from ui_module import render_ui
render_ui()
