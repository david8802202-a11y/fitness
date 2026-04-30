"""
用戶數據持久化模組 - Google Sheets 版本
使用 Google Sheets 雲端儲存每個用戶的訓練紀錄
保留與原 JSON 版本相同的函式介面,主程式無需修改
"""
import json
import hashlib
import streamlit as st
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials


# ==================== 連線設定 ====================
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]


@st.cache_resource
def _get_gspread_client():
    """
    建立並快取 Google Sheets 連線
    使用 @st.cache_resource 確保整個 App 只連線一次
    """
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client


@st.cache_resource
def _get_spreadsheet():
    """取得試算表物件(快取,只會抓一次)"""
    client = _get_gspread_client()
    spreadsheet_id = st.secrets["sheets"]["spreadsheet_id"]
    return client.open_by_key(spreadsheet_id)


def _get_users_sheet():
    """取得 users 工作表"""
    return _get_spreadsheet().worksheet("users")


def _get_records_sheet():
    """取得 records 工作表"""
    return _get_spreadsheet().worksheet("records")


def _get_settings_sheet():
    """取得 settings 工作表"""
    return _get_spreadsheet().worksheet("settings")


# ==================== 快取機制 ====================
@st.cache_data(ttl=30)  # 快取 30 秒,避免每次都打 API
def _cached_get_all_users():
    """快取讀取所有用戶"""
    return _get_users_sheet().get_all_records()


@st.cache_data(ttl=30)
def _cached_get_all_records():
    """快取讀取所有訓練紀錄"""
    return _get_records_sheet().get_all_records()


@st.cache_data(ttl=30)
def _cached_get_all_settings():
    """快取讀取所有設定"""
    return _get_settings_sheet().get_all_records()


def _clear_cache():
    """寫入後清除快取,確保下次讀到最新資料"""
    _cached_get_all_users.clear()
    _cached_get_all_records.clear()
    _cached_get_all_settings.clear()


# ==================== 主要函式(與原版介面相同) ====================
def init_users_dir():
    """
    初始化(原版用來建立目錄,新版不需要)
    保留是為了相容性,實際上什麼都不做
    """
    pass


def get_user_file(user_id):
    """
    原版用來取得檔案路徑,新版改用 Google Sheets
    保留為相容性,但回傳 None
    """
    return None


def create_user(username):
    """
    創建新用戶或返回現有用戶ID
    返回: (user_id, is_new_user)
    """
    user_id = hashlib.md5(username.encode()).hexdigest()[:10]
    
    # 檢查用戶是否已存在
    all_users = _cached_get_all_users()
    for user in all_users:
        if user.get("user_id") == user_id:
            return user_id, False  # 用戶已存在
    
    # 創建新用戶
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 寫入 users 工作表
    users_sheet = _get_users_sheet()
    users_sheet.append_row([
        user_id,           # A: user_id
        username,          # B: username
        "",                # C: password_hash(預留,目前不使用)
        username,          # D: name(預設等同 username)
        25,                # E: age(預設值)
        now                # F: created_at
    ])
    
    # 同時建立預設設定
    settings_sheet = _get_settings_sheet()
    settings_sheet.append_row([
        user_id,           # A: user_id
        username,          # B: name
        25,                # C: age
        now                # D: updated_at
    ])
    
    _clear_cache()
    return user_id, True


def load_user_data(user_id):
    """
    載入用戶數據
    回傳格式與原版一致:
    {
        "username": "...",
        "user_id": "...",
        "created_at": "...",
        "user_info": {"name": "...", "age": ...},
        "records": [...]
    }
    """
    all_users = _cached_get_all_users()
    
    # 找用戶基本資料
    user = None
    for u in all_users:
        if u.get("user_id") == user_id:
            user = u
            break
    
    if user is None:
        return None
    
    # 找用戶設定
    all_settings = _cached_get_all_settings()
    settings = None
    for s in all_settings:
        if s.get("user_id") == user_id:
            settings = s
            break
    
    # 取得訓練紀錄
    records = get_records(user_id)
    
    # 組裝成原版相容格式
    return {
        "username": user.get("username", ""),
        "user_id": user_id,
        "created_at": user.get("created_at", ""),
        "user_info": {
            "name": settings.get("name", user.get("name", "")) if settings else user.get("name", ""),
            "age": int(settings.get("age", 25)) if settings else 25
        },
        "records": records
    }


def save_user_data(user_id, data):
    """
    保存用戶數據(完整覆寫)
    主要用於:儲存新訓練紀錄、更新設定
    """
    if not data:
        return
    
    # 1. 處理訓練紀錄(只新增最後一筆,因為主程式都是 append)
    new_records = data.get("records", [])
    existing_records = get_records(user_id)
    
    # 找出新增的紀錄(原版用 append,所以新紀錄會在最後)
    if len(new_records) > len(existing_records):
        # 只新增多出來的部分
        for record in new_records[len(existing_records):]:
            _append_record(user_id, record)
    
    # 2. 處理用戶設定
    user_info = data.get("user_info", {})
    if user_info:
        _update_settings(user_id, user_info.get("name", ""), user_info.get("age", 25))
    
    _clear_cache()


