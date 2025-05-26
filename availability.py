
from sheets import get_df, save_df

def update_availability(user_id, available_dates):
    df = get_df()
    date_str = ','.join(available_dates)
    df.loc[df['user_id'] == user_id, 'available_dates'] = date_str
    save_df(df)
    return date_str

def find_users_by_date(date, current_user_id):
    df = get_df()
    return df[(df['available_dates'].str.contains(date, na=False)) & 
              (df['user_id'] != current_user_id)]['user_id'].tolist()
