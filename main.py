import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx
import time

# ✅ 每 10 秒重新整理一次（10000 毫秒）
st_autorefresh = st.experimental_data_editor if hasattr(st, "experimental_data_editor") else st.empty
st_autorefresh()
st.experimental_rerun = getattr(st, "experimental_rerun", lambda: None)

# 以下載入主畫面
from ui_module import render_ui
render_ui()