def _append_record(user_id, record):
    """新增單筆訓練紀錄到 records 工作表"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    records_sheet = _get_records_sheet()
    records_sheet.append_row([
        user_id,                                    # A: user_id
        record.get("日期", ""),                     # B: date
        record.get("動作數", 0),                    # C: exercises_count
        record.get("組數", 0),                      # D: total_sets
        record.get("時長(分)", 0),                  # E: duration_min
        record.get("熱量", 0),                      # F: calories
        record.get("總Volume", 0),                  # G: total_volume
        record.get("詳細", "{}"),                   # H: details
        now                                         # I: created_at
    ])


def _update_settings(user_id, name, age):
    """更新用戶設定"""
    settings_sheet = _get_settings_sheet()
    all_settings = _cached_get_all_settings()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 找該用戶在第幾列
    target_row = None
    for idx, s in enumerate(all_settings, start=2):  # 第 2 列開始(第 1 列是標題)
        if s.get("user_id") == user_id:
            target_row = idx
            break
    
    if target_row:
        # 更新現有列
        settings_sheet.update(
            f'A{target_row}:D{target_row}',
            [[user_id, name, age, now]]
        )
    else:
        # 新增列
        settings_sheet.append_row([user_id, name, age, now])


def add_record(user_id, record):
    """新增訓練記錄(原版函式,保留相容性)"""
    user = load_user_data(user_id)
    if user:
        _append_record(user_id, record)
        _clear_cache()
        return True
    return False


def get_records(user_id):
    """獲取用戶的所有訓練記錄"""
    all_records = _cached_get_all_records()
    
    user_records = []
    for r in all_records:
        if r.get("user_id") == user_id:
            # 轉換成原版格式(中文 key)
            user_records.append({
                "日期": r.get("date", ""),
                "動作數": int(r.get("exercises_count", 0)) if r.get("exercises_count") != "" else 0,
                "組數": int(r.get("total_sets", 0)) if r.get("total_sets") != "" else 0,
                "時長(分)": int(r.get("duration_min", 0)) if r.get("duration_min") != "" else 0,
                "熱量": int(r.get("calories", 0)) if r.get("calories") != "" else 0,
                "總Volume": int(r.get("total_volume", 0)) if r.get("total_volume") != "" else 0,
                "詳細": r.get("details", "{}")
            })
    
    return user_records


def update_user_info(user_id, user_info):
    """更新用戶基本資訊"""
    user = load_user_data(user_id)
    if user:
        _update_settings(
            user_id,
            user_info.get("name", ""),
            user_info.get("age", 25)
        )
        _clear_cache()
        return True
    return False


def list_all_users():
    """列出所有用戶"""
    all_users = _cached_get_all_users()
    all_records = _cached_get_all_records()
    
    # 計算每個用戶的紀錄數
    record_counts = {}
    for r in all_records:
        uid = r.get("user_id")
        record_counts[uid] = record_counts.get(uid, 0) + 1
    
    users = []
    for u in all_users:
        uid = u.get("user_id")
        users.append({
            "user_id": uid,
            "username": u.get("username", ""),
            "created_at": u.get("created_at", ""),
            "records_count": record_counts.get(uid, 0)
        })
    
    return users


def delete_user(user_id):
    """刪除用戶及其所有數據(用 row 刪除)"""
    try:
        # 1. 刪除 users 工作表中該用戶
        users_sheet = _get_users_sheet()
        all_users = _cached_get_all_users()
        for idx, u in enumerate(all_users, start=2):
            if u.get("user_id") == user_id:
                users_sheet.delete_rows(idx)
                break
        
        # 2. 刪除 settings 工作表中該用戶
        settings_sheet = _get_settings_sheet()
        all_settings = _cached_get_all_settings()
        for idx, s in enumerate(all_settings, start=2):
            if s.get("user_id") == user_id:
                settings_sheet.delete_rows(idx)
                break
        
        # 3. 刪除 records 工作表中該用戶的所有紀錄(從後往前刪)
        records_sheet = _get_records_sheet()
        all_records = _cached_get_all_records()
        rows_to_delete = []
        for idx, r in enumerate(all_records, start=2):
            if r.get("user_id") == user_id:
                rows_to_delete.append(idx)
        # 從大到小排序,避免刪除時 index 錯位
        for row_idx in sorted(rows_to_delete, reverse=True):
            records_sheet.delete_rows(row_idx)
        
        _clear_cache()
        return True
    except Exception as e:
        print(f"刪除用戶失敗: {e}")
        return False
