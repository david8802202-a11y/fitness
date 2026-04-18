import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from image_data import IMAGES_DATA
from users_database import create_user, load_user_data, save_user_data, get_records, update_user_info
import json
import time

st.set_page_config(page_title="SmartFit", page_icon="💪", layout="wide")

BODY_PARTS = ["胸部", "背部", "肩膀", "手臂", "腿部", "核心"]
INJURY_AREAS = ["肩膀", "肘部", "腕部", "腰部", "膝蓋", "踝部", "頸部", "下背部"]

# ==================== 50個動作 ====================
EXERCISES = [
    # 徒手/啞鈴 - 胸部 (5個)
    {"id": "001", "nameCN": "俯臥撑", "bodyPart": "胸部", "target_muscle": "胸肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "徒手/啞鈴", "equipment": "無", "filename": "push_ups.jpg", "require_weight": False, "tempo": "下放2秒 撐起1秒", "risk_areas": ["肩膀", "肘部", "腕部"], "intensity_reduction_possible": True, "tips": ["保持身體直線", "降低至胸部", "推回起始位置"]},
    {"id": "002", "nameCN": "寬距俯臥撑", "bodyPart": "胸部", "target_muscle": "胸肌", "difficulty": "初級", "sets": 3, "reps": 10, "category": "徒手/啞鈴", "equipment": "無", "filename": "wide_push_ups.jpg", "require_weight": False, "tempo": "下放2秒 撐起1秒", "risk_areas": ["肩膀", "肘部", "腕部"], "intensity_reduction_possible": True, "tips": ["雙手寬距", "保持直線", "完整範圍"]},
    {"id": "003", "nameCN": "菱形俯臥撑", "bodyPart": "胸部", "target_muscle": "胸肌", "difficulty": "中級", "sets": 3, "reps": 8, "category": "徒手/啞鈴", "equipment": "無", "filename": "diamond_push_ups.jpg", "require_weight": False, "tempo": "下放2秒 撐起1秒", "risk_areas": ["肘部", "腕部", "肩膀"], "intensity_reduction_possible": True, "tips": ["雙手在胸下", "肘部靠近", "完全伸展"]},
    {"id": "004", "nameCN": "下斜俯臥撑", "bodyPart": "胸部", "target_muscle": "胸肌", "difficulty": "中級", "sets": 3, "reps": 10, "category": "徒手/啞鈴", "equipment": "無", "filename": "decline_push_ups.jpg", "require_weight": False, "tempo": "下放2秒 撐起1秒", "risk_areas": ["肩膀", "肘部", "腕部"], "intensity_reduction_possible": True, "tips": ["雙腳放高", "身體直線", "完整動作"]},
    {"id": "005", "nameCN": "箭手俯臥撑", "bodyPart": "胸部", "target_muscle": "胸肌", "difficulty": "高級", "sets": 3, "reps": 6, "category": "徒手/啞鈴", "equipment": "無", "filename": "archer_push_ups.jpg", "require_weight": False, "tempo": "下放2秒 撐起1秒", "risk_areas": ["肩膀", "肘部", "腕部"], "intensity_reduction_possible": True, "tips": ["一側彎曲", "一側伸直", "平衡訓練"]},
    
    # 徒手/啞鈴 - 背部 (5個)
    {"id": "006", "nameCN": "引體向上", "bodyPart": "背部", "target_muscle": "背肌", "difficulty": "中級", "sets": 3, "reps": 8, "category": "徒手/啞鈴", "equipment": "無", "filename": "pull_ups.jpg", "require_weight": False, "tempo": "下放2秒 撐起1秒", "risk_areas": ["肩膀", "肘部"], "intensity_reduction_possible": False, "tips": ["握距寬", "下巴超杆", "控制下降"]},
    {"id": "007", "nameCN": "窄握引體向上", "bodyPart": "背部", "target_muscle": "背肌", "difficulty": "中級", "sets": 3, "reps": 8, "category": "徒手/啞鈴", "equipment": "無", "filename": "chin_ups.jpg", "require_weight": False, "tempo": "下放2秒 撐起1秒", "risk_areas": ["肘部", "肩膀"], "intensity_reduction_possible": False, "tips": ["掌心向內", "肘部靠近", "平順動作"]},
    {"id": "008", "nameCN": "反向划船", "bodyPart": "背部", "target_muscle": "背肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "徒手/啞鈴", "equipment": "無", "filename": "reverse_rows.jpg", "require_weight": False, "tempo": "下放2秒 拉起1秒", "risk_areas": ["肩膀", "腕部"], "intensity_reduction_possible": True, "tips": ["身體直線", "拉至胸部", "控制下降"]},
    {"id": "009", "nameCN": "啞鈴划船", "bodyPart": "背部", "target_muscle": "背肌", "difficulty": "中級", "sets": 4, "reps": 10, "category": "徒手/啞鈴", "equipment": "啞鈴", "filename": "dumbbell_rows.jpg", "require_weight": True, "tempo": "下放2秒 拉起1秒", "risk_areas": ["肩膀", "腰部"], "intensity_reduction_possible": True, "tips": ["膝蓋跪", "核心穩定", "拉至腰"]},
    {"id": "010", "nameCN": "超人式", "bodyPart": "背部", "target_muscle": "背肌", "difficulty": "初級", "sets": 3, "reps": 30, "category": "徒手/啞鈴", "equipment": "無", "filename": "superman_hold.jpg", "require_weight": False, "tempo": "靜止2秒", "risk_areas": ["下背部", "腰部"], "intensity_reduction_possible": False, "tips": ["手臂前伸", "腿後伸", "胸部離地"]},
    
    # 徒手/啞鈴 - 肩膀 (5個)
    {"id": "051", "nameCN": "啞鈴肩推", "bodyPart": "肩膀", "target_muscle": "肩肌", "difficulty": "中級", "sets": 3, "reps": 10, "category": "徒手/啞鈴", "equipment": "啞鈴", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["肩膀", "肘部"], "intensity_reduction_possible": True, "tips": ["挺胸", "肩膀穩定", "完整範圍"]},
    {"id": "052", "nameCN": "啞鈴側平舉", "bodyPart": "肩膀", "target_muscle": "肩肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "徒手/啞鈴", "equipment": "啞鈴", "filename": None, "require_weight": True, "tempo": "上升2秒 下放2秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["挺胸", "肘部微彎", "控制速度"]},
    {"id": "053", "nameCN": "啞鈴前平舉", "bodyPart": "肩膀", "target_muscle": "肩肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "徒手/啞鈴", "equipment": "啞鈴", "filename": None, "require_weight": True, "tempo": "上升1秒 下放2秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["肘部微彎", "緩慢控制", "完整動作"]},
    {"id": "054", "nameCN": "啞鈴後舉飛鳥", "bodyPart": "肩膀", "target_muscle": "肩肌", "difficulty": "中級", "sets": 3, "reps": 12, "category": "徒手/啞鈴", "equipment": "啞鈴", "filename": None, "require_weight": True, "tempo": "上升2秒 下放2秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["身體前傾", "肘部微彎", "集中收縮"]},
    {"id": "055", "nameCN": "肩部聳動", "bodyPart": "肩膀", "target_muscle": "肩肌", "difficulty": "初級", "sets": 3, "reps": 15, "category": "徒手/啞鈴", "equipment": "啞鈴", "filename": None, "require_weight": True, "tempo": "上升1秒 下放1秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["肩膀聳起", "頂部停留", "控制下降"]},
    
    # 徒手/啞鈴 - 手臂 (5個)
    {"id": "056", "nameCN": "啞鈴彎舉", "bodyPart": "手臂", "target_muscle": "二頭肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "徒手/啞鈴", "equipment": "啞鈴", "filename": None, "require_weight": True, "tempo": "上升1秒 下放2秒", "risk_areas": ["肘部"], "intensity_reduction_possible": True, "tips": ["肘部固定", "完全收縮", "控制速度"]},
    {"id": "057", "nameCN": "錘式彎舉", "bodyPart": "手臂", "target_muscle": "二頭肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "徒手/啞鈴", "equipment": "啞鈴", "filename": None, "require_weight": True, "tempo": "上升1秒 下放2秒", "risk_areas": ["肘部"], "intensity_reduction_possible": True, "tips": ["握把中立", "肘部穩定", "完整範圍"]},
    {"id": "058", "nameCN": "啞鈴三頭伸展", "bodyPart": "手臂", "target_muscle": "三頭肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "徒手/啞鈴", "equipment": "啞鈴", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["肘部", "肩膀"], "intensity_reduction_possible": True, "tips": ["肘部靠近", "完全伸展", "控制速度"]},
    {"id": "059", "nameCN": "窄距俯臥撑（三頭）", "bodyPart": "手臂", "target_muscle": "三頭肌", "difficulty": "中級", "sets": 3, "reps": 10, "category": "徒手/啞鈴", "equipment": "無", "filename": None, "require_weight": False, "tempo": "下放2秒 推起1秒", "risk_areas": ["肘部", "腕部"], "intensity_reduction_possible": True, "tips": ["雙手靠近", "肘部貼身", "完整動作"]},
    {"id": "060", "nameCN": "啞鈴過頭伸展", "bodyPart": "手臂", "target_muscle": "三頭肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "徒手/啞鈴", "equipment": "啞鈴", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["肘部", "肩膀"], "intensity_reduction_possible": True, "tips": ["單手或雙手", "肘部固定", "完全伸展"]},
    
    # 徒手/啞鈴 - 腿部 (5個)
    {"id": "011", "nameCN": "深蹲", "bodyPart": "腿部", "target_muscle": "腿肌", "difficulty": "初級", "sets": 3, "reps": 15, "category": "徒手/啞鈴", "equipment": "無", "filename": "squats.jpg", "require_weight": False, "tempo": "下放2秒 撐起1秒", "risk_areas": ["膝蓋", "踝部", "下背部"], "intensity_reduction_possible": True, "tips": ["挺胸", "臀部後坐", "腳跟推起"]},
    {"id": "012", "nameCN": "跳躍深蹲", "bodyPart": "腿部", "target_muscle": "腿肌", "difficulty": "中級", "sets": 3, "reps": 12, "category": "徒手/啞鈴", "equipment": "無", "filename": "jump_squats.jpg", "require_weight": False, "tempo": "爆發式", "risk_areas": ["膝蓋", "踝部"], "intensity_reduction_possible": False, "tips": ["全力跳", "軟著陸", "快速起身"]},
    {"id": "013", "nameCN": "弓步", "bodyPart": "腿部", "target_muscle": "腿肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "徒手/啞鈴", "equipment": "無", "filename": "lunges.jpg", "require_weight": False, "tempo": "下放2秒 撐起1秒", "risk_areas": ["膝蓋", "踝部"], "intensity_reduction_possible": True, "tips": ["前腳90度", "後腳接地", "保持直立"]},
    {"id": "014", "nameCN": "啞鈴深蹲", "bodyPart": "腿部", "target_muscle": "腿肌", "difficulty": "中級", "sets": 4, "reps": 10, "category": "徒手/啞鈴", "equipment": "啞鈴", "filename": "dumbbell_squats.jpg", "require_weight": True, "tempo": "下放2秒 撐起1秒", "risk_areas": ["膝蓋", "腰部"], "intensity_reduction_possible": True, "tips": ["拿著啞鈴", "挺胸下蹲", "腳跟推起"]},
    {"id": "015", "nameCN": "提踵", "bodyPart": "腿部", "target_muscle": "腿肌", "difficulty": "初級", "sets": 3, "reps": 20, "category": "徒手/啞鈴", "equipment": "無", "filename": "calf_raises.jpg", "require_weight": False, "tempo": "上升1秒 下放1秒", "risk_areas": ["踝部"], "intensity_reduction_possible": True, "tips": ["站直", "提起腳跟", "控制下降"]},
    
    # 徒手/啞鈴 - 核心 (5個)
    {"id": "016", "nameCN": "棒式", "bodyPart": "核心", "target_muscle": "核心", "difficulty": "初級", "sets": 3, "reps": 30, "category": "徒手/啞鈴", "equipment": "無", "filename": "plank.jpg", "require_weight": False, "tempo": "靜止", "risk_areas": ["腕部", "肩膀"], "intensity_reduction_possible": True, "tips": ["身體直線", "核心緊縮", "臀部不下沉"]},
    {"id": "017", "nameCN": "側棒式", "bodyPart": "核心", "target_muscle": "核心", "difficulty": "初級", "sets": 3, "reps": 20, "category": "徒手/啞鈴", "equipment": "無", "filename": "side_plank.jpg", "require_weight": False, "tempo": "靜止", "risk_areas": ["肩膀", "腕部"], "intensity_reduction_possible": True, "tips": ["身體直線", "核心收緊", "臀部不下沉"]},
    {"id": "018", "nameCN": "仰臥起坐", "bodyPart": "核心", "target_muscle": "核心", "difficulty": "初級", "sets": 3, "reps": 15, "category": "徒手/啞鈴", "equipment": "無", "filename": "sit_ups.jpg", "require_weight": False, "tempo": "上起1秒 下放1秒", "risk_areas": ["頸部", "下背部"], "intensity_reduction_possible": True, "tips": ["膝蓋彎曲", "不拉脖子", "胸部向膝"]},
    {"id": "019", "nameCN": "爬山者", "bodyPart": "核心", "target_muscle": "核心", "difficulty": "中級", "sets": 3, "reps": 20, "category": "徒手/啞鈴", "equipment": "無", "filename": "mountain_climbers.jpg", "require_weight": False, "tempo": "快速", "risk_areas": ["肩膀", "腕部"], "intensity_reduction_possible": True, "tips": ["快速交替", "保持俯臥撑", "核心緊縮"]},
    {"id": "020", "nameCN": "抬腿", "bodyPart": "核心", "target_muscle": "核心", "difficulty": "初級", "sets": 3, "reps": 12, "category": "徒手/啞鈴", "equipment": "無", "filename": "leg_raises.jpg", "require_weight": False, "tempo": "上升1秒 下放2秒", "risk_areas": ["下背部"], "intensity_reduction_possible": True, "tips": ["背部貼地", "腿部直", "控制速度"]},
    
    # 健身房儀器 - 胸部 (5個，有圖21-25)
    {"id": "021", "nameCN": "槓鈴臥推", "bodyPart": "胸部", "target_muscle": "胸肌", "difficulty": "中級", "sets": 4, "reps": 8, "category": "健身房儀器", "equipment": "槓鈴", "filename": "barbell_bench.jpg", "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["肩膀", "肘部"], "intensity_reduction_possible": True, "tips": ["背貼板", "肩膀穩定", "平順動作"]},
    {"id": "022", "nameCN": "胸部推蹬機", "bodyPart": "胸部", "target_muscle": "胸肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "推蹬機", "filename": "chest_machine.jpg", "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["肩膀", "肘部"], "intensity_reduction_possible": True, "tips": ["坐直對齊", "完全推出", "控制回放"]},
    {"id": "023", "nameCN": "拉力機夾胸", "bodyPart": "胸部", "target_muscle": "胸肌", "difficulty": "中級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "拉力機", "filename": "cable_flyes.jpg", "require_weight": True, "tempo": "外展2秒 內收1秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["手臂微彎", "控制回放", "集中收縮"]},
    {"id": "024", "nameCN": "史密斯機臥推", "bodyPart": "胸部", "target_muscle": "胸肌", "difficulty": "初級", "sets": 4, "reps": 12, "category": "健身房儀器", "equipment": "史密斯機", "filename": "smith_machine_bench.jpg", "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["肩膀", "肘部"], "intensity_reduction_possible": True, "tips": ["槓在肩", "直線下降", "完整動作"]},
    {"id": "025", "nameCN": "胸部飛鳥機", "bodyPart": "胸部", "target_muscle": "胸肌", "difficulty": "中級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "飛鳥機", "filename": "pec_deck.jpg", "require_weight": True, "tempo": "外展2秒 內收1秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["手臂微彎", "控制回放", "充分收縮"]},
    
    # 健身房儀器 - 背部 (5個，有圖26-27)
    {"id": "026", "nameCN": "槓鈴划船", "bodyPart": "背部", "target_muscle": "背肌", "difficulty": "中級", "sets": 4, "reps": 8, "category": "健身房儀器", "equipment": "槓鈴", "filename": "barbell_rows.jpg", "require_weight": True, "tempo": "下放2秒 拉起1秒", "risk_areas": ["肩膀", "腰部"], "intensity_reduction_possible": True, "tips": ["膝蓋微彎", "背部直", "拉至腹"]},
    {"id": "027", "nameCN": "下拉機", "bodyPart": "背部", "target_muscle": "背肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "下拉機", "filename": "lat_pulldown.jpg", "require_weight": True, "tempo": "下放2秒 拉起1秒", "risk_areas": ["肩膀", "肘部"], "intensity_reduction_possible": True, "tips": ["拉至胸", "控制回放", "核心緊縮"]},
    {"id": "028", "nameCN": "拉力機划船", "bodyPart": "背部", "target_muscle": "背肌", "difficulty": "初級", "sets": 4, "reps": 12, "category": "健身房儀器", "equipment": "拉力機", "filename": None, "require_weight": True, "tempo": "下放2秒 拉起1秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["坐直挺胸", "拉至腹", "控制回放"]},
    {"id": "029", "nameCN": "T槓划船", "bodyPart": "背部", "target_muscle": "背肌", "difficulty": "中級", "sets": 4, "reps": 10, "category": "健身房儀器", "equipment": "T槓", "filename": None, "require_weight": True, "tempo": "下放2秒 拉起1秒", "risk_areas": ["腰部", "肩膀"], "intensity_reduction_possible": True, "tips": ["身體穩定", "拉至胸", "控制下降"]},
    {"id": "030", "nameCN": "背闊肌拉力機", "bodyPart": "背部", "target_muscle": "背肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "背闊肌機", "filename": None, "require_weight": True, "tempo": "下放2秒 拉起1秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["坐直", "拉至腹", "控制回放"]},
    
    # 健身房儀器 - 肩膀 (5個)
    {"id": "031", "nameCN": "槓鈴肩推", "bodyPart": "肩膀", "target_muscle": "肩肌", "difficulty": "中級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "槓鈴", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["肩膀", "肘部"], "intensity_reduction_possible": True, "tips": ["槓在肩", "上推至頂", "控制下降"]},
    {"id": "032", "nameCN": "肩推機", "bodyPart": "肩膀", "target_muscle": "肩肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "肩推機", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["坐直", "推至頂部", "控制下降"]},
    {"id": "033", "nameCN": "側平舉機", "bodyPart": "肩膀", "target_muscle": "肩肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "側平舉機", "filename": None, "require_weight": True, "tempo": "上升2秒 下放2秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["坐直", "抬至肩高", "控制速度"]},
    {"id": "034", "nameCN": "反向夾胸機", "bodyPart": "肩膀", "target_muscle": "肩肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "夾胸機", "filename": None, "require_weight": True, "tempo": "外展2秒 內收1秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["坐直", "手臂向外", "控制回放"]},
    {"id": "035", "nameCN": "前平舉機", "bodyPart": "肩膀", "target_muscle": "肩肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "前平舉機", "filename": None, "require_weight": True, "tempo": "上升2秒 下放2秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["坐直", "推至肩高", "控制速度"]},
    
    # 健身房儀器 - 手臂 (5個)
    {"id": "036", "nameCN": "繩索下壓", "bodyPart": "手臂", "target_muscle": "三頭肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "拉力機", "filename": None, "require_weight": True, "tempo": "下放1秒 推起1秒", "risk_areas": ["肘部"], "intensity_reduction_possible": True, "tips": ["肘部不動", "完全伸展", "控制回放"]},
    {"id": "037", "nameCN": "拉力機彎舉", "bodyPart": "手臂", "target_muscle": "二頭肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "拉力機", "filename": None, "require_weight": True, "tempo": "上升1秒 下放2秒", "risk_areas": ["肘部"], "intensity_reduction_possible": True, "tips": ["肘部固定", "張力持續", "控制回放"]},
    {"id": "038", "nameCN": "三頭撐體機", "bodyPart": "手臂", "target_muscle": "三頭肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "撐體機", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["肩膀", "肘部"], "intensity_reduction_possible": True, "tips": ["身體向前", "肘部90度", "完整動作"]},
    {"id": "039", "nameCN": "二頭彎舉機", "bodyPart": "手臂", "target_muscle": "二頭肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "彎舉機", "filename": None, "require_weight": True, "tempo": "上升1秒 下放2秒", "risk_areas": ["肘部"], "intensity_reduction_possible": True, "tips": ["坐直", "充分收縮", "控制速度"]},
    {"id": "040", "nameCN": "三頭肌機器", "bodyPart": "手臂", "target_muscle": "三頭肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "三頭機", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["肘部"], "intensity_reduction_possible": True, "tips": ["坐直", "完全伸展", "控制回放"]},
    
    # 健身房儀器 - 腿部 (5個)
    {"id": "041", "nameCN": "推蹬機", "bodyPart": "腿部", "target_muscle": "腿肌", "difficulty": "初級", "sets": 3, "reps": 15, "category": "健身房儀器", "equipment": "推蹬機", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["膝蓋"], "intensity_reduction_possible": True, "tips": ["腳在機器", "完全伸展", "控制下降"]},
    {"id": "042", "nameCN": "腿部卷舉機", "bodyPart": "腿部", "target_muscle": "腿肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "卷舉機", "filename": None, "require_weight": True, "tempo": "上升1秒 下放2秒", "risk_areas": ["膝蓋"], "intensity_reduction_possible": True, "tips": ["坐直", "卷至胸", "控制回放"]},
    {"id": "043", "nameCN": "腿部伸展機", "bodyPart": "腿部", "target_muscle": "腿肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "伸展機", "filename": None, "require_weight": True, "tempo": "伸展1秒 下放2秒", "risk_areas": ["膝蓋"], "intensity_reduction_possible": True, "tips": ["坐直", "完全伸展", "控制回放"]},
    {"id": "044", "nameCN": "哈克深蹲機", "bodyPart": "腿部", "target_muscle": "腿肌", "difficulty": "中級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "哈克機", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["膝蓋"], "intensity_reduction_possible": True, "tips": ["肩膀靠機", "深蹲至平行", "完整動作"]},
    {"id": "045", "nameCN": "槓鈴深蹲", "bodyPart": "腿部", "target_muscle": "腿肌", "difficulty": "中級", "sets": 4, "reps": 8, "category": "健身房儀器", "equipment": "槓鈴", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["膝蓋", "腰部"], "intensity_reduction_possible": True, "tips": ["槓在肩", "直立姿勢", "深蹲至平行"]},
    
    # 健身房儀器 - 核心 (5個)
    {"id": "046", "nameCN": "拉力卷腹", "bodyPart": "核心", "target_muscle": "核心", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "拉力機", "filename": None, "require_weight": True, "tempo": "下放2秒 收起1秒", "risk_areas": ["下背部"], "intensity_reduction_possible": True, "tips": ["膝蓋彎", "卷至膝", "控制回放"]},
    {"id": "047", "nameCN": "腹肌卷腹機", "bodyPart": "核心", "target_muscle": "核心", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "卷腹機", "filename": None, "require_weight": True, "tempo": "收起1秒 下放2秒", "risk_areas": ["下背部", "頸部"], "intensity_reduction_possible": True, "tips": ["坐直對齊", "卷起完整", "控制回放"]},
    {"id": "048", "nameCN": "滑輪卷腹", "bodyPart": "核心", "target_muscle": "核心", "difficulty": "中級", "sets": 3, "reps": 10, "category": "健身房儀器", "equipment": "滑輪", "filename": None, "require_weight": False, "tempo": "向前滾2秒 回收1秒", "risk_areas": ["腕部", "肩膀"], "intensity_reduction_possible": False, "tips": ["膝蓋跪", "向前滾", "回收縮腹"]},
    {"id": "049", "nameCN": "旋轉腹肌機", "bodyPart": "核心", "target_muscle": "核心", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "旋轉機", "filename": None, "require_weight": True, "tempo": "旋轉1秒 回中1秒", "risk_areas": ["腰部"], "intensity_reduction_possible": True, "tips": ["坐直", "緩慢旋轉", "控制速度"]},
    {"id": "050", "nameCN": "懸掛抬腿", "bodyPart": "核心", "target_muscle": "核心", "difficulty": "中級", "sets": 3, "reps": 10, "category": "健身房儀器", "equipment": "單槓", "filename": None, "require_weight": False, "tempo": "上升2秒 下放2秒", "risk_areas": ["肩膀", "肘部"], "intensity_reduction_possible": False, "tips": ["握把穩定", "腿抬至水平", "控制下降"]},
]

TRAINING_SUGGESTIONS = {
    15: {"name": "快速訓練 (15分)", "desc": "3-4個動作", "exercises_count": (3, 4)},
    30: {"name": "標準訓練 (30分)", "desc": "5-6個動作", "exercises_count": (5, 6)},
    45: {"name": "加強訓練 (45分)", "desc": "7-8個動作", "exercises_count": (7, 8)},
    60: {"name": "完整訓練 (60分)", "desc": "9-10個動作", "exercises_count": (9, 10)},
}

REST_TIMES = {"初級": 60, "中級": 90, "高級": 120}

# ==================== 輔助函式 ====================
def filter_exercises_by_injuries(exercises, injured_areas):
    """根據受傷部位過濾動作"""
    filtered = []
    replaced = {}
    intensity_warnings = {}
    
    for ex in exercises:
        has_injury = any(area in ex.get("risk_areas", []) for area in injured_areas)
        
        if has_injury:
            if ex.get("intensity_reduction_possible", False):
                filtered.append(ex)
                intensity_warnings[ex["nameCN"]] = True
            else:
                alternatives = [alt for alt in exercises if alt["target_muscle"] == ex["target_muscle"] and alt["id"] != ex["id"] and not any(area in alt.get("risk_areas", []) for area in injured_areas)]
                if alternatives:
                    replaced[ex["nameCN"]] = alternatives[0]["nameCN"]
        else:
            filtered.append(ex)
    
    return filtered, replaced, intensity_warnings

def get_exercises(body_parts, category, injured_areas=[], excluded_parts=[]):
    """獲取動作列表"""
    exercises = [e for e in EXERCISES if e["category"] == category and e["bodyPart"] in body_parts and e["bodyPart"] not in excluded_parts]
    filtered, replaced, warnings = filter_exercises_by_injuries(exercises, injured_areas)
    return filtered, replaced, warnings

def get_past_best_weight(records, exercise_name):
    """獲取該動作的最高重量"""
    for record in records:
        try:
            details = json.loads(record.get("詳細", "{}"))
            for log in details.values():
                if log.get("exercise") == exercise_name and log.get("weight"):
                    return float(log.get("weight", 0))
        except:
            pass
    return None

def get_past_best_reps(records, exercise_name):
    """獲取該動作的最高次數"""
    for record in records:
        try:
            details = json.loads(record.get("詳細", "{}"))
            for log in details.values():
                if log.get("exercise") == exercise_name and log.get("reps"):
                    return int(log.get("reps", 0))
        except:
            pass
    return None

# ==================== 登入頁面 ====================
if "user_id" not in st.session_state:
    st.set_page_config(page_title="SmartFit - 登入", page_icon="💪")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("💪 SmartFit")
        st.subheader("智能健身系統")
        st.divider()
        
        username = st.text_input("👤 輸入用戶名稱", placeholder="例: 小王", key="login_username")
        
        if st.button("🚀 進入系統", use_container_width=True, type="primary", key="login_btn"):
            if username.strip():
                user_id, is_new = create_user(username)
                st.session_state.user_id = user_id
                st.session_state.username = username
                st.session_state.page = "home"
                st.session_state.selected_parts = []
                
                if is_new:
                    st.success(f"✅ 歡迎新用戶 {username}！")
                else:
                    st.success(f"👋 歡迎回來 {username}！")
                
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ 請輸入用戶名稱")
        
        st.divider()
        st.info("""
        📌 **說明**
        - ✅ 每個用戶有獨立的訓練紀錄
        - ✅ 數據永久保存（即使關閉瀏覽器）
        - ✅ 多人可以共用同一個裝置
        """)

else:
    # ==================== 已登入 ====================
    user_id = st.session_state.user_id
    username = st.session_state.username
    user_data = load_user_data(user_id)
    
    # 初始化訓練頁面狀態
    if "selected_parts" not in st.session_state:
        st.session_state.selected_parts = []
    if "selected_exercises_list" not in st.session_state:
        st.session_state.selected_exercises_list = []
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "workout" not in st.session_state:
        st.session_state.workout = None
    if "exercise_weights" not in st.session_state:
        st.session_state.exercise_weights = {}
    if "rest_timer_active" not in st.session_state:
        st.session_state.rest_timer_active = False
    if "rest_end_time" not in st.session_state:
        st.session_state.rest_end_time = None
    if "rest_skipped" not in st.session_state:
        st.session_state.rest_skipped = False
    
    st.set_page_config(page_title="SmartFit", page_icon="💪", layout="wide")
    
    with st.sidebar:
        st.title(f"💪 {username}")
        st.write(f"👤 用戶ID: {user_id[:8]}...")
        st.divider()
        
        if st.button("🏠 首頁", use_container_width=True, key="nav_home"):
            st.session_state.page = "home"
            st.rerun()
        if st.button("📊 統計", use_container_width=True, key="nav_stats"):
            st.session_state.page = "stats"
            st.rerun()
        if st.button("📈 趨勢", use_container_width=True, key="nav_trend"):
            st.session_state.page = "trend"
            st.rerun()
        if st.button("⚙️ 設置", use_container_width=True, key="nav_settings"):
            st.session_state.page = "settings"
            st.rerun()
        
        st.divider()
        if st.button("🚪 登出", use_container_width=True, key="logout_btn"):
            del st.session_state.user_id
            del st.session_state.username
            st.rerun()
    
    # ==================== 首頁 ====================
    if st.session_state.page == "home":
        st.title(f"💪 {username} 的訓練計畫")
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            mode = st.radio("訓練模式", ["🏠 徒手/啞鈴", "🏋️ 健身房儀器"], horizontal=True, key="mode_radio")
            category = "徒手/啞鈴" if "徒手" in mode else "健身房儀器"
        with col2:
            duration = st.radio("時長", [15, 30, 45, 60], horizontal=True, key="duration_radio")
        
        st.subheader("🏥 傷病部位")
        injured = st.multiselect("選擇受傷部位", INJURY_AREAS, key="injury_select")
        
        st.subheader("🎯 訓練部位")
        cols = st.columns(3)
        selected_parts = []
        for i, part in enumerate(BODY_PARTS):
            with cols[i % 3]:
                is_checked = st.checkbox(part, value=(part in st.session_state.selected_parts), key=f"part_check_{part}")
                if is_checked:
                    selected_parts.append(part)
        
        st.session_state.selected_parts = selected_parts
        
        if selected_parts:
            all_exercises, replaced, warnings = get_exercises(selected_parts, category, injured, [])
            
            if replaced:
                st.info(f"📌 動作替換: {chr(10).join([f'❌ {k} → ✅ {v}' for k, v in replaced.items()])}")
            
            st.subheader(f"🏆 可用動作 ({len(all_exercises)}個)")
            
            selected_exercises_list = st.session_state.selected_exercises_list
            
            cols = st.columns(2)
            for i, ex in enumerate(all_exercises):
                with cols[i % 2]:
                    if ex["filename"] and ex["filename"] in IMAGES_DATA:
                        st.image(IMAGES_DATA[ex["filename"]], use_column_width=True)
                    else:
                        st.info("⏳ 圖片準備中")
                    
                    st.write(f"**{ex['nameCN']}**")
                    st.write(f"難度: {ex['difficulty']} | {ex['sets']}組 × {ex['reps']}次")
                    
                    if ex['nameCN'] in warnings:
                        st.warning("⚠️ 請減輕重量")
                    
                    is_selected = any(selected.get("id") == ex["id"] for selected in selected_exercises_list)
                    if st.checkbox("✅ 選", value=is_selected, key=f"select_{ex['id']}"):
                        if not is_selected:
                            selected_exercises_list.append(ex)
                    else:
                        selected_exercises_list = [s for s in selected_exercises_list if s.get("id") != ex["id"]]
            
            st.session_state.selected_exercises_list = selected_exercises_list
            
            # 顯示已選動作清單
            if selected_exercises_list:
                st.divider()
                st.subheader("📋 已選動作清單")
                
                for idx, ex in enumerate(selected_exercises_list):
                    col_ex, col_cancel = st.columns([9, 1])
                    
                    with col_ex:
                        st.write(f"{idx + 1}. **{ex['nameCN']}** ({ex['sets']}組 × {ex['reps']}次)")
                    
                    with col_cancel:
                        if st.button("❌", key=f"remove_{ex['id']}", help="移除此動作"):
                            selected_exercises_list = [s for s in selected_exercises_list if s.get("id") != ex["id"]]
                            st.session_state.selected_exercises_list = selected_exercises_list
                            st.rerun()
                
                st.divider()
                st.success(f"✅ 已選 {len(selected_exercises_list)} 個動作 | 總組數: {sum(e['sets'] for e in selected_exercises_list)}")
                
                if st.button("🎬 開始訓練", use_container_width=True, type="primary", key="start_workout_btn"):
                    st.session_state.workout = {
                        "exercises": selected_exercises_list,
                        "start": datetime.now(),
                        "duration": duration
                    }
                    st.session_state.current_ex_idx = 0
                    st.session_state.current_set = 1
                    st.session_state.workout_log = {}
                    st.session_state.exercise_weights = {}
                    st.session_state.page = "workout"
                    st.rerun()
    
    # ==================== 訓練執行 ====================
    elif st.session_state.page == "workout" and st.session_state.workout:
        exs = st.session_state.workout["exercises"]
        current_ex_idx = st.session_state.get("current_ex_idx", 0)
        current_set = st.session_state.get("current_set", 1)
        
        total_sets = sum(e["sets"] for e in exs)
        completed_sets = sum(exs[i]["sets"] for i in range(current_ex_idx)) + (current_set - 1)
        progress = completed_sets / total_sets if total_sets > 0 else 0
        
        st.progress(progress, text=f"進度: {completed_sets}/{total_sets} 組")
        
        # ============ 休息計時器 ============
        if st.session_state.rest_timer_active and st.session_state.rest_end_time and not st.session_state.rest_skipped:
            remaining = (st.session_state.rest_end_time - datetime.now()).total_seconds()
            if remaining > 0:
                col_rest1, col_rest2, col_rest3 = st.columns([1, 2, 1])
                with col_rest2:
                    st.markdown(f"""
                    <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px;'>
                        <h1 style='color: white; margin: 0;'>⏱️ 休息中</h1>
                        <h2 style='color: #FFD700; margin: 10px 0;'>{int(remaining)} 秒</h2>
                        <p style='color: white; margin: 0;'>深呼吸，為下一組做好準備</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                col_skip1, col_skip2, col_skip3 = st.columns([1, 2, 1])
                with col_skip2:
                    if st.button("⏭️ 跳過休息", use_container_width=True, key="btn_skip_rest"):
                        st.session_state.rest_skipped = True
                        st.rerun()
                
                import time
                for i in range(int(remaining), 0, -1):
                    time.sleep(1)
                    if st.session_state.rest_skipped:
                        break
                    st.rerun()
                
                st.session_state.rest_timer_active = False
                st.session_state.rest_skipped = False
                st.success("✅ 休息時間到！準備下一組")
                st.rerun()
        
        if current_ex_idx < len(exs):
            ex = exs[current_ex_idx]
            
            col1, col2 = st.columns([1.5, 1])
            
            with col1:
                st.subheader(f"動作 {current_ex_idx + 1}/{len(exs)}: {ex['nameCN']}")
                if ex["filename"] and ex["filename"] in IMAGES_DATA:
                    st.image(IMAGES_DATA[ex["filename"]], use_column_width=True)
                else:
                    st.info("⏳ 圖片準備中")
            
            with col2:
                st.write(f"**難度**: {ex['difficulty']}")
                st.write(f"**部位**: {ex['bodyPart']}")
                st.write(f"**目標肌群**: {ex['target_muscle']}")
                st.write(f"**器材**: {ex['equipment']}")
                st.write(f"**節奏**: {ex['tempo']}")
                st.divider()
                
                st.metric("當前組數", f"{current_set}/{ex['sets']}")
                st.metric("每組次數", ex['reps'])
                
                st.divider()
                st.subheader("執行技巧:")
                for tip in ex["tips"]:
                    st.write(f"✅ {tip}")
            
            st.divider()
            
            # 訓練數據輸入
            st.subheader("📊 這一組的數據")
            col_data1, col_data2, col_data3 = st.columns(3)
            
            records = get_records(user_id) or []
            
            with col_data1:
                past_best_reps = get_past_best_reps(records, ex['nameCN'])
                actual_reps = st.number_input(
                    "實際完成次數",
                    min_value=1,
                    max_value=ex['reps'] + 5,
                    value=ex['reps'],
                    key=f"reps_{current_ex_idx}_{current_set}"
                )
                if past_best_reps and actual_reps > past_best_reps:
                    st.toast("🔥 突破紀錄了！", icon="🎉")
                if past_best_reps:
                    st.caption(f"歷史最高: {past_best_reps} 次")
            
            weight = 0
            if ex['require_weight']:
                with col_data2:
                    exercise_key = f"{ex['id']}"
                    default_weight = st.session_state.exercise_weights.get(exercise_key, 0.0)
                    
                    past_best_weight = get_past_best_weight(records, ex['nameCN'])
                    weight = st.number_input(
                        "重量 (kg/lb)",
                        min_value=0.0,
                        step=0.5,
                        value=default_weight,
                        key=f"weight_{current_ex_idx}_{current_set}"
                    )
                    
                    st.session_state.exercise_weights[exercise_key] = weight
                    
                    if past_best_weight and weight > past_best_weight:
                        st.toast("🔥 突破紀錄了！", icon="🎉")
                    if past_best_weight:
                        st.caption(f"歷史最高: {past_best_weight} kg")
            
            with col_data3:
                fatigue = st.slider(
                    "疲勞度 (1-10)",
                    1, 10, 5,
                    key=f"fatigue_{current_ex_idx}_{current_set}"
                )
            
            st.divider()
            
            # 控制按鈕
            c1, c2, c3 = st.columns(3)
            
            with c1:
                if st.button("⏭️ 跳過動作", use_container_width=True, key="btn_skip"):
                    st.session_state.current_ex_idx += 1
                    st.session_state.current_set = 1
                    st.rerun()
            
            with c2:
                if st.button("✅ 完成這組", use_container_width=True, key="btn_done", type="primary"):
                    volume = weight * actual_reps if ex['require_weight'] else actual_reps
                    
                    log_key = f"{current_ex_idx}_{current_set}"
                    if "workout_log" not in st.session_state:
                        st.session_state.workout_log = {}
                    
                    st.session_state.workout_log[log_key] = {
                        "exercise": ex['nameCN'],
                        "set": current_set,
                        "reps": actual_reps,
                        "weight": weight if ex['require_weight'] else None,
                        "fatigue": fatigue,
                        "volume": volume
                    }
                    
                    if current_set < ex["sets"]:
                        rest_time = REST_TIMES.get(ex['difficulty'], 60)
                        st.session_state.rest_timer_active = True
                        st.session_state.rest_end_time = datetime.now() + timedelta(seconds=rest_time)
                        st.session_state.rest_skipped = False
                        st.session_state.current_set += 1
                    else:
                        st.session_state.current_ex_idx += 1
                        st.session_state.current_set = 1
                    st.rerun()
            
            with c3:
                if st.button("⏹️ 結束訓練", use_container_width=True, key="btn_finish"):
                    dur = int((datetime.now() - st.session_state.workout["start"]).total_seconds() / 60)
                    total_volume = sum(log.get("volume", 0) for log in st.session_state.workout_log.values())
                    
                    record = {
                        "日期": datetime.now().strftime("%Y-%m-%d"),
                        "動作數": len(exs),
                        "組數": sum(e["sets"] for e in exs),
                        "時長(分)": dur,
                        "熱量": int(dur * 7),
                        "總Volume": int(total_volume),
                        "詳細": json.dumps(st.session_state.workout_log)
                    }
                    
                    save_user_data(user_id, {**user_data, "records": user_data.get("records", []) + [record]})
                    
                    st.session_state.workout = None
                    st.session_state.page = "stats"
                    st.balloons()
                    st.rerun()
        else:
            # 訓練完成，顯示完成界面
            st.success("🎉 訓練完成！")
            st.divider()
            
            dur = int((datetime.now() - st.session_state.workout["start"]).total_seconds() / 60)
            total_volume = sum(log.get("volume", 0) for log in st.session_state.workout_log.values())
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("動作數", len(exs))
            col2.metric("組數", sum(e["sets"] for e in exs))
            col3.metric("時長", f"{dur}分")
            col4.metric("總Volume", f"{int(total_volume)}")
            
            st.divider()
            
            if st.button("📊 查看統計", use_container_width=True, type="primary", key="view_stats_btn"):
                dur = int((datetime.now() - st.session_state.workout["start"]).total_seconds() / 60)
                total_volume = sum(log.get("volume", 0) for log in st.session_state.workout_log.values())
                
                record = {
                    "日期": datetime.now().strftime("%Y-%m-%d"),
                    "動作數": len(exs),
                    "組數": sum(e["sets"] for e in exs),
                    "時長(分)": dur,
                    "熱量": int(dur * 7),
                    "總Volume": int(total_volume),
                    "詳細": json.dumps(st.session_state.workout_log)
                }
                
                save_user_data(user_id, {**user_data, "records": user_data.get("records", []) + [record]})
                
                st.session_state.workout = None
                st.session_state.page = "stats"
                st.balloons()
                st.rerun()
    
    # ==================== 統計 ====================
    elif st.session_state.page == "stats":
        st.title(f"📊 {username} 的訓練統計")
        records = get_records(user_id)
        
        if records:
            df = pd.DataFrame(records)
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("訓練次", len(records))
            c2.metric("總組數", int(df['組數'].sum()))
            c3.metric("總時長", f"{int(df['時長(分)'].sum())}分")
            c4.metric("總熱量", int(df['熱量'].sum()))
            c5.metric("累計Volume", f"{int(df['總Volume'].sum())}")
            
            display_df = df[['日期', '動作數', '組數', '時長(分)', '總Volume']].copy()
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("暫無訓練記錄")
    
    # ==================== 趨勢 ====================
    elif st.session_state.page == "trend":
        st.title(f"📈 {username} 的訓練趨勢")
        records = get_records(user_id)
        
        if records:
            df = pd.DataFrame(records)
            df['日期'] = pd.to_datetime(df['日期'])
            df_sorted = df.sort_values('日期')
            
            st.subheader("週訓練量趨勢")
            df_sorted['週'] = df_sorted['日期'].dt.to_period('W')
            weekly = df_sorted.groupby('週').agg({'總Volume': 'sum'}).reset_index()
            weekly['週'] = weekly['週'].astype(str)
            st.line_chart(weekly.set_index('週')['總Volume'])
            
            st.subheader("月訓練量趨勢")
            df_sorted['月'] = df_sorted['日期'].dt.to_period('M')
            monthly = df_sorted.groupby('月').agg({'總Volume': 'sum'}).reset_index()
            monthly['月'] = monthly['月'].astype(str)
            st.bar_chart(monthly.set_index('月')['總Volume'])
        else:
            st.info("暫無訓練數據")
    
    # ==================== 設置 ====================
    elif st.session_state.page == "settings":
        st.title("⚙️ 設置")
        
        name = st.text_input("姓名", user_data.get("user_info", {}).get("name", ""), key="user_name_input")
        age = st.slider("年齡", 15, 100, user_data.get("user_info", {}).get("age", 25), key="user_age_slider")
        
        if st.button("💾 保存", use_container_width=True, key="save_settings_btn"):
            update_user_info(user_id, {"name": name, "age": age})
            st.success("✅ 已保存")
        
        st.divider()
        st.success("""
        ✅ SmartFit v18 - 完成後自動跳轉統計
        
        🎯 功能：
        ✅ 訓練完成自動跳轉統計頁
        ✅ 休息計時器（可跳過）
        ✅ 重量記憶（同動作共用）
        ✅ 已選動作可取消
        ✅ 多用戶獨立記錄
        ✅ 完整訓練系統
        """)
