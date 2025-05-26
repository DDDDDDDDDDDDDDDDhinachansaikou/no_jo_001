import streamlit as st

def confirm_action(label, key=None, warn_text="此動作不可復原，請再次確認！"):
    st.markdown(
        f"<div style='color:white;background:#d9534f;padding:8px 16px;margin:8px 0;border-radius:5px;'>"
        f"<b>安全性警告：</b>{warn_text}"
        f"</div>", unsafe_allow_html=True
    )
    confirmed = st.checkbox("我已充分閱讀、確認並願意執行此不可逆動作", key=f"{key}_checkbox")
    do_action = st.button(label, key=f"{key}_btn")
    return confirmed and do_action
