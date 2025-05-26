import streamlit as st
from storage_module import get_df, save_df
from calendar_module import display_calendar_view
from confirm_dialog_module import confirm_action
from group_event import render_group_events_ui,add_event_row,get_event_rows,delete_event_by_id,update_event_participation_by_id,get_event_by_id

def ensure_group_columns(df):
    if 'groups' not in df.columns:
        df['groups'] = ''
    if 'group_members' not in df.columns:
        df['group_members'] = ''
    return df

# 工具函式：解析與重組 group_members 欄位
def parse_group_members(members_str):
    group_map = {}
    if members_str:
        entries = [s for s in members_str.split('|') if s]
        for entry in entries:
            if ':' not in entry:
                continue
            group, members = entry.split(':', 1)
            member_list = [m.strip() for m in members.split(',') if m.strip()]
            group_map[group] = set(member_list)
    return group_map

def to_group_members_str(group_map):
    return ''.join(f'|{g}:{",".join(sorted(mems))}' for g, mems in group_map.items() if mems)

def create_group(user_id, group_name):
    df = get_df()
    df = ensure_group_columns(df)

    # 檢查群組名稱是否已存在
    existing_groups = set()
    for g in df["groups"].dropna():
        existing_groups.update(g.split(","))
    if group_name in existing_groups:
        return False, "該群組名稱已存在"

    # 為用戶新增群組到 groups 與 group_members
    for i in df.index:
        if df.at[i, "user_id"] == user_id:
            # 更新 groups
            groups = df.at[i, "groups"]
            group_set = set(groups.split(",")) if groups else set()
            group_set.add(group_name)
            df.at[i, "groups"] = ",".join(sorted(group_set))
            # 更新 group_members
            group_map = parse_group_members(df.at[i, "group_members"])
            group_map.setdefault(group_name, set()).add(user_id)
            df.at[i, "group_members"] = to_group_members_str(group_map)
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

    # 檢查對方是否已在群組中
    group_map = parse_group_members(friend_row["group_members"].values[0])
    if group_name in group_map and friend_id in group_map[group_name]:
        return False, "對方已經在該群組中"

    # 更新 groups 欄
    idx = friend_row.index[0]
    groups = df.at[idx, "groups"]
    group_set = set(groups.split(",")) if groups else set()
    group_set.add(group_name)
    df.at[idx, "groups"] = ",".join(sorted(group_set))

    # 更新 group_members 欄
    group_map = parse_group_members(df.at[idx, "group_members"])
    group_map.setdefault(group_name, set()).add(friend_id)
    df.at[idx, "group_members"] = to_group_members_str(group_map)

    save_df(df)
    return True, "邀請成功，好友已加入群組"

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

    # 1. 移除 groups 欄位的群組
    group_list = set(df.at[idx, 'groups'].split(',')) if df.at[idx, 'groups'] else set()
    if group_name in group_list:
        group_list.remove(group_name)
        df.at[idx, 'groups'] = ','.join(sorted(group_list))

    # 2. 更新 group_members 欄位
    group_map = parse_group_members(df.at[idx, 'group_members'])
    if group_name in group_map:
        group_map[group_name].discard(target_id)
        if not group_map[group_name]:
            del group_map[group_name]
    df.at[idx, 'group_members'] = to_group_members_str(group_map)

    save_df(df)
    return True, f"{target_id} 已從群組 {group_name} 中移除"

def delete_group(group_name):
    df = get_df()
    df = ensure_group_columns(df)

    # 1. 先移除所有人的 groups 和 group_members 欄位中的這個群組
    for idx, row in df.iterrows():
        # 移除 groups 欄
        groups = set(row['groups'].split(',')) if row['groups'] else set()
        if group_name in groups:
            groups.remove(group_name)
            df.at[idx, 'groups'] = ','.join(sorted(groups))
        # 移除 group_members 欄
        group_map = parse_group_members(row['group_members'])
        if group_name in group_map:
            del group_map[group_name]
        df.at[idx, 'group_members'] = to_group_members_str(group_map)
    
    # 2. 刪除群組本身與所有活動（row_type==group 或 event 且 group_name符合）
    df = df[~(((df['row_type'] == 'group') | (df['row_type'] == 'event')) & (df['group_name'] == group_name))]

    save_df(df)
    return True, f"群組 {group_name} 及其活動已刪除"


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

    group_choices = list(groups.keys()) if groups else []
    if group_choices:
        group_target = st.selectbox("選擇要加入的群組", group_choices, key="group_invite_target")
        if st.button("邀請好友"):
            success, msg = invite_friend_to_group(user_id, friend_to_invite, group_target)
            st.success(msg) if success else st.error(msg)
    else:
        st.info("您目前沒有任何群組，請先建立群組才能邀請好友加入")
        
    st.markdown("---")
    st.subheader("移除群組成員")
    if groups:
        selected_group_for_kick = st.selectbox("選擇群組", list(groups.keys()), key="kick_group_select")
        kickable_members = [m for m in groups[selected_group_for_kick] if m != user_id]
        if kickable_members:
            selected_member_to_kick = st.selectbox("選擇要移除的成員", kickable_members, key="kick_member_select")
            if confirm_action("確定移除這位成員", key="remove_member", warn_text="移除後該成員將無法再存取本群組資料，且無法復原。"):
                success, msg = remove_member_from_group(user_id, selected_group_for_kick, selected_member_to_kick)
                if success:
                    st.success("移除完成")
                    st.info(msg)
                else:
                    st.error(msg)
        else:
            st.info("該群組沒有其他成員可移除")
            
    st.markdown("---")
    st.subheader("刪除群組")
    if groups:
        selected_group_for_delete = st.selectbox("選擇要刪除的群組", list(groups.keys()), key="delete_group_selector")
        if confirm_action("確定刪除這個群組", key="delete_group", warn_text="本群組及所有資料將永久刪除，無法復原！"):
            success, msg = delete_group(selected_group_for_delete)
            if success:
                st.success("刪除完成")
                st.info(msg)
            else:
                st.error(msg)

    else:
        st.info("您尚未加入任何群組")
    for gname, members in groups.items():
        st.markdown(f"#### {gname}")
        st.markdown(f"成員：{', '.join(members)}")
        with st.expander(f"【{gname}】活動／日程表"):
            render_group_events_ui(gname, user_id)
