import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from image_data import IMAGES_DATA
import json

st.set_page_config(page_title="SmartFit", page_icon="💪", layout="wide")

BODY_PARTS = ["胸部", "背部", "肩膀", "手臂", "腿部", "核心"]

# ==================== 50個動作 ====================
EXERCISES = [
    # 徒手/啞鈴 (1-20)
    {"id": "001", "nameCN": "俯臥撑", "bodyPart": "胸部", "difficulty": "初級", "sets": 3, "reps": 12, "category": "徒手/啞鈴", "equipment": "無", "filename": "push_ups.jpg", "require_weight": False, "tempo": "下放2秒 撐起1秒", "tips": ["保持身體直線", "降低至胸部", "推回起始位置"]},
    {"id": "002", "nameCN": "寬距俯臥撑", "bodyPart": "胸部", "difficulty": "初級", "sets": 3, "reps": 10, "category": "徒手/啞鈴", "equipment": "無", "filename": "wide_push_ups.jpg", "require_weight": False, "tempo": "下放2秒 撐起1秒", "tips": ["雙手寬距", "保持直線", "完整範圍"]},
    {"id": "003", "nameCN": "菱形俯臥撑", "bodyPart": "胸部", "difficulty": "中級", "sets": 3, "reps": 8, "category": "徒手/啞鈴", "equipment": "無", "filename": "diamond_push_ups.jpg", "require_weight": False, "tempo": "下放2秒 撐起1秒", "tips": ["雙手在胸下", "肘部靠近", "完全伸展"]},
    {"id": "004", "nameCN": "下斜俯臥撑", "bodyPart": "胸部", "difficulty": "中級", "sets": 3, "reps": 10, "category": "徒手/啞鈴", "equipment": "無", "filename": "decline_push_ups.jpg", "require_weight": False, "tempo": "下放2秒 撐起1秒", "tips": ["雙腳放高", "身體直線", "完整動作"]},
    {"id": "005", "nameCN": "箭手俯臥撑", "bodyPart": "胸部", "difficulty": "高級", "sets": 3, "reps": 6, "category": "徒手/啞鈴", "equipment": "無", "filename": "archer_push_ups.jpg", "require_weight": False, "tempo": "下放2秒 撐起1秒", "tips": ["一側彎曲", "一側伸直", "平衡訓練"]},
    {"id": "006", "nameCN": "引體向上", "bodyPart": "背部", "difficulty": "中級", "sets": 3, "reps": 8, "category": "徒手/啞鈴", "equipment": "無", "filename": "pull_ups.jpg", "require_weight": False, "tempo": "下放2秒 撐起1秒", "tips": ["握距寬", "下巴超杆", "控制下降"]},
    {"id": "007", "nameCN": "窄握引體向上", "bodyPart": "背部", "difficulty": "中級", "sets": 3, "reps": 8, "category": "徒手/啞鈴", "equipment": "無", "filename": "chin_ups.jpg", "require_weight": False, "tempo": "下放2秒 撐起1秒", "tips": ["掌心向內", "肘部靠近", "平順動作"]},
    {"id": "008", "nameCN": "反向划船", "bodyPart": "背部", "difficulty": "初級", "sets": 3, "reps": 12, "category": "徒手/啞鈴", "equipment": "無", "filename": "reverse_rows.jpg", "require_weight": False, "tempo": "下放2秒 拉起1秒", "tips": ["身體直線", "拉至胸部", "控制下降"]},
    {"id": "009", "nameCN": "啞鈴划船", "bodyPart": "背部", "difficulty": "中級", "sets": 4, "reps": 10, "category": "徒手/啞鈴", "equipment": "啞鈴", "filename": "dumbbell_rows.jpg", "require_weight": True, "tempo": "下放2秒 拉起1秒", "tips": ["膝蓋跪", "核心穩定", "拉至腰"]},
    {"id": "010", "nameCN": "超人式", "bodyPart": "背部", "difficulty": "初級", "sets": 3, "reps": 30, "category": "徒手/啞鈴", "equipment": "無", "filename": "superman_hold.jpg", "require_weight": False, "tempo": "靜止2秒", "tips": ["手臂前伸", "腿後伸", "胸部離地"]},
    {"id": "011", "nameCN": "深蹲", "bodyPart": "腿部", "difficulty": "初級", "sets": 3, "reps": 15, "category": "徒手/啞鈴", "equipment": "無", "filename": "squats.jpg", "require_weight": False, "tempo": "下放2秒 撐起1秒", "tips": ["挺胸", "臀部後坐", "腳跟推起"]},
    {"id": "012", "nameCN": "跳躍深蹲", "bodyPart": "腿部", "difficulty": "中級", "sets": 3, "reps": 12, "category": "徒手/啞鈴", "equipment": "無", "filename": "jump_squats.jpg", "require_weight": False, "tempo": "爆發式", "tips": ["全力跳", "軟著陸", "快速起身"]},
    {"id": "013", "nameCN": "弓步", "bodyPart": "腿部", "difficulty": "初級", "sets": 3, "reps": 12, "category": "徒手/啞鈴", "equipment": "無", "filename": "lunges.jpg", "require_weight": False, "tempo": "下放2秒 撐起1秒", "tips": ["前腳90度", "後腳接地", "保持直立"]},
    {"id": "014", "nameCN": "啞鈴深蹲", "bodyPart": "腿部", "difficulty": "中級", "sets": 4, "reps": 10, "category": "徒手/啞鈴", "equipment": "啞鈴", "filename": "dumbbell_squats.jpg", "require_weight": True, "tempo": "下放2秒 撐起1秒", "tips": ["拿著啞鈴", "挺胸下蹲", "腳跟推起"]},
    {"id": "015", "nameCN": "提踵", "bodyPart": "腿部", "difficulty": "初級", "sets": 3, "reps": 20, "category": "徒手/啞鈴", "equipment": "無", "filename": "calf_raises.jpg", "require_weight": False, "tempo": "上升1秒 下放1秒", "tips": ["站直", "提起腳跟", "控制下降"]},
    {"id": "016", "nameCN": "棒式", "bodyPart": "核心", "difficulty": "初級", "sets": 3, "reps": 30, "category": "徒手/啞鈴", "equipment": "無", "filename": "plank.jpg", "require_weight": False, "tempo": "靜止", "tips": ["身體直線", "核心緊縮", "臀部不下沉"]},
    {"id": "017", "nameCN": "側棒式", "bodyPart": "核心", "difficulty": "初級", "sets": 3, "reps": 20, "category": "徒手/啞鈴", "equipment": "無", "filename": "side_plank.jpg", "require_weight": False, "tempo": "靜止", "tips": ["身體直線", "核心收緊", "臀部不下沉"]},
    {"id": "018", "nameCN": "仰臥起坐", "bodyPart": "核心", "difficulty": "初級", "sets": 3, "reps": 15, "category": "徒手/啞鈴", "equipment": "無", "filename": "sit_ups.jpg", "require_weight": False, "tempo": "上起1秒 下放1秒", "tips": ["膝蓋彎曲", "不拉脖子", "胸部向膝"]},
    {"id": "019", "nameCN": "爬山者", "bodyPart": "核心", "difficulty": "中級", "sets": 3, "reps": 20, "category": "徒手/啞鈴", "equipment": "無", "filename": "mountain_climbers.jpg", "require_weight": False, "tempo": "快速", "tips": ["快速交替", "保持俯臥撑", "核心緊縮"]},
    {"id": "020", "nameCN": "抬腿", "bodyPart": "核心", "difficulty": "初級", "sets": 3, "reps": 12, "category": "徒手/啞鈴", "equipment": "無", "filename": "leg_raises.jpg", "require_weight": False, "tempo": "上升1秒 下放2秒", "tips": ["背部貼地", "腿部直", "控制速度"]},
    
    # 健身房儀器 (21-27 有圖片)
    {"id": "021", "nameCN": "槓鈴臥推", "bodyPart": "胸部", "difficulty": "中級", "sets": 4, "reps": 8, "category": "健身房儀器", "equipment": "槓鈴", "filename": "barbell_bench.jpg", "require_weight": True, "tempo": "下放2秒 推起1秒", "tips": ["背貼板", "肩膀穩定", "平順動作"]},
    {"id": "022", "nameCN": "胸部推蹬機", "bodyPart": "胸部", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "推蹬機", "filename": "chest_machine.jpg", "require_weight": True, "tempo": "下放2秒 推起1秒", "tips": ["坐直對齊", "完全推出", "控制回放"]},
    {"id": "023", "nameCN": "拉力機夾胸", "bodyPart": "胸部", "difficulty": "中級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "拉力機", "filename": "cable_flyes.jpg", "require_weight": True, "tempo": "外展2秒 內收1秒", "tips": ["手臂微彎", "控制回放", "集中收縮"]},
    {"id": "024", "nameCN": "史密斯機臥推", "bodyPart": "胸部", "difficulty": "初級", "sets": 4, "reps": 12, "category": "健身房儀器", "equipment": "史密斯機", "filename": "smith_machine_bench.jpg", "require_weight": True, "tempo": "下放2秒 推起1秒", "tips": ["槓在肩", "直線下降", "完整動作"]},
    {"id": "025", "nameCN": "胸部飛鳥機", "bodyPart": "胸部", "difficulty": "中級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "飛鳥機", "filename": "pec_deck.jpg", "require_weight": True, "tempo": "外展2秒 內收1秒", "tips": ["手臂微彎", "控制回放", "充分收縮"]},
    {"id": "026", "nameCN": "槓鈴划船", "bodyPart": "背部", "difficulty": "中級", "sets": 4, "reps": 8, "category": "健身房儀器", "equipment": "槓鈴", "filename": "barbell_rows.jpg", "require_weight": True, "tempo": "下放2秒 拉起1秒", "tips": ["膝蓋微彎", "背部直", "拉至腹"]},
    {"id": "027", "nameCN": "下拉機", "bodyPart": "背部", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "下拉機", "filename": "lat_pulldown.jpg", "require_weight": True, "tempo": "下放2秒 拉起1秒", "tips": ["拉至胸", "控制回放", "核心緊縮"]},
    
    # 28-50 無圖片
    {"id": "028", "nameCN": "拉力機划船", "bodyPart": "背部", "difficulty": "初級", "sets": 4, "reps": 12, "category": "健身房儀器", "equipment": "拉力機", "filename": None, "require_weight": True, "tempo": "下放2秒 拉起1秒", "tips": ["坐直挺胸", "拉至腹", "控制回放"]},
    {"id": "029", "nameCN": "T槓划船", "bodyPart": "背部", "difficulty": "中級", "sets": 4, "reps": 10, "category": "健身房儀器", "equipment": "T槓", "filename": None, "require_weight": True, "tempo": "下放2秒 拉起1秒", "tips": ["身體穩定", "拉至胸", "控制下降"]},
    {"id": "030", "nameCN": "背闊肌拉力機", "bodyPart": "背部", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "背闊肌機", "filename": None, "require_weight": True, "tempo": "下放2秒 拉起1秒", "tips": ["坐直", "拉至腹", "控制回放"]},
    {"id": "031", "nameCN": "槓鈴肩推", "bodyPart": "肩膀", "difficulty": "中級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "槓鈴", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "tips": ["槓在肩", "上推至頂", "控制下降"]},
    {"id": "032", "nameCN": "肩推機", "bodyPart": "肩膀", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "肩推機", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "tips": ["坐直", "推至頂部", "控制下降"]},
    {"id": "033", "nameCN": "側平舉機", "bodyPart": "肩膀", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "側平舉機", "filename": None, "require_weight": True, "tempo": "上升2秒 下放2秒", "tips": ["坐直", "抬至肩高", "控制速度"]},
    {"id": "034", "nameCN": "反向夾胸機", "bodyPart": "肩膀", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "夾胸機", "filename": None, "require_weight": True, "tempo": "外展2秒 內收1秒", "tips": ["坐直", "手臂向外", "控制回放"]},
    {"id": "035", "nameCN": "前平舉機", "bodyPart": "肩膀", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "前平舉機", "filename": None, "require_weight": True, "tempo": "上升2秒 下放2秒", "tips": ["坐直", "推至肩高", "控制速度"]},
    {"id": "036", "nameCN": "繩索下壓", "bodyPart": "手臂", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "拉力機", "filename": None, "require_weight": True, "tempo": "下放1秒 推起1秒", "tips": ["肘部不動", "完全伸展", "控制回放"]},
    {"id": "037", "nameCN": "拉力機彎舉", "bodyPart": "手臂", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "拉力機", "filename": None, "require_weight": True, "tempo": "上升1秒 下放2秒", "tips": ["肘部固定", "張力持續", "控制回放"]},
    {"id": "038", "nameCN": "三頭撐體機", "bodyPart": "手臂", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "撐體機", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "tips": ["身體向前", "肘部90度", "完整動作"]},
    {"id": "039", "nameCN": "二頭彎舉機", "bodyPart": "手臂", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "彎舉機", "filename": None, "require_weight": True, "tempo": "上升1秒 下放2秒", "tips": ["坐直", "充分收縮", "控制速度"]},
    {"id": "040", "nameCN": "三頭肌機器", "bodyPart": "手臂", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "三頭機", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "tips": ["坐直", "完全伸展", "控制回放"]},
    {"id": "041", "nameCN": "推蹬機", "bodyPart": "腿部", "difficulty": "初級", "sets": 3, "reps": 15, "category": "健身房儀器", "equipment": "推蹬機", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "tips": ["腳在機器", "完全伸展", "控制下降"]},
    {"id": "042", "nameCN": "腿部卷舉機", "bodyPart": "腿部", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "卷舉機", "filename": None, "require_weight": True, "tempo": "上升1秒 下放2秒", "tips": ["坐直", "卷至胸", "控制回放"]},
    {"id": "043", "nameCN": "腿部伸展機", "bodyPart": "腿部", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "伸展機", "filename": None, "require_weight": True, "tempo": "伸展1秒 下放2秒", "tips": ["坐直", "完全伸展", "控制回放"]},
    {"id": "044", "nameCN": "哈克深蹲機", "bodyPart": "腿部", "difficulty": "中級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "哈克機", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "tips": ["肩膀靠機", "深蹲至平行", "完整動作"]},
    {"id": "045", "nameCN": "槓鈴深蹲", "bodyPart": "腿部", "difficulty": "中級", "sets": 4, "reps": 8, "category": "健身房儀器", "equipment": "槓鈴", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "tips": ["槓在肩", "直立姿勢", "深蹲至平行"]},
    {"id": "046", "nameCN": "拉力卷腹", "bodyPart": "核心", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "拉力機", "filename": None, "require_weight": True, "tempo": "下放2秒 收起1秒", "tips": ["膝蓋彎", "卷至膝", "控制回放"]},
    {"id": "047", "nameCN": "腹肌卷腹機", "bodyPart": "核心", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "卷腹機", "filename": None, "require_weight": True, "tempo": "收起1秒 下放2秒", "tips": ["坐直對齊", "卷起完整", "控制回放"]},
    {"id": "048", "nameCN": "滑輪卷腹", "bodyPart": "核心", "difficulty": "中級", "sets": 3, "reps": 10, "category": "健身房儀器", "equipment": "滑輪", "filename": None, "require_weight": False, "tempo": "向前滾2秒 回收1秒", "tips": ["膝蓋跪", "向前滾", "回收縮腹"]},
    {"id": "049", "nameCN": "旋轉腹肌機", "bodyPart": "核心", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "旋轉機", "filename": None, "require_weight": True, "tempo": "旋轉1秒 回中1秒", "tips": ["坐直", "緩慢旋轉", "控制速度"]},
    {"id": "050", "nameCN": "懸掛抬腿", "bodyPart": "核心", "difficulty": "中級", "sets": 3, "reps": 10, "category": "健身房儀器", "equipment": "單槓", "filename": None, "require_weight": False, "tempo": "上升2秒 下放2秒", "tips": ["握把穩定", "腿抬至水平", "控制下降"]},
]

TRAINING_SUGGESTIONS = {
    15: {"name": "快速訓練 (15分)", "desc": "3-4個動作，低組數", "exercises_count": (3, 4), "sets_multiplier": 1},
    30: {"name": "標準訓練 (30分)", "desc": "5-6個動作，中等組數", "exercises_count": (5, 6), "sets_multiplier": 1},
    45: {"name": "加強訓練 (45分)", "desc": "7-8個動作，正常組數", "exercises_count": (7, 8), "sets_multiplier": 1},
    60: {"name": "完整訓練 (60分)", "desc": "9-10個動作，高組數", "exercises_count": (9, 10), "sets_multiplier": 1.2},
}

REST_TIMES = {
    "初級": 60,
    "中級": 90,
    "高級": 120,
}

# ==================== Session State ====================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "user" not in st.session_state:
    st.session_state.user = {"name": "", "age": 25}
if "records" not in st.session_state:
    st.session_state.records = []
if "workout" not in st.session_state:
    st.session_state.workout = None
if "current_set" not in st.session_state:
    st.session_state.current_set = 1
if "current_ex_idx" not in st.session_state:
    st.session_state.current_ex_idx = 0
if "selected_exercises" not in st.session_state:
    st.session_state.selected_exercises = []
if "excluded_parts" not in st.session_state:
    st.session_state.excluded_parts = []
if "rest_timer_active" not in st.session_state:
    st.session_state.rest_timer_active = False
if "rest_end_time" not in st.session_state:
    st.session_state.rest_end_time = None
if "workout_log" not in st.session_state:
    st.session_state.workout_log = {}

# ==================== 函數 ====================
def get_exercises(body_parts, category, excluded_parts=[]):
    return [e for e in EXERCISES 
            if e["category"] == category 
            and e["bodyPart"] in body_parts
            and e["bodyPart"] not in excluded_parts]

def display_image(filename):
    if filename and filename in IMAGES_DATA:
        st.image(IMAGES_DATA[filename], use_column_width=True)
        return True
    return False

def calculate_estimated_time(exercises):
    total_sets = sum(e["sets"] for e in exercises)
    estimated = int(total_sets * 1.5 + len(exercises) * 0.5)
    return estimated

def start_rest_timer(seconds):
    st.session_state.rest_timer_active = True
    st.session_state.rest_end_time = datetime.now() + timedelta(seconds=seconds)

# ==================== 側邊欄 ====================
with st.sidebar:
    st.title("💪 SmartFit")
    st.write("✅ 已上傳: 27/50 張圖片")
    st.write("📍 進度: 54%")
    
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

# ==================== 首頁 ====================
if st.session_state.page == "home":
    st.title("💪 SmartFit - 您的私人健身教練")
    
    col1, col2 = st.columns(2)
    with col1:
        mode = st.radio("訓練模式", ["🏠 徒手/啞鈴", "🏋️ 健身房儀器"], key="mode_select")
        category = "徒手/啞鈴" if "徒手" in mode else "健身房儀器"
    with col2:
        duration = st.radio("訓練時長", [15, 30, 45, 60], horizontal=True, key="duration_select")
    
    # 排除部位設定
    st.subheader("⚠️ 排除部位（有受傷或不適）")
    excluded = st.multiselect("選擇要排除的部位", BODY_PARTS, key="exclude_parts")
    st.session_state.excluded_parts = excluded
    if excluded:
        st.warning(f"已排除: {', '.join(excluded)}")
    
    # 訓練建議
    suggestion = TRAINING_SUGGESTIONS[duration]
    st.info(f"""
    📋 {suggestion['name']}
    {suggestion['desc']}
    建議選擇 {suggestion['exercises_count'][0]}-{suggestion['exercises_count'][1]} 個動作
    """)
    
    st.divider()
    st.subheader("🎯 選擇訓練部位")
    cols = st.columns(3)
    selected_parts = []
    for i, part in enumerate(BODY_PARTS):
        with cols[i % 3]:
            if st.checkbox(part, key=f"part_{part}"):
                selected_parts.append(part)
    
    st.divider()
    
    if selected_parts:
        st.success(f"✅ 已選擇: {', '.join(selected_parts)}")
        
        all_exercises = get_exercises(selected_parts, category, excluded)
        
        if all_exercises:
            st.subheader(f"🏆 可用動作 ({len(all_exercises)}個)")
            
            st.session_state.selected_exercises = []
            
            cols = st.columns(2)
            col_idx = 0
            
            for ex in all_exercises:
                with cols[col_idx % 2]:
                    if ex["filename"] and ex["filename"] in IMAGES_DATA:
                        st.image(IMAGES_DATA[ex["filename"]], use_column_width=True)
                    else:
                        st.info("⏳ 圖片準備中")
                    
                    st.write(f"**{ex['nameCN']}**")
                    st.write(f"難度: {ex['difficulty']} | 部位: {ex['bodyPart']}")
                    st.write(f"建議: {ex['sets']}組 × {ex['reps']}次")
                    if ex['require_weight']:
                        st.write("🏋️ 需要輸入重量")
                    
                    if st.checkbox("✅ 選擇", key=f"select_{ex['id']}"):
                        if ex not in st.session_state.selected_exercises:
                            st.session_state.selected_exercises.append(ex)
                    
                    st.divider()
                    col_idx += 1
            
            st.divider()
            
            if st.session_state.selected_exercises:
                selected_count = len(st.session_state.selected_exercises)
                total_sets = sum(e["sets"] for e in st.session_state.selected_exercises)
                estimated_time = calculate_estimated_time(st.session_state.selected_exercises)
                
                st.success(f"✅ 已選擇 {selected_count} 個動作 | 總共 {total_sets} 組 | 預計時間: {estimated_time} 分鐘")
                
                if st.button("🎬 開始訓練", use_container_width=True, key="btn_start", type="primary"):
                    st.session_state.workout = {
                        "exercises": st.session_state.selected_exercises,
                        "start": datetime.now(),
                        "duration": duration
                    }
                    st.session_state.current_set = 1
                    st.session_state.current_ex_idx = 0
                    st.session_state.workout_log = {}
                    st.session_state.page = "workout"
                    st.rerun()
            else:
                st.info("👈 請先選擇要訓練的動作")

# ==================== 訓練執行 ====================
elif st.session_state.page == "workout":
    if st.session_state.workout:
        exs = st.session_state.workout["exercises"]
        current_ex_idx = st.session_state.current_ex_idx
        current_set = st.session_state.current_set
        
        # 進度條
        total_sets = sum(e["sets"] for e in exs)
        completed_sets = sum(exs[i]["sets"] for i in range(current_ex_idx)) + (current_set - 1)
        progress = completed_sets / total_sets if total_sets > 0 else 0
        
        st.progress(progress, text=f"進度: {completed_sets}/{total_sets} 組")
        
        # 休息計時器
        if st.session_state.rest_timer_active and st.session_state.rest_end_time:
            remaining = (st.session_state.rest_end_time - datetime.now()).total_seconds()
            if remaining > 0:
                st.warning(f"⏱️ 休息中... {int(remaining)} 秒")
            else:
                st.session_state.rest_timer_active = False
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
            
            with col_data1:
                actual_reps = st.number_input(
                    "實際完成次數",
                    min_value=1,
                    max_value=ex['reps'] + 5,
                    value=ex['reps'],
                    key=f"reps_{current_ex_idx}_{current_set}"
                )
            
            weight = 0
            if ex['require_weight']:
                with col_data2:
                    weight = st.number_input(
                        "重量 (kg/lb)",
                        min_value=0.0,
                        step=0.5,
                        key=f"weight_{current_ex_idx}_{current_set}"
                    )
            
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
                    # 記錄訓練數據
                    log_key = f"{current_ex_idx}_{current_set}"
                    st.session_state.workout_log[log_key] = {
                        "exercise": ex['nameCN'],
                        "set": current_set,
                        "reps": actual_reps,
                        "weight": weight if ex['require_weight'] else None,
                        "fatigue": fatigue
                    }
                    
                    if current_set < ex["sets"]:
                        # 開始休息計時
                        rest_time = REST_TIMES.get(ex['difficulty'], 60)
                        start_rest_timer(rest_time)
                        st.session_state.current_set += 1
                    else:
                        st.session_state.current_ex_idx += 1
                        st.session_state.current_set = 1
                    st.rerun()
            
            with c3:
                if st.button("⏹️ 結束訓練", use_container_width=True, key="btn_finish"):
                    dur = int((datetime.now() - st.session_state.workout["start"]).total_seconds() / 60)
                    st.session_state.records.append({
                        "日期": datetime.now().strftime("%Y-%m-%d"),
                        "動作數": len(exs),
                        "組數": sum(e["sets"] for e in exs),
                        "時長(分)": dur,
                        "熱量": int(dur * 7)
                    })
                    st.session_state.workout = None
                    st.session_state.page = "stats"
                    st.balloons()
                    st.rerun()
        else:
            st.success("🎉 訓練完成！")
            dur = int((datetime.now() - st.session_state.workout["start"]).total_seconds() / 60)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("動作數", len(exs))
            c2.metric("組數", sum(e["sets"] for e in exs))
            c3.metric("時長", f"{dur}分")
            c4.metric("熱量", int(dur * 7))

# ==================== 統計 ====================
elif st.session_state.page == "stats":
    st.title("📊 訓練統計")
    if st.session_state.records:
        df = pd.DataFrame(st.session_state.records)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("訓練次", len(st.session_state.records))
        c2.metric("總組數", int(df['組數'].sum()))
        c3.metric("總時長", f"{int(df['時長(分)'].sum())}分")
        c4.metric("總熱量", int(df['熱量'].sum()))
        
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("還沒有訓練記錄")

# ==================== 趨勢分析 ====================
elif st.session_state.page == "trend":
    st.title("📈 訓練趨勢")
    if st.session_state.records:
        df = pd.DataFrame(st.session_state.records)
        df['日期'] = pd.to_datetime(df['日期'])
        df_sorted = df.sort_values('日期')
        
        # 週趨勢
        st.subheader("📊 週訓練量趨勢")
        df_sorted['週'] = df_sorted['日期'].dt.to_period('W')
        weekly = df_sorted.groupby('週').agg({
            '組數': 'sum',
            '時長(分)': 'sum',
            '熱量': 'sum'
        }).reset_index()
        weekly['週'] = weekly['週'].astype(str)
        
        st.line_chart(weekly.set_index('週')[['組數']])
        
        # 月趨勢
        st.subheader("📊 月訓練量趨勢")
        df_sorted['月'] = df_sorted['日期'].dt.to_period('M')
        monthly = df_sorted.groupby('月').agg({
            '組數': 'sum',
            '時長(分)': 'sum',
            '熱量': 'sum'
        }).reset_index()
        monthly['月'] = monthly['月'].astype(str)
        
        st.bar_chart(monthly.set_index('月')['組數'])
    else:
        st.info("暫無訓練數據")

# ==================== 設置 ====================
elif st.session_state.page == "settings":
    st.title("⚙️ 設置")
    st.session_state.user["name"] = st.text_input("姓名", st.session_state.user["name"])
    st.session_state.user["age"] = st.slider("年齡", 15, 100, st.session_state.user["age"])
    
    c1, c2, c3 = st.columns(3)
    c1.metric("版本", "12.0 完整版")
    c2.metric("動作", "50")
    c3.metric("圖片進度", "27/50 (54%)")
    
    st.divider()
    st.success("""
    ✅ SmartFit v12 - 全面優化
    
    🎯 新增功能：
    ✅ 排除部位設定
    ✅ 自動休息計時器
    ✅ 訓練數據實時修改
    ✅ 疲勞度追蹤
    ✅ 重量記錄
    ✅ 節奏提示
    ✅ 週/月趨勢分析
    ✅ 離心/向心時間提示
    """)
