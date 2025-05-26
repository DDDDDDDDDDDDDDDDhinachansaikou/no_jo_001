# main.py — 主控邏輯（UI 行為交由 ui_module 處理）
import streamlit as st

# UI 控制與頁面邏輯（主選單與所有互動都在此模組）
from ui_module import *

# 資料與功能模組（行為邏輯）
from auth import authenticate_user, register_user
from availability import update_availability, find_users_by_date
from calendar_module import display_calendar_view
from friend_module import (
    send_friend_request, accept_friend_request, reject_friend_request,
    list_friend_requests, list_friends,
    show_friend_list_with_availability
)
from group_module import (
    render_group_management_ui
)
from storage_module import get_df, save_df
import pandas as pd
from datetime import date
