import streamlit as st
from storage_module import get_df, save_df
from calendar_module import display_calendar_view

def ensure_group_columns(df):
    if 'groups' not in df.columns:
        df['groups'] = ''
    if 'group_members' not in df.columns:
        df['group_members'] = ''
    return df

def create_group(user_id, group_name):
    df = get_df()
    df = ensure_group_columns(df)

    # 檢查群組名稱是否已存在
    existing_groups = set()
    for g in df["groups"].dropna():
        existing_groups.update(g.split(","))
    if group_name in existing_groups:
        return False, "該群組名稱已存在"

    # 為該用戶新增群組
    for i in df.index:
        if df.at[i, "user_id"] == user_id:
            groups = df.at[i, "groups"]
            group_members = df.at[i, "group_members"]
            new_groups = ",".join(sorted(set(groups.split(",") + [group_name]) if groups else [group_name]))
            new_members = ",".join(sorted(set(group_members.split(",") + [user_id]) if group_members else [user_id]))
            df.at[i, "groups"] = new_groups
            df.at[i, "group_members"] = new_members
            break

    save_df(df)
    return True, "建立群組成功"

def invite_friend_to_group(current_user, friend_id, group_name):
    df = get_df()
    df = ensure_group_columns(df)

    # 不能邀請自己
    if current_user == friend_id:
        return False, "不能邀請自己加入群組"

    # 檢查使用者是否存在
    friend_row = df[df["user_id"] == friend_id]
    if friend_row.empty:
        return False, "該使用者不存在"

    # 檢查是否為好友
    current_row = df[df["user_id"] == current_user]
    if current_row.empty:
        return False, "當前使用者不存在"

    current_friends_raw = current_row["friends"].values[0]
    current_friends = set(current_friends_raw.split(",")) if current_friends_raw else set()
    if friend_id not in current_friends:
        return False, "只能邀請好友加入群組"

    # 檢查對方是否已在群組中（解析 |group:member,member|group2:member2）
    group_members = friend_row["group_members"].values[0]
    is_in_group = False
    if group_members:
        entries = [s for s in group_members.split('|') if s]
        for entry in entries:
            if ':' not in entry:
                continue
            gname, members = entry.split(':', 1)
            member_list = [m.strip() for m in members.split(',') if m.strip()]
            if gname == group_name and friend_id in member_list:
                is_in_group = True
                break
    if is_in_group:
        return False, "對方已經在該群組中"

    return True, "邀請成功"

def list_groups_for_user(user_id):
    df = get_df()
    df = ensure_group_columns(df)
    idx = df[df['user_id'] == user_id].index[0]
    user_groups = set(df.at[idx, 'groups'].split(',')) if df.at[idx, 'groups'] else set()
    group_members_map = {g: [] for g in user_groups}
    for _, row in df.iterrows():
        row_groups = set(row['groups'].split(',')) if row['groups'] else set()
        for g in user_groups:
            if g in row_groups:
                group_members_map[g].append(row['user_id'])
    return group_members_map

def remove_member_from_group(user_id, group_name, target_id):
    df = get_df()
    df = ensure_group_columns(df)

    if target_id not in df['user_id'].values:
        return False, "成員不存在"

    idx = df[df['user_id'] == target_id].index[0]
    group_list = set(df.at[idx, 'groups'].split(',')) if df.at[idx, 'groups'] else set()

    if group_name in group_list:
        group_list.remove(group_name)
        df.at[idx, 'groups'] = ','.join(sorted(group_list))

    member_entry = f"|{group_name}:{target_id}"
    df.at[idx, 'group_members'] = df.at[idx, 'group_members'].replace(member_entry, '')

    save_df(df)
    return True, f"{target_id} 已從群組 {group_name} 中移除"

def delete_group(group_name):
    df = get_df()
    df = ensure_group_columns(df)
    for idx, row in df.iterrows():
        groups = set(row['groups'].split(',')) if row['groups'] else set()
        if group_name in groups:
            groups.remove(group_name)
            df.at[idx, 'groups'] = ','.join(sorted(groups))

        members = row['group_members']
        df.at[idx, 'group_members'] = '|'.join(
            [entry for entry in members.split('|') if not entry.startswith(f"{group_name}:")]
        )

    save_df(df)
    return True, f"群組 {group_name} 已刪除"

def show_group_availability(group_map):
    st.subheader("群組成員空閒時間")

    if not group_map:
        st.info("你目前沒有加入任何群組")
        return

    group_names = list(group_map.keys())
    selected_group = st.selectbox("選擇群組", group_names, key="group_selector")

    members = group_map.get(selected_group, [])
    if not members:
        st.info("這個群組尚無其他成員")
        return

    selected_user = st.selectbox("選擇要查看的成員", members, key=f"user_selector_{selected_group}")

    if st.session_state.get("last_calendar_group") != selected_group or st.session_state.get("last_calendar_user") != selected_user:
        for suffix in ["show_year", "show_month", "last_click"]:
            st.session_state.pop(f"{selected_user}_{suffix}", None)
        st.session_state["last_calendar_group"] = selected_group
        st.session_state["last_calendar_user"] = selected_user

    display_calendar_view(selected_user)

def render_group_management_ui(user_id):
    st.subheader("所屬群組與成員")

    groups = list_groups_for_user(user_id)

    if not groups:
        st.info("您尚未加入任何群組")
    else:
        for gname, members in groups.items():
            st.markdown(f"#### {gname}")
            st.markdown(f"成員：{', '.join(members)}")

    st.markdown("---")
    st.subheader("建立新群組")
    new_group = st.text_input("群組名稱", key="new_group_input")
    if st.button("建立群組"):
        success, msg = create_group(user_id, new_group)
        if success:
            st.success(msg)
        else:
            st.error(msg)



    st.subheader("邀請好友加入群組")
    friend_to_invite = st.text_input("好友 ID", key="friend_invite_input")
    group_target = st.selectbox("選擇要加入的群組", list(groups.keys()) if groups else [], key="group_invite_target")
    if st.button("邀請好友"):
        success, msg = invite_friend_to_group(user_id, friend_to_invite, group_target)
        st.success(msg) if success else st.error(msg)
        

    st.markdown("---")
    st.subheader("移除群組成員")
    if groups:
        selected_group_for_kick = st.selectbox("選擇群組", list(groups.keys()), key="kick_group_select")
        kickable_members = [m for m in groups[selected_group_for_kick] if m != user_id]
        if kickable_members:
            selected_member_to_kick = st.selectbox("選擇要移除的成員", kickable_members, key="kick_member_select")
            if st.button("移除該成員"):
                success, msg = remove_member_from_group(user_id, selected_group_for_kick, selected_member_to_kick)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        else:
            st.info("該群組沒有其他成員可移除")

    st.markdown("---")
    st.subheader("刪除群組")
    if groups:
        selected_group_for_delete = st.selectbox("選擇要刪除的群組", list(groups.keys()), key="delete_group_selector")
        if st.button("刪除選定群組"):
            success, msg = delete_group(selected_group_for_delete)
            st.success(msg) if success else st.error(msg)
            st.rerun()
    else:
        st.info("您尚未加入任何群組")
