import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx
import time

from streamlit_extras.st_autorefresh import st_autorefresh
st_autorefresh(interval=10000, key="auto_refresh")  # 每 10 秒刷新一次


# 以下載入主畫面
from ui_module import render_ui
render_ui()
