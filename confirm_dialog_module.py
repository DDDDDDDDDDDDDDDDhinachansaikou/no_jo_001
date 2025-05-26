import streamlit as st

def confirm_action(label, key=None):
    """顯示一個安全性確認區塊。若使用者勾選確認並按下按鈕才會傳回 True，否則 False。"""
    col1, col2 = st.columns([5, 1])
    with col1:
        confirmed = st.checkbox("我確認要執行這個動作，且明白後果不可逆", key=f"{key}_checkbox")
    with col2:
        do_action = st.button(label, key=f"{key}_btn")
    return confirmed and do_action
