import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from image_data import IMAGES_DATA
from users_database import create_user, load_user_data, save_user_data, get_records, update_user_info
import json
import time

st.set_page_config(page_title="SmartFit", page_icon="💪", layout="centered", initial_sidebar_state="collapsed")

# ==================== 手機優化 CSS ====================
st.markdown("""
<style>
    /* 縮小頂部與兩側留白 */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        max-width: 100% !important;
    }
    
    /* 按鈕加大,方便手指點擊 */
    .stButton > button {
        min-height: 3rem !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
    }
    
    /* number_input 字體加大,觸控更容易 */
    .stNumberInput input {
        font-size: 1.3rem !important;
        text-align: center !important;
        height: 3rem !important;
    }
    
    /* slider 加大 */
    .stSlider {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
    }
    
    /* 圖片限制最大高度,避免手機上過大 */
    .stImage img {
        max-height: 280px !important;
        object-fit: contain !important;
        border-radius: 12px !important;
    }
    
    /* checkbox 加大 */
    .stCheckbox {
        font-size: 1.05rem !important;
    }
    
    /* metric 卡片優化 */
    [data-testid="stMetric"] {
        background-color: rgba(102, 126, 234, 0.08);
        padding: 0.6rem;
        border-radius: 10px;
        text-align: center;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 1.3rem !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
    }
    
    /* tab 字體調整 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-size: 0.95rem;
        padding: 0.6rem 0.8rem;
    }
    
    /* radio 按鈕橫排 */
    .stRadio > div {
        gap: 0.5rem;
    }
    
    /* 隱藏 Streamlit 預設選單 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 標題縮小一點,避免擠壓 */
    h1 { font-size: 1.6rem !important; }
    h2 { font-size: 1.3rem !important; }
    h3 { font-size: 1.1rem !important; }
    
    /* 動作卡片樣式 */
    .exercise-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 12px;
        border-radius: 12px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

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
    {"id": "059", "nameCN": "窄距俯臥撑(三頭)", "bodyPart": "手臂", "target_muscle": "三頭肌", "difficulty": "中級", "sets": 3, "reps": 10, "category": "徒手/啞鈴", "equipment": "無", "filename": None, "require_weight": False, "tempo": "下放2秒 推起1秒", "risk_areas": ["肘部", "腕部"], "intensity_reduction_possible": True, "tips": ["雙手靠近", "肘部貼身", "完整動作"]},
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
    
    # 健身房儀器 - 胸部
    {"id": "021", "nameCN": "槓鈴臥推", "bodyPart": "胸部", "target_muscle": "胸肌", "difficulty": "中級", "sets": 4, "reps": 8, "category": "健身房儀器", "equipment": "槓鈴", "filename": "barbell_bench.jpg", "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["肩膀", "肘部"], "intensity_reduction_possible": True, "tips": ["背貼板", "肩膀穩定", "平順動作"]},
    {"id": "022", "nameCN": "胸部推蹬機", "bodyPart": "胸部", "target_muscle": "胸肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "推蹬機", "filename": "chest_machine.jpg", "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["肩膀", "肘部"], "intensity_reduction_possible": True, "tips": ["坐直對齊", "完全推出", "控制回放"]},
    {"id": "023", "nameCN": "拉力機夾胸", "bodyPart": "胸部", "target_muscle": "胸肌", "difficulty": "中級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "拉力機", "filename": "cable_flyes.jpg", "require_weight": True, "tempo": "外展2秒 內收1秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["手臂微彎", "控制回放", "集中收縮"]},
    {"id": "024", "nameCN": "史密斯機臥推", "bodyPart": "胸部", "target_muscle": "胸肌", "difficulty": "初級", "sets": 4, "reps": 12, "category": "健身房儀器", "equipment": "史密斯機", "filename": "smith_machine_bench.jpg", "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["肩膀", "肘部"], "intensity_reduction_possible": True, "tips": ["槓在肩", "直線下降", "完整動作"]},
    {"id": "025", "nameCN": "胸部飛鳥機", "bodyPart": "胸部", "target_muscle": "胸肌", "difficulty": "中級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "飛鳥機", "filename": "pec_deck.jpg", "require_weight": True, "tempo": "外展2秒 內收1秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["手臂微彎", "控制回放", "充分收縮"]},
    
    # 健身房儀器 - 背部
    {"id": "026", "nameCN": "槓鈴划船", "bodyPart": "背部", "target_muscle": "背肌", "difficulty": "中級", "sets": 4, "reps": 8, "category": "健身房儀器", "equipment": "槓鈴", "filename": "barbell_rows.jpg", "require_weight": True, "tempo": "下放2秒 拉起1秒", "risk_areas": ["肩膀", "腰部"], "intensity_reduction_possible": True, "tips": ["膝蓋微彎", "背部直", "拉至腹"]},
    {"id": "027", "nameCN": "下拉機", "bodyPart": "背部", "target_muscle": "背肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "下拉機", "filename": "lat_pulldown.jpg", "require_weight": True, "tempo": "下放2秒 拉起1秒", "risk_areas": ["肩膀", "肘部"], "intensity_reduction_possible": True, "tips": ["拉至胸", "控制回放", "核心緊縮"]},
    {"id": "028", "nameCN": "拉力機划船", "bodyPart": "背部", "target_muscle": "背肌", "difficulty": "初級", "sets": 4, "reps": 12, "category": "健身房儀器", "equipment": "拉力機", "filename": None, "require_weight": True, "tempo": "下放2秒 拉起1秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["坐直挺胸", "拉至腹", "控制回放"]},
    {"id": "029", "nameCN": "T槓划船", "bodyPart": "背部", "target_muscle": "背肌", "difficulty": "中級", "sets": 4, "reps": 10, "category": "健身房儀器", "equipment": "T槓", "filename": None, "require_weight": True, "tempo": "下放2秒 拉起1秒", "risk_areas": ["腰部", "肩膀"], "intensity_reduction_possible": True, "tips": ["身體穩定", "拉至胸", "控制下降"]},
    {"id": "030", "nameCN": "背闊肌拉力機", "bodyPart": "背部", "target_muscle": "背肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "背闊肌機", "filename": None, "require_weight": True, "tempo": "下放2秒 拉起1秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["坐直", "拉至腹", "控制回放"]},
    
    # 健身房儀器 - 肩膀
    {"id": "031", "nameCN": "槓鈴肩推", "bodyPart": "肩膀", "target_muscle": "肩肌", "difficulty": "中級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "槓鈴", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["肩膀", "肘部"], "intensity_reduction_possible": True, "tips": ["槓在肩", "上推至頂", "控制下降"]},
    {"id": "032", "nameCN": "肩推機", "bodyPart": "肩膀", "target_muscle": "肩肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "肩推機", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["坐直", "推至頂部", "控制下降"]},
    {"id": "033", "nameCN": "側平舉機", "bodyPart": "肩膀", "target_muscle": "肩肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "側平舉機", "filename": None, "require_weight": True, "tempo": "上升2秒 下放2秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["坐直", "抬至肩高", "控制速度"]},
    {"id": "034", "nameCN": "反向夾胸機", "bodyPart": "肩膀", "target_muscle": "肩肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "夾胸機", "filename": None, "require_weight": True, "tempo": "外展2秒 內收1秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["坐直", "手臂向外", "控制回放"]},
    {"id": "035", "nameCN": "前平舉機", "bodyPart": "肩膀", "target_muscle": "肩肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "前平舉機", "filename": None, "require_weight": True, "tempo": "上升2秒 下放2秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["坐直", "推至肩高", "控制速度"]},
    
    # 健身房儀器 - 手臂
    {"id": "036", "nameCN": "繩索下壓", "bodyPart": "手臂", "target_muscle": "三頭肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "拉力機", "filename": None, "require_weight": True, "tempo": "下放1秒 推起1秒", "risk_areas": ["肘部"], "intensity_reduction_possible": True, "tips": ["肘部不動", "完全伸展", "控制回放"]},
    {"id": "037", "nameCN": "拉力機彎舉", "bodyPart": "手臂", "target_muscle": "二頭肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "拉力機", "filename": None, "require_weight": True, "tempo": "上升1秒 下放2秒", "risk_areas": ["肘部"], "intensity_reduction_possible": True, "tips": ["肘部固定", "張力持續", "控制回放"]},
    {"id": "038", "nameCN": "三頭撐體機", "bodyPart": "手臂", "target_muscle": "三頭肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "撐體機", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["肩膀", "肘部"], "intensity_reduction_possible": True, "tips": ["身體向前", "肘部90度", "完整動作"]},
    {"id": "039", "nameCN": "二頭彎舉機", "bodyPart": "手臂", "target_muscle": "二頭肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "彎舉機", "filename": None, "require_weight": True, "tempo": "上升1秒 下放2秒", "risk_areas": ["肘部"], "intensity_reduction_possible": True, "tips": ["坐直", "充分收縮", "控制速度"]},
    {"id": "040", "nameCN": "三頭肌機器", "bodyPart": "手臂", "target_muscle": "三頭肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "三頭機", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["肘部"], "intensity_reduction_possible": True, "tips": ["坐直", "完全伸展", "控制回放"]},
    
    # 健身房儀器 - 腿部
    {"id": "041", "nameCN": "推蹬機", "bodyPart": "腿部", "target_muscle": "腿肌", "difficulty": "初級", "sets": 3, "reps": 15, "category": "健身房儀器", "equipment": "推蹬機", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["膝蓋"], "intensity_reduction_possible": True, "tips": ["腳在機器", "完全伸展", "控制下降"]},
    {"id": "042", "nameCN": "腿部卷舉機", "bodyPart": "腿部", "target_muscle": "腿肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "卷舉機", "filename": None, "require_weight": True, "tempo": "上升1秒 下放2秒", "risk_areas": ["膝蓋"], "intensity_reduction_possible": True, "tips": ["坐直", "卷至胸", "控制回放"]},
    {"id": "043", "nameCN": "腿部伸展機", "bodyPart": "腿部", "target_muscle": "腿肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "伸展機", "filename": None, "require_weight": True, "tempo": "伸展1秒 下放2秒", "risk_areas": ["膝蓋"], "intensity_reduction_possible": True, "tips": ["坐直", "完全伸展", "控制回放"]},
    {"id": "044", "nameCN": "哈克深蹲機", "bodyPart": "腿部", "target_muscle": "腿肌", "difficulty": "中級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "哈克機", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["膝蓋"], "intensity_reduction_possible": True, "tips": ["肩膀靠機", "深蹲至平行", "完整動作"]},
    {"id": "045", "nameCN": "槓鈴深蹲", "bodyPart": "腿部", "target_muscle": "腿肌", "difficulty": "中級", "sets": 4, "reps": 8, "category": "健身房儀器", "equipment": "槓鈴", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["膝蓋", "腰部"], "intensity_reduction_possible": True, "tips": ["槓在肩", "直立姿勢", "深蹲至平行"]},
    
    # 健身房儀器 - 核心
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
    exercises = [e for e in EXERCISES if e["category"] == category and e["bodyPart"] in body_parts and e["bodyPart"] not in excluded_parts]
    filtered, replaced, warnings = filter_exercises_by_injuries(exercises, injured_areas)
    return filtered, replaced, warnings

def get_past_best_weight(records, exercise_name):
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
                st.success(f"✅ 歡迎新用戶 {username}!")
            else:
                st.success(f"👋 歡迎回來 {username}!")
            
            time.sleep(1)
            st.rerun()
        else:
            st.error("❌ 請輸入用戶名稱")
    
    st.divider()
    with st.expander("📌 使用說明"):
        st.write("""
        - ✅ 每個用戶有獨立的訓練紀錄
        - ✅ 數據永久保存(即使關閉瀏覽器)
        - ✅ 多人可以共用同一個裝置
        - ✅ 支援手機橫向/直向使用
        """)

else:
    # ==================== 已登入 ====================
    user_id = st.session_state.user_id
    username = st.session_state.username
    user_data = load_user_data(user_id)
    
    # 初始化狀態
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
    
    # ==================== 頂部導航(取代側邊欄) ====================
    # 訓練中不顯示導航,避免誤觸
    if st.session_state.page != "workout":
        st.markdown(f"### 💪 {username}")
        nav_cols = st.columns(4)
        with nav_cols[0]:
            if st.button("🏠 首頁", use_container_width=True, key="nav_home",
                        type="primary" if st.session_state.page == "home" else "secondary"):
                st.session_state.page = "home"
                st.rerun()
        with nav_cols[1]:
            if st.button("📊 統計", use_container_width=True, key="nav_stats",
                        type="primary" if st.session_state.page == "stats" else "secondary"):
                st.session_state.page = "stats"
                st.rerun()
        with nav_cols[2]:
            if st.button("📈 趨勢", use_container_width=True, key="nav_trend",
                        type="primary" if st.session_state.page == "trend" else "secondary"):
                st.session_state.page = "trend"
                st.rerun()
        with nav_cols[3]:
            if st.button("⚙️ 設置", use_container_width=True, key="nav_settings",
                        type="primary" if st.session_state.page == "settings" else "secondary"):
                st.session_state.page = "settings"
                st.rerun()
        st.divider()
    
    # ==================== 首頁 ====================
    if st.session_state.page == "home":
        st.markdown("#### 🎯 設定訓練計畫")
        
        # 訓練模式 - 垂直排列
        mode = st.radio("訓練模式", ["🏠 徒手/啞鈴", "🏋️ 健身房儀器"], 
                       horizontal=True, key="mode_radio")
        category = "徒手/啞鈴" if "徒手" in mode else "健身房儀器"
        
        # 時長 - 橫排
        duration = st.radio("⏱️ 訓練時長(分鐘)", [15, 30, 45, 60], 
                           horizontal=True, key="duration_radio")
        
        # 傷病部位 - 折疊
        with st.expander("🏥 傷病部位(選填)", expanded=False):
            injured = st.multiselect("選擇受傷部位", INJURY_AREAS, key="injury_select",
                                    label_visibility="collapsed")
        
        st.divider()
        
        # 訓練部位 - 兩欄排列(手機剛好)
        st.markdown("#### 🎯 訓練部位")
        cols = st.columns(2)
        selected_parts = []
        for i, part in enumerate(BODY_PARTS):
            with cols[i % 2]:
                is_checked = st.checkbox(part, value=(part in st.session_state.selected_parts), 
                                        key=f"part_check_{part}")
                if is_checked:
                    selected_parts.append(part)
        
        st.session_state.selected_parts = selected_parts
        
        if selected_parts:
            all_exercises, replaced, warnings = get_exercises(selected_parts, category, injured, [])
            
            if replaced:
                with st.expander(f"📌 動作替換通知 ({len(replaced)}項)", expanded=True):
                    for k, v in replaced.items():
                        st.write(f"❌ {k} → ✅ {v}")
            
            st.divider()
            st.markdown(f"#### 🏆 可用動作 ({len(all_exercises)}個)")
            
            selected_exercises_list = st.session_state.selected_exercises_list
            
            # 按部位分 Tab,減少滑動
            if len(selected_parts) > 1:
                tabs = st.tabs(selected_parts)
                for tab, part in zip(tabs, selected_parts):
                    with tab:
                        part_exercises = [e for e in all_exercises if e['bodyPart'] == part]
                        for ex in part_exercises:
                            with st.container(border=True):
                                if ex["filename"] and ex["filename"] in IMAGES_DATA:
                                    st.image(IMAGES_DATA[ex["filename"]], use_container_width=True)
                                else:
                                    st.info("⏳ 圖片準備中")
                                
                                st.markdown(f"**{ex['nameCN']}**")
                                st.caption(f"{ex['difficulty']} · {ex['sets']}組 × {ex['reps']}次 · {ex['equipment']}")
                                
                                if ex['nameCN'] in warnings:
                                    st.warning("⚠️ 請減輕重量")
                                
                                is_selected = any(s.get("id") == ex["id"] for s in selected_exercises_list)
                                if st.checkbox("✅ 加入訓練", value=is_selected, key=f"select_{ex['id']}"):
                                    if not is_selected:
                                        selected_exercises_list.append(ex)
                                else:
                                    selected_exercises_list = [s for s in selected_exercises_list if s.get("id") != ex["id"]]
            else:
                # 單一部位直接列出
                for ex in all_exercises:
                    with st.container(border=True):
                        if ex["filename"] and ex["filename"] in IMAGES_DATA:
                            st.image(IMAGES_DATA[ex["filename"]], use_container_width=True)
                        else:
                            st.info("⏳ 圖片準備中")
                        
                        st.markdown(f"**{ex['nameCN']}**")
                        st.caption(f"{ex['difficulty']} · {ex['sets']}組 × {ex['reps']}次 · {ex['equipment']}")
                        
                        if ex['nameCN'] in warnings:
                            st.warning("⚠️ 請減輕重量")
                        
                        is_selected = any(s.get("id") == ex["id"] for s in selected_exercises_list)
                        if st.checkbox("✅ 加入訓練", value=is_selected, key=f"select_{ex['id']}"):
                            if not is_selected:
                                selected_exercises_list.append(ex)
                        else:
                            selected_exercises_list = [s for s in selected_exercises_list if s.get("id") != ex["id"]]
            
            st.session_state.selected_exercises_list = selected_exercises_list
            
            # 已選動作清單
            if selected_exercises_list:
                st.divider()
                st.markdown(f"#### 📋 已選動作 ({len(selected_exercises_list)}個)")
                
                for idx, ex in enumerate(selected_exercises_list):
                    col_ex, col_cancel = st.columns([8, 2])
                    with col_ex:
                        st.write(f"**{idx + 1}.** {ex['nameCN']}")
                        st.caption(f"{ex['sets']}組 × {ex['reps']}次")
                    with col_cancel:
                        if st.button("❌", key=f"remove_{ex['id']}", use_container_width=True):
                            st.session_state.selected_exercises_list = [s for s in selected_exercises_list if s.get("id") != ex["id"]]
                            st.rerun()
                
                st.success(f"✅ 共 {len(selected_exercises_list)} 個動作 · 總組數 {sum(e['sets'] for e in selected_exercises_list)}")
                
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
        
        # ============ 休息計時器(全螢幕) ============
        if st.session_state.rest_timer_active and st.session_state.rest_end_time and not st.session_state.rest_skipped:
            remaining = (st.session_state.rest_end_time - datetime.now()).total_seconds()
            if remaining > 0:
                st.markdown(f"""
                <div style='text-align: center; padding: 40px 20px; 
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            border-radius: 16px; margin: 20px 0;'>
                    <h1 style='color: white; margin: 0; font-size: 2rem !important;'>⏱️ 休息中</h1>
                    <h1 style='color: #FFD700; margin: 20px 0; font-size: 5rem !important;'>{int(remaining)}</h1>
                    <p style='color: white; margin: 0; font-size: 1.1rem;'>深呼吸,為下一組做好準備</p>
                </div>
                """, unsafe_allow_html=True)
                
                # 觸發手機振動(剩 3 秒時)
                if int(remaining) <= 3:
                    st.markdown("""
                    <script>
                        if (navigator.vibrate) { navigator.vibrate([200]); }
                    </script>
                    """, unsafe_allow_html=True)
                
                if st.button("⏭️ 跳過休息", use_container_width=True, key="btn_skip_rest", type="primary"):
                    st.session_state.rest_skipped = True
                    st.rerun()
                
                for i in range(int(remaining), 0, -1):
                    time.sleep(1)
                    if st.session_state.rest_skipped:
                        break
                    st.rerun()
                
                st.session_state.rest_timer_active = False
                st.session_state.rest_skipped = False
                st.success("✅ 休息結束!準備下一組")
                st.rerun()
        
        if current_ex_idx < len(exs):
            ex = exs[current_ex_idx]
            
            # 動作標題
            st.markdown(f"### {current_ex_idx + 1}/{len(exs)} · {ex['nameCN']}")
            
            # 圖片(全寬)
            if ex["filename"] and ex["filename"] in IMAGES_DATA:
                st.image(IMAGES_DATA[ex["filename"]], use_container_width=True)
            else:
                st.info("⏳ 圖片準備中")
            
            # 當前組數 - 大字顯示
            st.markdown(f"""
            <div style='text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 16px; border-radius: 12px; margin: 10px 0;'>
                <p style='color: white; margin: 0; font-size: 0.9rem;'>當前組數</p>
                <h1 style='color: #FFD700; margin: 4px 0; font-size: 2.5rem !important;'>
                    {current_set} / {ex['sets']}
                </h1>
                <p style='color: white; margin: 0; font-size: 0.95rem;'>目標 {ex['reps']} 次</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 動作資訊 - 折疊
            with st.expander("📋 動作詳情與技巧", expanded=False):
                st.write(f"**難度**: {ex['difficulty']}")
                st.write(f"**部位**: {ex['bodyPart']} · {ex['target_muscle']}")
                st.write(f"**器材**: {ex['equipment']}")
                st.write(f"**節奏**: {ex['tempo']}")
                st.write("**執行技巧**:")
                for tip in ex["tips"]:
                    st.write(f"✅ {tip}")
            
            st.divider()
            
            # ============ 訓練數據輸入(垂直排列) ============
            st.markdown("#### 📊 這一組的數據")
            
            records = get_records(user_id) or []
            
            # 次數
            past_best_reps = get_past_best_reps(records, ex['nameCN'])
            actual_reps = st.number_input(
                f"💪 實際完成次數" + (f" (歷史最高: {past_best_reps})" if past_best_reps else ""),
                min_value=1,
                max_value=ex['reps'] + 5,
                value=ex['reps'],
                key=f"reps_{current_ex_idx}_{current_set}"
            )
            if past_best_reps and actual_reps > past_best_reps:
                st.toast("🔥 突破紀錄了!", icon="🎉")
            
            # 重量(僅需要時顯示)
            weight = 0
            if ex['require_weight']:
                exercise_key = f"{ex['id']}"
                default_weight = st.session_state.exercise_weights.get(exercise_key, 0.0)
                past_best_weight = get_past_best_weight(records, ex['nameCN'])
                
                weight = st.number_input(
                    f"🏋️ 重量 kg" + (f" (歷史最高: {past_best_weight})" if past_best_weight else ""),
                    min_value=0.0,
                    step=0.5,
                    value=default_weight,
                    key=f"weight_{current_ex_idx}_{current_set}"
                )
                
                st.session_state.exercise_weights[exercise_key] = weight
                
                if past_best_weight and weight > past_best_weight:
                    st.toast("🔥 突破紀錄了!", icon="🎉")
            
            # 疲勞度
            fatigue = st.slider(
                "😓 疲勞度 (1=輕鬆 / 10=力竭)",
                1, 10, 5,
                key=f"fatigue_{current_ex_idx}_{current_set}"
            )
            
            st.divider()
            
            # ============ 控制按鈕(主按鈕全寬,次要折疊) ============
            if st.button("✅ 完成這組", use_container_width=True, type="primary", key="btn_done"):
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
                
                # 完成時手機振動
                st.markdown("""
                <script>
                    if (navigator.vibrate) { navigator.vibrate([100, 50, 100]); }
                </script>
                """, unsafe_allow_html=True)
                
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
            
            # 次要按鈕折疊
            with st.expander("⚙️ 其他操作"):
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("⏭️ 跳過動作", use_container_width=True, key="btn_skip"):
                        st.session_state.current_ex_idx += 1
                        st.session_state.current_set = 1
                        st.rerun()
                with col2:
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
            # 訓練完成
            st.success("🎉 訓練完成!")
            st.divider()
            
            dur = int((datetime.now() - st.session_state.workout["start"]).total_seconds() / 60)
            total_volume = sum(log.get("volume", 0) for log in st.session_state.workout_log.values())
            
            # 兩欄 metric 在手機上剛好
            col1, col2 = st.columns(2)
            col1.metric("動作數", len(exs))
            col2.metric("組數", sum(e["sets"] for e in exs))
            col3, col4 = st.columns(2)
            col3.metric("時長", f"{dur}分")
            col4.metric("總Volume", f"{int(total_volume)}")
            
            st.divider()
            
            if st.button("📊 查看統計", use_container_width=True, type="primary", key="view_stats_btn"):
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
        st.markdown(f"#### 📊 訓練統計")
        records = get_records(user_id)
        
        if records:
            df = pd.DataFrame(records)
            
            # 兩欄 metric 適合手機
            c1, c2 = st.columns(2)
            c1.metric("訓練次數", len(records))
            c2.metric("總組數", int(df['組數'].sum()))
            c3, c4 = st.columns(2)
            c3.metric("總時長", f"{int(df['時長(分)'].sum())}分")
            c4.metric("總熱量", int(df['熱量'].sum()))
            
            st.metric("累計 Volume", f"{int(df['總Volume'].sum())}")
            
            st.divider()
            st.markdown("#### 📋 訓練紀錄")
            
            # 卡片式顯示(取代 dataframe)
            for idx, record in enumerate(reversed(records[-20:])):
                with st.container(border=True):
                    st.write(f"📅 **{record['日期']}**")
                    rcol1, rcol2, rcol3 = st.columns(3)
                    rcol1.metric("動作", record['動作數'])
                    rcol2.metric("組數", record['組數'])
                    rcol3.metric("Volume", record['總Volume'])
                    st.caption(f"⏱️ {record['時長(分)']}分鐘 · 🔥 {record['熱量']}卡")
        else:
            st.info("暫無訓練記錄,先去完成第一次訓練吧!")
    
    # ==================== 趨勢 ====================
    elif st.session_state.page == "trend":
        st.markdown(f"#### 📈 訓練趨勢")
        records = get_records(user_id)
        
        if records:
            df = pd.DataFrame(records)
            df['日期'] = pd.to_datetime(df['日期'])
            df_sorted = df.sort_values('日期')
            
            tab_week, tab_month = st.tabs(["📅 週趨勢", "📆 月趨勢"])
            
            with tab_week:
                df_sorted['週'] = df_sorted['日期'].dt.to_period('W')
                weekly = df_sorted.groupby('週').agg({'總Volume': 'sum'}).reset_index()
                weekly['週'] = weekly['週'].astype(str)
                st.line_chart(weekly.set_index('週')['總Volume'], height=300)
            
            with tab_month:
                df_sorted['月'] = df_sorted['日期'].dt.to_period('M')
                monthly = df_sorted.groupby('月').agg({'總Volume': 'sum'}).reset_index()
                monthly['月'] = monthly['月'].astype(str)
                st.bar_chart(monthly.set_index('月')['總Volume'], height=300)
        else:
            st.info("暫無訓練數據")
    
    # ==================== 設置 ====================
    elif st.session_state.page == "settings":
        st.markdown("#### ⚙️ 個人設置")
        
        name = st.text_input("姓名", user_data.get("user_info", {}).get("name", ""), key="user_name_input")
        age = st.slider("年齡", 15, 100, user_data.get("user_info", {}).get("age", 25), key="user_age_slider")
        
        if st.button("💾 保存設置", use_container_width=True, type="primary", key="save_settings_btn"):
            update_user_info(user_id, {"name": name, "age": age})
            st.success("✅ 已保存")
        
        st.divider()
        
        if st.button("🚪 登出", use_container_width=True, key="logout_btn"):
            del st.session_state.user_id
            del st.session_state.username
            st.rerun()
        
        st.divider()
        
        with st.expander("ℹ️ 版本資訊"):
            st.success("""
            ✅ SmartFit v19 - 手機優化版
            
            🎯 手機優化:
            ✅ 單欄垂直佈局
            ✅ 大按鈕設計(min 3rem)
            ✅ 頂部 Tab 導航(取代側邊欄)
            ✅ 動作分頁顯示
            ✅ 全螢幕休息計時器
            ✅ 完成組數手機振動回饋
            ✅ 卡片式統計顯示
            ✅ 折疊式詳情(節省畫面)
            
            🎯 核心功能:
            ✅ 訓練完成自動跳轉統計頁
            ✅ 重量記憶(同動作共用)
            ✅ 多用戶獨立記錄
            ✅ 50個動作完整資料庫
            """)
