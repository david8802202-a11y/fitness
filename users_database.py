"""
用戶數據持久化模組
使用 JSON 檔案儲存每個用戶的訓練紀錄
"""

import json
import os
from datetime import datetime
import hashlib

USERS_DIR = "smartfit_users"

def init_users_dir():
    """初始化用戶目錄"""
    if not os.path.exists(USERS_DIR):
        os.makedirs(USERS_DIR)

def get_user_file(user_id):
    """獲取用戶數據檔案路徑"""
    init_users_dir()
    return os.path.join(USERS_DIR, f"{user_id}.json")

def create_user(username):
    """
    創建新用戶或返回現有用戶ID
    返回: (user_id, is_new_user)
    """
    init_users_dir()
    user_id = hashlib.md5(username.encode()).hexdigest()[:10]
    user_file = get_user_file(user_id)
    
    if os.path.exists(user_file):
        return user_id, False  # 用戶已存在
    
    # 創建新用戶
    default_data = {
        "username": username,
        "user_id": user_id,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_info": {"name": username, "age": 25},
        "records": []
    }
    
    with open(user_file, 'w', encoding='utf-8') as f:
        json.dump(default_data, f, ensure_ascii=False, indent=2)
    
    return user_id, True

def load_user_data(user_id):
    """載入用戶數據"""
    init_users_dir()
    user_file = get_user_file(user_id)
    
    if os.path.exists(user_file):
        with open(user_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return None

def save_user_data(user_id, data):
    """保存用戶數據"""
    init_users_dir()
    user_file = get_user_file(user_id)
    
    with open(user_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_record(user_id, record):
    """新增訓練記錄"""
    data = load_user_data(user_id)
    if data:
        data["records"].append(record)
        save_user_data(user_id, data)
        return True
    return False

def get_records(user_id):
    """獲取用戶的所有訓練記錄"""
    data = load_user_data(user_id)
    if data:
        return data.get("records", [])
    return []

def update_user_info(user_id, user_info):
    """更新用戶基本資訊"""
    data = load_user_data(user_id)
    if data:
        data["user_info"] = user_info
        save_user_data(user_id, data)
        return True
    return False

def list_all_users():
    """列出所有用戶"""
    init_users_dir()
    users = []
    
    for filename in os.listdir(USERS_DIR):
        if filename.endswith('.json'):
            user_id = filename[:-5]
            data = load_user_data(user_id)
            if data:
                users.append({
                    "user_id": user_id,
                    "username": data.get("username"),
                    "created_at": data.get("created_at"),
                    "records_count": len(data.get("records", []))
                })
    
    return users

def delete_user(user_id):
    """刪除用戶及其所有數據"""
    init_users_dir()
    user_file = get_user_file(user_id)
    
    if os.path.exists(user_file):
        os.remove(user_file)
        return True
    return False
