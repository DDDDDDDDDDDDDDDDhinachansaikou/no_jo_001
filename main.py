import streamlit as st
import time

# 每 10 秒自動重新整理畫面
if "last_refresh_time" not in st.session_state:
    st.session_state.last_refresh_time = time.time()
elif time.time() - st.session_state.last_refresh_time > 10:
    st.session_state.last_refresh_time = time.time()
    st.experimental_rerun()

# 載入 UI
from ui_module import render_ui
render_ui()
