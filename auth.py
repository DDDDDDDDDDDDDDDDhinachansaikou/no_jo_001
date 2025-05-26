
import re
import pandas as pd
from sheets import get_df, save_df

def register_user(user_id, password):
    user_id, password = str(user_id), str(password)
    if len(password) < 6 or not re.search(r'[A-Za-z]', password):
        return False, "密碼必須至少 6 個字元，且包含英文字母"
    df = get_df()
    if user_id in df['user_id'].values:
        return False, "使用者 ID 已存在"
    new_entry = pd.DataFrame([{
        'user_id': user_id,
        'password': password,
        'available_dates': '',
        'friends': '',
        'friend_requests': ''
    }])
    df = pd.concat([df, new_entry], ignore_index=True)
    save_df(df)
    return True, "註冊成功"

def authenticate_user(user_id, password):
    df = get_df()
    return not df[(df['user_id'] == str(user_id)) & (df['password'] == str(password))].empty
