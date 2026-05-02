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
        padding-top: 0.5rem !important;
        padding-bottom: 6rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        max-width: 100% !important;
    }
    
    /* 按鈕加大,方便手指點擊 */
    .stButton > button {
        min-height: 2.8rem !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
    }
    
    /* number_input 字體加大 */
    .stNumberInput input {
        font-size: 1.4rem !important;
        text-align: center !important;
        height: 3rem !important;
        font-weight: 600 !important;
    }
    
    /* 圖片限制(訓練中縮小) */
    .stImage img {
        max-height: 220px !important;
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
    
    /* 標題縮小 */
    h1 { font-size: 1.6rem !important; }
    h2 { font-size: 1.3rem !important; }
    h3 { font-size: 1.1rem !important; }
    
    /* ============ 全螢幕休息倒數覆蓋層 ============ */
    .rest-overlay {
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        z-index: 99999;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 20px;
    }
    
    .rest-title {
        color: white;
        font-size: 1.5rem;
        margin: 0 0 20px 0;
        font-weight: 600;
    }
    
    .rest-circle {
        width: 280px;
        height: 280px;
        border-radius: 50%;
        background: rgba(255,255,255,0.1);
        border: 8px solid rgba(255,255,255,0.3);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin: 20px 0;
        box-shadow: 0 0 40px rgba(255,215,0,0.3);
    }
    
    .rest-number {
        color: #FFD700;
        font-size: 6rem;
        font-weight: 800;
        line-height: 1;
        margin: 0;
    }
    
    .rest-unit {
        color: white;
        font-size: 1.2rem;
        margin-top: 8px;
    }
    
    .rest-next {
        color: white;
        background: rgba(0,0,0,0.25);
        padding: 12px 20px;
        border-radius: 12px;
        margin: 16px 0;
        text-align: center;
        max-width: 90%;
    }
    
    /* 黏性底部按鈕(訓練中) */
    .sticky-bottom {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        padding: 12px;
        box-shadow: 0 -4px 12px rgba(0,0,0,0.1);
        z-index: 100;
    }
    
    /* 緊湊資訊條 */
    .info-bar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px 14px;
        border-radius: 10px;
        margin: 6px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* 暗色模式適配 */
    @media (prefers-color-scheme: dark) {
        .sticky-bottom {
            background: #0e1117;
        }
    }
</style>
""", unsafe_allow_html=True)

BODY_PARTS = ["胸部", "背部", "肩膀", "手臂", "腿部", "核心"]
INJURY_AREAS = ["肩膀", "肘部", "腕部", "腰部", "膝蓋", "踝部", "頸部", "下背部"]

# ==================== 50個動作 ====================
EXERCISES = [
    {"id": "001", "nameCN": "俯臥撑", "bodyPart": "胸部", "target_muscle": "胸肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "徒手/啞鈴", "equipment": "無", "filename": "push_ups.jpg", "require_weight": False, "tempo": "下放2秒 撐起1秒", "risk_areas": ["肩膀", "肘部", "腕部"], "intensity_reduction_possible": True, "tips": ["保持身體直線", "降低至胸部", "推回起始位置"]},
    {"id": "002", "nameCN": "寬距俯臥撑", "bodyPart": "胸部", "target_muscle": "胸肌", "difficulty": "初級", "sets": 3, "reps": 10, "category": "徒手/啞鈴", "equipment": "無", "filename": "wide_push_ups.jpg", "require_weight": False, "tempo": "下放2秒 撐起1秒", "risk_areas": ["肩膀", "肘部", "腕部"], "intensity_reduction_possible": True, "tips": ["雙手寬距", "保持直線", "完整範圍"]},
    {"id": "003", "nameCN": "菱形俯臥撑", "bodyPart": "胸部", "target_muscle": "胸肌", "difficulty": "中級", "sets": 3, "reps": 8, "category": "徒手/啞鈴", "equipment": "無", "filename": "diamond_push_ups.jpg", "require_weight": False, "tempo": "下放2秒 撐起1秒", "risk_areas": ["肘部", "腕部", "肩膀"], "intensity_reduction_possible": True, "tips": ["雙手在胸下", "肘部靠近", "完全伸展"]},
    {"id": "004", "nameCN": "下斜俯臥撑", "bodyPart": "胸部", "target_muscle": "胸肌", "difficulty": "中級", "sets": 3, "reps": 10, "category": "徒手/啞鈴", "equipment": "無", "filename": "decline_push_ups.jpg", "require_weight": False, "tempo": "下放2秒 撐起1秒", "risk_areas": ["肩膀", "肘部", "腕部"], "intensity_reduction_possible": True, "tips": ["雙腳放高", "身體直線", "完整動作"]},
    {"id": "005", "nameCN": "箭手俯臥撑", "bodyPart": "胸部", "target_muscle": "胸肌", "difficulty": "高級", "sets": 3, "reps": 6, "category": "徒手/啞鈴", "equipment": "無", "filename": "archer_push_ups.jpg", "require_weight": False, "tempo": "下放2秒 撐起1秒", "risk_areas": ["肩膀", "肘部", "腕部"], "intensity_reduction_possible": True, "tips": ["一側彎曲", "一側伸直", "平衡訓練"]},
    {"id": "006", "nameCN": "引體向上", "bodyPart": "背部", "target_muscle": "背肌", "difficulty": "中級", "sets": 3, "reps": 8, "category": "徒手/啞鈴", "equipment": "無", "filename": "pull_ups.jpg", "require_weight": False, "tempo": "下放2秒 撐起1秒", "risk_areas": ["肩膀", "肘部"], "intensity_reduction_possible": False, "tips": ["握距寬", "下巴超杆", "控制下降"]},
    {"id": "007", "nameCN": "窄握引體向上", "bodyPart": "背部", "target_muscle": "背肌", "difficulty": "中級", "sets": 3, "reps": 8, "category": "徒手/啞鈴", "equipment": "無", "filename": "chin_ups.jpg", "require_weight": False, "tempo": "下放2秒 撐起1秒", "risk_areas": ["肘部", "肩膀"], "intensity_reduction_possible": False, "tips": ["掌心向內", "肘部靠近", "平順動作"]},
    {"id": "008", "nameCN": "反向划船", "bodyPart": "背部", "target_muscle": "背肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "徒手/啞鈴", "equipment": "無", "filename": "reverse_rows.jpg", "require_weight": False, "tempo": "下放2秒 拉起1秒", "risk_areas": ["肩膀", "腕部"], "intensity_reduction_possible": True, "tips": ["身體直線", "拉至胸部", "控制下降"]},
    {"id": "009", "nameCN": "啞鈴划船", "bodyPart": "背部", "target_muscle": "背肌", "difficulty": "中級", "sets": 4, "reps": 10, "category": "徒手/啞鈴", "equipment": "啞鈴", "filename": "dumbbell_rows.jpg", "require_weight": True, "tempo": "下放2秒 拉起1秒", "risk_areas": ["肩膀", "腰部"], "intensity_reduction_possible": True, "tips": ["膝蓋跪", "核心穩定", "拉至腰"]},
    {"id": "010", "nameCN": "超人式", "bodyPart": "背部", "target_muscle": "背肌", "difficulty": "初級", "sets": 3, "reps": 30, "category": "徒手/啞鈴", "equipment": "無", "filename": "superman_hold.jpg", "require_weight": False, "tempo": "靜止2秒", "risk_areas": ["下背部", "腰部"], "intensity_reduction_possible": False, "tips": ["手臂前伸", "腿後伸", "胸部離地"]},
    {"id": "051", "nameCN": "啞鈴肩推", "bodyPart": "肩膀", "target_muscle": "肩肌", "difficulty": "中級", "sets": 3, "reps": 10, "category": "徒手/啞鈴", "equipment": "啞鈴", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["肩膀", "肘部"], "intensity_reduction_possible": True, "tips": ["挺胸", "肩膀穩定", "完整範圍"]},
    {"id": "052", "nameCN": "啞鈴側平舉", "bodyPart": "肩膀", "target_muscle": "肩肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "徒手/啞鈴", "equipment": "啞鈴", "filename": None, "require_weight": True, "tempo": "上升2秒 下放2秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["挺胸", "肘部微彎", "控制速度"]},
    {"id": "053", "nameCN": "啞鈴前平舉", "bodyPart": "肩膀", "target_muscle": "肩肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "徒手/啞鈴", "equipment": "啞鈴", "filename": None, "require_weight": True, "tempo": "上升1秒 下放2秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["肘部微彎", "緩慢控制", "完整動作"]},
    {"id": "054", "nameCN": "啞鈴後舉飛鳥", "bodyPart": "肩膀", "target_muscle": "肩肌", "difficulty": "中級", "sets": 3, "reps": 12, "category": "徒手/啞鈴", "equipment": "啞鈴", "filename": None, "require_weight": True, "tempo": "上升2秒 下放2秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["身體前傾", "肘部微彎", "集中收縮"]},
    {"id": "055", "nameCN": "肩部聳動", "bodyPart": "肩膀", "target_muscle": "肩肌", "difficulty": "初級", "sets": 3, "reps": 15, "category": "徒手/啞鈴", "equipment": "啞鈴", "filename": None, "require_weight": True, "tempo": "上升1秒 下放1秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["肩膀聳起", "頂部停留", "控制下降"]},
    {"id": "056", "nameCN": "啞鈴彎舉", "bodyPart": "手臂", "target_muscle": "二頭肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "徒手/啞鈴", "equipment": "啞鈴", "filename": None, "require_weight": True, "tempo": "上升1秒 下放2秒", "risk_areas": ["肘部"], "intensity_reduction_possible": True, "tips": ["肘部固定", "完全收縮", "控制速度"]},
    {"id": "057", "nameCN": "錘式彎舉", "bodyPart": "手臂", "target_muscle": "二頭肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "徒手/啞鈴", "equipment": "啞鈴", "filename": None, "require_weight": True, "tempo": "上升1秒 下放2秒", "risk_areas": ["肘部"], "intensity_reduction_possible": True, "tips": ["握把中立", "肘部穩定", "完整範圍"]},
    {"id": "058", "nameCN": "啞鈴三頭伸展", "bodyPart": "手臂", "target_muscle": "三頭肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "徒手/啞鈴", "equipment": "啞鈴", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["肘部", "肩膀"], "intensity_reduction_possible": True, "tips": ["肘部靠近", "完全伸展", "控制速度"]},
    {"id": "059", "nameCN": "窄距俯臥撑(三頭)", "bodyPart": "手臂", "target_muscle": "三頭肌", "difficulty": "中級", "sets": 3, "reps": 10, "category": "徒手/啞鈴", "equipment": "無", "filename": None, "require_weight": False, "tempo": "下放2秒 推起1秒", "risk_areas": ["肘部", "腕部"], "intensity_reduction_possible": True, "tips": ["雙手靠近", "肘部貼身", "完整動作"]},
    {"id": "060", "nameCN": "啞鈴過頭伸展", "bodyPart": "手臂", "target_muscle": "三頭肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "徒手/啞鈴", "equipment": "啞鈴", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["肘部", "肩膀"], "intensity_reduction_possible": True, "tips": ["單手或雙手", "肘部固定", "完全伸展"]},
    {"id": "011", "nameCN": "深蹲", "bodyPart": "腿部", "target_muscle": "腿肌", "difficulty": "初級", "sets": 3, "reps": 15, "category": "徒手/啞鈴", "equipment": "無", "filename": "squats.jpg", "require_weight": False, "tempo": "下放2秒 撐起1秒", "risk_areas": ["膝蓋", "踝部", "下背部"], "intensity_reduction_possible": True, "tips": ["挺胸", "臀部後坐", "腳跟推起"]},
    {"id": "012", "nameCN": "跳躍深蹲", "bodyPart": "腿部", "target_muscle": "腿肌", "difficulty": "中級", "sets": 3, "reps": 12, "category": "徒手/啞鈴", "equipment": "無", "filename": "jump_squats.jpg", "require_weight": False, "tempo": "爆發式", "risk_areas": ["膝蓋", "踝部"], "intensity_reduction_possible": False, "tips": ["全力跳", "軟著陸", "快速起身"]},
    {"id": "013", "nameCN": "弓步", "bodyPart": "腿部", "target_muscle": "腿肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "徒手/啞鈴", "equipment": "無", "filename": "lunges.jpg", "require_weight": False, "tempo": "下放2秒 撐起1秒", "risk_areas": ["膝蓋", "踝部"], "intensity_reduction_possible": True, "tips": ["前腳90度", "後腳接地", "保持直立"]},
    {"id": "014", "nameCN": "啞鈴深蹲", "bodyPart": "腿部", "target_muscle": "腿肌", "difficulty": "中級", "sets": 4, "reps": 10, "category": "徒手/啞鈴", "equipment": "啞鈴", "filename": "dumbbell_squats.jpg", "require_weight": True, "tempo": "下放2秒 撐起1秒", "risk_areas": ["膝蓋", "腰部"], "intensity_reduction_possible": True, "tips": ["拿著啞鈴", "挺胸下蹲", "腳跟推起"]},
    {"id": "015", "nameCN": "提踵", "bodyPart": "腿部", "target_muscle": "腿肌", "difficulty": "初級", "sets": 3, "reps": 20, "category": "徒手/啞鈴", "equipment": "無", "filename": "calf_raises.jpg", "require_weight": False, "tempo": "上升1秒 下放1秒", "risk_areas": ["踝部"], "intensity_reduction_possible": True, "tips": ["站直", "提起腳跟", "控制下降"]},
    {"id": "016", "nameCN": "棒式", "bodyPart": "核心", "target_muscle": "核心", "difficulty": "初級", "sets": 3, "reps": 30, "category": "徒手/啞鈴", "equipment": "無", "filename": "plank.jpg", "require_weight": False, "tempo": "靜止", "risk_areas": ["腕部", "肩膀"], "intensity_reduction_possible": True, "tips": ["身體直線", "核心緊縮", "臀部不下沉"]},
    {"id": "017", "nameCN": "側棒式", "bodyPart": "核心", "target_muscle": "核心", "difficulty": "初級", "sets": 3, "reps": 20, "category": "徒手/啞鈴", "equipment": "無", "filename": "side_plank.jpg", "require_weight": False, "tempo": "靜止", "risk_areas": ["肩膀", "腕部"], "intensity_reduction_possible": True, "tips": ["身體直線", "核心收緊", "臀部不下沉"]},
    {"id": "018", "nameCN": "仰臥起坐", "bodyPart": "核心", "target_muscle": "核心", "difficulty": "初級", "sets": 3, "reps": 15, "category": "徒手/啞鈴", "equipment": "無", "filename": "sit_ups.jpg", "require_weight": False, "tempo": "上起1秒 下放1秒", "risk_areas": ["頸部", "下背部"], "intensity_reduction_possible": True, "tips": ["膝蓋彎曲", "不拉脖子", "胸部向膝"]},
    {"id": "019", "nameCN": "爬山者", "bodyPart": "核心", "target_muscle": "核心", "difficulty": "中級", "sets": 3, "reps": 20, "category": "徒手/啞鈴", "equipment": "無", "filename": "mountain_climbers.jpg", "require_weight": False, "tempo": "快速", "risk_areas": ["肩膀", "腕部"], "intensity_reduction_possible": True, "tips": ["快速交替", "保持俯臥撑", "核心緊縮"]},
    {"id": "020", "nameCN": "抬腿", "bodyPart": "核心", "target_muscle": "核心", "difficulty": "初級", "sets": 3, "reps": 12, "category": "徒手/啞鈴", "equipment": "無", "filename": "leg_raises.jpg", "require_weight": False, "tempo": "上升1秒 下放2秒", "risk_areas": ["下背部"], "intensity_reduction_possible": True, "tips": ["背部貼地", "腿部直", "控制速度"]},
    {"id": "021", "nameCN": "槓鈴臥推", "bodyPart": "胸部", "target_muscle": "胸肌", "difficulty": "中級", "sets": 4, "reps": 8, "category": "健身房儀器", "equipment": "槓鈴", "filename": "barbell_bench.jpg", "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["肩膀", "肘部"], "intensity_reduction_possible": True, "tips": ["背貼板", "肩膀穩定", "平順動作"]},
    {"id": "022", "nameCN": "胸部推蹬機", "bodyPart": "胸部", "target_muscle": "胸肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "推蹬機", "filename": "chest_machine.jpg", "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["肩膀", "肘部"], "intensity_reduction_possible": True, "tips": ["坐直對齊", "完全推出", "控制回放"]},
    {"id": "023", "nameCN": "拉力機夾胸", "bodyPart": "胸部", "target_muscle": "胸肌", "difficulty": "中級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "拉力機", "filename": "cable_flyes.jpg", "require_weight": True, "tempo": "外展2秒 內收1秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["手臂微彎", "控制回放", "集中收縮"]},
    {"id": "024", "nameCN": "史密斯機臥推", "bodyPart": "胸部", "target_muscle": "胸肌", "difficulty": "初級", "sets": 4, "reps": 12, "category": "健身房儀器", "equipment": "史密斯機", "filename": "smith_machine_bench.jpg", "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["肩膀", "肘部"], "intensity_reduction_possible": True, "tips": ["槓在肩", "直線下降", "完整動作"]},
    {"id": "025", "nameCN": "胸部飛鳥機", "bodyPart": "胸部", "target_muscle": "胸肌", "difficulty": "中級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "飛鳥機", "filename": "pec_deck.jpg", "require_weight": True, "tempo": "外展2秒 內收1秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["手臂微彎", "控制回放", "充分收縮"]},
    {"id": "026", "nameCN": "槓鈴划船", "bodyPart": "背部", "target_muscle": "背肌", "difficulty": "中級", "sets": 4, "reps": 8, "category": "健身房儀器", "equipment": "槓鈴", "filename": "barbell_rows.jpg", "require_weight": True, "tempo": "下放2秒 拉起1秒", "risk_areas": ["肩膀", "腰部"], "intensity_reduction_possible": True, "tips": ["膝蓋微彎", "背部直", "拉至腹"]},
    {"id": "027", "nameCN": "下拉機", "bodyPart": "背部", "target_muscle": "背肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "下拉機", "filename": "lat_pulldown.jpg", "require_weight": True, "tempo": "下放2秒 拉起1秒", "risk_areas": ["肩膀", "肘部"], "intensity_reduction_possible": True, "tips": ["拉至胸", "控制回放", "核心緊縮"]},
    {"id": "028", "nameCN": "拉力機划船", "bodyPart": "背部", "target_muscle": "背肌", "difficulty": "初級", "sets": 4, "reps": 12, "category": "健身房儀器", "equipment": "拉力機", "filename": None, "require_weight": True, "tempo": "下放2秒 拉起1秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["坐直挺胸", "拉至腹", "控制回放"]},
    {"id": "029", "nameCN": "T槓划船", "bodyPart": "背部", "target_muscle": "背肌", "difficulty": "中級", "sets": 4, "reps": 10, "category": "健身房儀器", "equipment": "T槓", "filename": None, "require_weight": True, "tempo": "下放2秒 拉起1秒", "risk_areas": ["腰部", "肩膀"], "intensity_reduction_possible": True, "tips": ["身體穩定", "拉至胸", "控制下降"]},
    {"id": "030", "nameCN": "背闊肌拉力機", "bodyPart": "背部", "target_muscle": "背肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "背闊肌機", "filename": None, "require_weight": True, "tempo": "下放2秒 拉起1秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["坐直", "拉至腹", "控制回放"]},
    {"id": "031", "nameCN": "槓鈴肩推", "bodyPart": "肩膀", "target_muscle": "肩肌", "difficulty": "中級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "槓鈴", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["肩膀", "肘部"], "intensity_reduction_possible": True, "tips": ["槓在肩", "上推至頂", "控制下降"]},
    {"id": "032", "nameCN": "肩推機", "bodyPart": "肩膀", "target_muscle": "肩肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "肩推機", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["坐直", "推至頂部", "控制下降"]},
    {"id": "033", "nameCN": "側平舉機", "bodyPart": "肩膀", "target_muscle": "肩肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "側平舉機", "filename": None, "require_weight": True, "tempo": "上升2秒 下放2秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["坐直", "抬至肩高", "控制速度"]},
    {"id": "034", "nameCN": "反向夾胸機", "bodyPart": "肩膀", "target_muscle": "肩肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "夾胸機", "filename": None, "require_weight": True, "tempo": "外展2秒 內收1秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["坐直", "手臂向外", "控制回放"]},
    {"id": "035", "nameCN": "前平舉機", "bodyPart": "肩膀", "target_muscle": "肩肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "前平舉機", "filename": None, "require_weight": True, "tempo": "上升2秒 下放2秒", "risk_areas": ["肩膀"], "intensity_reduction_possible": True, "tips": ["坐直", "推至肩高", "控制速度"]},
    {"id": "036", "nameCN": "繩索下壓", "bodyPart": "手臂", "target_muscle": "三頭肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "拉力機", "filename": None, "require_weight": True, "tempo": "下放1秒 推起1秒", "risk_areas": ["肘部"], "intensity_reduction_possible": True, "tips": ["肘部不動", "完全伸展", "控制回放"]},
    {"id": "037", "nameCN": "拉力機彎舉", "bodyPart": "手臂", "target_muscle": "二頭肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "拉力機", "filename": None, "require_weight": True, "tempo": "上升1秒 下放2秒", "risk_areas": ["肘部"], "intensity_reduction_possible": True, "tips": ["肘部固定", "張力持續", "控制回放"]},
    {"id": "038", "nameCN": "三頭撐體機", "bodyPart": "手臂", "target_muscle": "三頭肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "撐體機", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["肩膀", "肘部"], "intensity_reduction_possible": True, "tips": ["身體向前", "肘部90度", "完整動作"]},
    {"id": "039", "nameCN": "二頭彎舉機", "bodyPart": "手臂", "target_muscle": "二頭肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "彎舉機", "filename": None, "require_weight": True, "tempo": "上升1秒 下放2秒", "risk_areas": ["肘部"], "intensity_reduction_possible": True, "tips": ["坐直", "充分收縮", "控制速度"]},
    {"id": "040", "nameCN": "三頭肌機器", "bodyPart": "手臂", "target_muscle": "三頭肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "三頭機", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["肘部"], "intensity_reduction_possible": True, "tips": ["坐直", "完全伸展", "控制回放"]},
    {"id": "041", "nameCN": "推蹬機", "bodyPart": "腿部", "target_muscle": "腿肌", "difficulty": "初級", "sets": 3, "reps": 15, "category": "健身房儀器", "equipment": "推蹬機", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["膝蓋"], "intensity_reduction_possible": True, "tips": ["腳在機器", "完全伸展", "控制下降"]},
    {"id": "042", "nameCN": "腿部卷舉機", "bodyPart": "腿部", "target_muscle": "腿肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "卷舉機", "filename": None, "require_weight": True, "tempo": "上升1秒 下放2秒", "risk_areas": ["膝蓋"], "intensity_reduction_possible": True, "tips": ["坐直", "卷至胸", "控制回放"]},
    {"id": "043", "nameCN": "腿部伸展機", "bodyPart": "腿部", "target_muscle": "腿肌", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "伸展機", "filename": None, "require_weight": True, "tempo": "伸展1秒 下放2秒", "risk_areas": ["膝蓋"], "intensity_reduction_possible": True, "tips": ["坐直", "完全伸展", "控制回放"]},
    {"id": "044", "nameCN": "哈克深蹲機", "bodyPart": "腿部", "target_muscle": "腿肌", "difficulty": "中級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "哈克機", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["膝蓋"], "intensity_reduction_possible": True, "tips": ["肩膀靠機", "深蹲至平行", "完整動作"]},
    {"id": "045", "nameCN": "槓鈴深蹲", "bodyPart": "腿部", "target_muscle": "腿肌", "difficulty": "中級", "sets": 4, "reps": 8, "category": "健身房儀器", "equipment": "槓鈴", "filename": None, "require_weight": True, "tempo": "下放2秒 推起1秒", "risk_areas": ["膝蓋", "腰部"], "intensity_reduction_possible": True, "tips": ["槓在肩", "直立姿勢", "深蹲至平行"]},
    {"id": "046", "nameCN": "拉力卷腹", "bodyPart": "核心", "target_muscle": "核心", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "拉力機", "filename": None, "require_weight": True, "tempo": "下放2秒 收起1秒", "risk_areas": ["下背部"], "intensity_reduction_possible": True, "tips": ["膝蓋彎", "卷至膝", "控制回放"]},
    {"id": "047", "nameCN": "腹肌卷腹機", "bodyPart": "核心", "target_muscle": "核心", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "卷腹機", "filename": None, "require_weight": True, "tempo": "收起1秒 下放2秒", "risk_areas": ["下背部", "頸部"], "intensity_reduction_possible": True, "tips": ["坐直對齊", "卷起完整", "控制回放"]},
    {"id": "048", "nameCN": "滑輪卷腹", "bodyPart": "核心", "target_muscle": "核心", "difficulty": "中級", "sets": 3, "reps": 10, "category": "健身房儀器", "equipment": "滑輪", "filename": None, "require_weight": False, "tempo": "向前滾2秒 回收1秒", "risk_areas": ["腕部", "肩膀"], "intensity_reduction_possible": False, "tips": ["膝蓋跪", "向前滾", "回收縮腹"]},
    {"id": "049", "nameCN": "旋轉腹肌機", "bodyPart": "核心", "target_muscle": "核心", "difficulty": "初級", "sets": 3, "reps": 12, "category": "健身房儀器", "equipment": "旋轉機", "filename": None, "require_weight": True, "tempo": "旋轉1秒 回中1秒", "risk_areas": ["腰部"], "intensity_reduction_possible": True, "tips": ["坐直", "緩慢旋轉", "控制速度"]},
    {"id": "050", "nameCN": "懸掛抬腿", "bodyPart": "核心", "target_muscle": "核心", "difficulty": "中級", "sets": 3, "reps": 10, "category": "健身房儀器", "equipment": "單槓", "filename": None, "require_weight": False, "tempo": "上升2秒 下放2秒", "risk_areas": ["肩膀", "肘部"], "intensity_reduction_possible": False, "tips": ["握把穩定", "腿抬至水平", "控制下降"]},
]

REST_TIMES = {"初級": 60, "中級": 90, "高級": 120}
WEIGHT_STEPS = [2.5, 5, 10]  # 快速重量調整步進
REPS_STEPS = [1, 5]  # 快速次數調整步進

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

def get_last_set_data(workout_log, exercise_name, current_set):
    """取得本次訓練的上一組數據"""
    if current_set <= 1:
        return None
    for key, log in workout_log.items():
        if log.get("exercise") == exercise_name and log.get("set") == current_set - 1:
            return log
    return None

# ==================== 自動登入(URL 參數) ====================
# 檢查 URL 是否帶有 user 參數,有的話自動登入
query_params = st.query_params
if "user" in query_params and "user_id" not in st.session_state:
    auto_username = query_params["user"]
    if auto_username.strip():
        try:
            auto_user_id, _ = create_user(auto_username)
            st.session_state.user_id = auto_user_id
            st.session_state.username = auto_username
            st.session_state.page = "home"
            st.session_state.selected_parts = []
        except Exception as e:
            st.error(f"自動登入失敗: {e}")

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
            
            # 設定 URL 參數,下次自動登入
            st.query_params["user"] = username
            
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
        - ✅ 數據永久保存
        - ✅ 多人可以共用同一個裝置
        - ✅ 手機優化界面
        - ✅ **加到主畫面**:登入後將網址加到手機主畫面,下次點開自動登入!
        """)

else:
    # ==================== 已登入 ====================
    user_id = st.session_state.user_id
    username = st.session_state.username
    user_data = load_user_data(user_id)
    
    # ===== 自動捲動到頂部(如果有標記) =====
    if st.session_state.get("scroll_to_top", False):
        st.session_state.scroll_to_top = False  # 用過就清除
        # 使用 components.html 確保 JS 能執行(突破 Streamlit iframe 限制)
        from streamlit.components.v1 import html as components_html
        components_html("""
        <script>
            // 多種方式嘗試捲動,確保在不同環境都能運作
            function scrollToTop() {
                // 方法 1: 透過 parent window
                try {
                    window.parent.document.querySelector('section.main').scrollTo({top: 0, behavior: 'smooth'});
                } catch(e) {}
                
                try {
                    window.parent.document.querySelector('[data-testid="stAppViewContainer"]').scrollTo({top: 0, behavior: 'smooth'});
                } catch(e) {}
                
                try {
                    window.parent.document.querySelector('.main .block-container').scrollIntoView({behavior: 'smooth', block: 'start'});
                } catch(e) {}
                
                try {
                    window.parent.scrollTo({top: 0, behavior: 'smooth'});
                } catch(e) {}
                
                // 方法 2: 直接捲動 window
                window.scrollTo({top: 0, behavior: 'smooth'});
                
                // 方法 3: 捲動 document.documentElement
                try {
                    window.parent.document.documentElement.scrollTop = 0;
                    window.parent.document.body.scrollTop = 0;
                } catch(e) {}
            }
            
            // 立即執行 + 延遲執行(確保元素已渲染)
            scrollToTop();
            setTimeout(scrollToTop, 100);
            setTimeout(scrollToTop, 300);
            setTimeout(scrollToTop, 600);
        </script>
        """, height=0)
    
    # 初始化狀態
    for key, default in [
        ("selected_parts", []),
        ("selected_exercises_list", []),
        ("page", "home"),
        ("workout", None),
        ("exercise_weights", {}),
        ("exercise_reps", {}),  # 重量+次數記憶
        ("rest_timer_active", False),
        ("rest_end_time", None),
        ("rest_skipped", False),
        ("rest_total_seconds", 60),  # 用於進度環計算
    ]:
        if key not in st.session_state:
            st.session_state[key] = default
    
    # ==================== 頂部導航(訓練中隱藏) ====================
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
        
        mode = st.radio("訓練模式", ["🏠 徒手/啞鈴", "🏋️ 健身房儀器"], 
                       horizontal=True, key="mode_radio")
        category = "徒手/啞鈴" if "徒手" in mode else "健身房儀器"
        
        duration = st.radio("⏱️ 訓練時長(分鐘)", [15, 30, 45, 60], 
                           horizontal=True, key="duration_radio")
        
        # 休息時間選擇(新增)
        rest_options = {
            "🤖 自動依難度": "auto",
            "30秒": 30,
            "60秒": 60,
            "90秒": 90,
            "120秒": 120
        }
        rest_choice = st.radio(
            "😴 休息時間",
            list(rest_options.keys()),
            horizontal=True,
            key="rest_time_radio",
            help="自動依難度:初級60秒 / 中級90秒 / 高級120秒"
        )
        rest_setting = rest_options[rest_choice]
        
        with st.expander("🏥 傷病部位(選填)", expanded=False):
            injured = st.multiselect("選擇受傷部位", INJURY_AREAS, key="injury_select",
                                    label_visibility="collapsed")
        
        st.divider()
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
            
            selected_exercises_list = st.session_state.selected_exercises_list
            
            # ===== 已選動作清單(摺疊在最上方,顯眼但不佔空間)=====
            if selected_exercises_list:
                with st.expander(
                    f"📋 已選動作 ({len(selected_exercises_list)}個 · 共{sum(e['sets'] for e in selected_exercises_list)}組)",
                    expanded=False
                ):
                    for idx, ex in enumerate(selected_exercises_list):
                        col_ex, col_cancel = st.columns([8, 2])
                        with col_ex:
                            st.write(f"**{idx + 1}.** {ex['nameCN']}")
                            st.caption(f"{ex['sets']}組 × {ex['reps']}次")
                        with col_cancel:
                            if st.button("❌", key=f"remove_{ex['id']}", use_container_width=True):
                                st.session_state.selected_exercises_list = [s for s in selected_exercises_list if s.get("id") != ex["id"]]
                                st.rerun()
            
            # ===== 可用動作(已選的會消失)=====
            selected_ids = {s["id"] for s in selected_exercises_list}
            available_exercises = [e for e in all_exercises if e["id"] not in selected_ids]
            
            st.markdown(f"#### 🏆 可用動作 ({len(available_exercises)}個)")
            
            if not available_exercises:
                st.info("✅ 此部位的動作都已選完!")
            else:
                if len(selected_parts) > 1:
                    tabs = st.tabs(selected_parts)
                    for tab, part in zip(tabs, selected_parts):
                        with tab:
                            part_exercises = [e for e in available_exercises if e['bodyPart'] == part]
                            if not part_exercises:
                                st.info(f"✅ {part} 的動作都已選完")
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
                                    
                                    if st.button("✅ 加入訓練", key=f"toggle_{ex['id']}", 
                                                 use_container_width=True, type="primary"):
                                        selected_exercises_list.append(ex)
                                        st.session_state.selected_exercises_list = selected_exercises_list
                                        st.rerun()
                else:
                    for ex in available_exercises:
                        with st.container(border=True):
                            if ex["filename"] and ex["filename"] in IMAGES_DATA:
                                st.image(IMAGES_DATA[ex["filename"]], use_container_width=True)
                            else:
                                st.info("⏳ 圖片準備中")
                            st.markdown(f"**{ex['nameCN']}**")
                            st.caption(f"{ex['difficulty']} · {ex['sets']}組 × {ex['reps']}次 · {ex['equipment']}")
                            if ex['nameCN'] in warnings:
                                st.warning("⚠️ 請減輕重量")
                            
                            if st.button("✅ 加入訓練", key=f"toggle_{ex['id']}", 
                                         use_container_width=True, type="primary"):
                                selected_exercises_list.append(ex)
                                st.session_state.selected_exercises_list = selected_exercises_list
                                st.rerun()
            
            st.session_state.selected_exercises_list = selected_exercises_list
            
            # ===== 開始訓練按鈕 =====
            if selected_exercises_list:
                st.divider()
                st.success(f"✅ 共 {len(selected_exercises_list)} 個動作 · 總組數 {sum(e['sets'] for e in selected_exercises_list)}")
                
                if st.button("🎬 開始訓練", use_container_width=True, type="primary", key="start_workout_btn"):
                    st.session_state.workout = {
                        "exercises": selected_exercises_list,
                        "start": datetime.now(),
                        "duration": duration,
                        "rest_setting": rest_setting
                    }
                    st.session_state.current_ex_idx = 0
                    st.session_state.current_set = 1
                    st.session_state.workout_log = {}
                    st.session_state.exercise_weights = {}
                    st.session_state.exercise_reps = {}
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
        
        # ============ 休息倒數(改用 Streamlit 原生元件) ============
        if st.session_state.rest_timer_active and st.session_state.rest_end_time and not st.session_state.rest_skipped:
            remaining = (st.session_state.rest_end_time - datetime.now()).total_seconds()
            
            if remaining > 0:
                # 計算下一組/下一動作預告
                ex_now = exs[current_ex_idx] if current_ex_idx < len(exs) else None
                if ex_now and current_set <= ex_now["sets"]:
                    next_info = f"下一組:第 {current_set} 組 / 共 {ex_now['sets']} 組"
                else:
                    next_idx = current_ex_idx + 1 if current_set > exs[current_ex_idx]["sets"] else current_ex_idx
                    if next_idx < len(exs):
                        next_ex = exs[next_idx]
                        next_info = f"下一個動作:{next_ex['nameCN']}"
                    else:
                        next_info = "🎉 即將完成所有訓練!"
                
                # 進度百分比
                total = st.session_state.rest_total_seconds
                progress_pct = max(0.0, min(1.0, 1 - (remaining / total))) if total > 0 else 0
                
                # 用 container 包起來,確保佈局穩定
                rest_container = st.container()
                with rest_container:
                    # 大字體倒數顯示(用 markdown 但不用 fixed position)
                    st.markdown(f"""
                    <div style='text-align: center; 
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                padding: 30px 20px; 
                                border-radius: 16px; 
                                margin: 10px 0;
                                box-shadow: 0 4px 20px rgba(102,126,234,0.3);'>
                        <div style='color: white; font-size: 1.3rem; font-weight: 600; margin-bottom: 8px;'>
                            ⏱️ 休息中
                        </div>
                        <div style='color: #FFD700; font-size: 5rem; font-weight: 800; line-height: 1; margin: 10px 0;'>
                            {int(remaining)}
                        </div>
                        <div style='color: white; font-size: 1.1rem;'>秒</div>
                        <div style='color: #FFE4B5; font-size: 0.95rem; margin-top: 14px; padding: 8px; background: rgba(0,0,0,0.2); border-radius: 8px;'>
                            ⏭️ {next_info}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 進度條(視覺輔助)
                    st.progress(progress_pct)
                    
                    # ===== 跳過按鈕(超大、超明顯)=====
                    if st.button("⏭️ 跳過休息,直接下一組", 
                                 use_container_width=True, 
                                 type="primary", 
                                 key=f"btn_skip_rest_{int(remaining)}"):
                        st.session_state.rest_skipped = True
                        st.session_state.rest_timer_active = False
                        st.rerun()
                    
                    # ===== +/- 30 秒按鈕 =====
                    adj_col1, adj_col2 = st.columns(2)
                    with adj_col1:
                        if st.button("➖ 減 30 秒", 
                                     use_container_width=True, 
                                     key=f"btn_minus_30_{int(remaining)}"):
                            st.session_state.rest_end_time -= timedelta(seconds=30)
                            st.rerun()
                    with adj_col2:
                        if st.button("➕ 加 30 秒", 
                                     use_container_width=True, 
                                     key=f"btn_plus_30_{int(remaining)}"):
                            st.session_state.rest_end_time += timedelta(seconds=30)
                            st.rerun()
                
                # 振動提示(最後 3 秒)
                if int(remaining) <= 3:
                    st.markdown("""
                    <script>
                        if (navigator.vibrate) { navigator.vibrate([200]); }
                    </script>
                    """, unsafe_allow_html=True)
                
                # 倒數迴圈(每秒重新整理一次)
                time.sleep(1)
                st.rerun()
            else:
                # 倒數結束
                st.session_state.rest_timer_active = False
                st.session_state.rest_skipped = False
                st.success("✅ 休息結束!準備下一組")
                st.markdown("""
                <script>
                    if (navigator.vibrate) { navigator.vibrate([100, 50, 100, 50, 200]); }
                </script>
                """, unsafe_allow_html=True)
                time.sleep(0.5)
                st.rerun()
            
            # 休息中時停止繼續執行訓練畫面(用 return 不行,因為在 elif 裡)
            st.stop()
        
        # ============ 正常訓練畫面 ============
        if current_ex_idx < len(exs):
            ex = exs[current_ex_idx]
            
            # ===== 頂部緊湊資訊條(永遠在頂,不會被遮)=====
            st.markdown(f"""
            <div class="info-bar">
                <div>
                    <div style="font-size: 0.85rem; opacity: 0.9;">動作 {current_ex_idx + 1}/{len(exs)}</div>
                    <div style="font-size: 1.2rem; font-weight: 700;">{ex['nameCN']}</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 0.85rem; opacity: 0.9;">當前組</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #FFD700;">{current_set}/{ex['sets']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 進度條
            st.progress(progress, text=f"總進度: {completed_sets}/{total_sets} 組")
            
            # ===== 🎯 目標數顯示(最重要,放在最顯眼位置)=====
            target_weight_str = ""
            if ex['require_weight']:
                last_w = st.session_state.exercise_weights.get(f"ex_{ex['id']}", 0)
                if last_w > 0:
                    target_weight_str = f" · 上次重量 {last_w}kg"
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #ff9a56 0%, #ff6b6b 100%);
                        color: white; padding: 16px; border-radius: 12px; margin: 8px 0;
                        text-align: center; box-shadow: 0 4px 12px rgba(255,107,107,0.3);'>
                <div style='font-size: 0.9rem; opacity: 0.95;'>🎯 本組目標</div>
                <div style='font-size: 1.8rem; font-weight: 800; margin: 4px 0;'>
                    {ex['reps']} 次{target_weight_str}
                </div>
                <div style='font-size: 0.85rem; opacity: 0.9;'>節奏:{ex['tempo']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # ===== Tab 分頁(動作 / 紀錄)=====
            tab_action, tab_record = st.tabs(["📋 動作說明", "📊 紀錄這組"])
            
            # ─────── Tab 1:動作說明 ───────
            with tab_action:
                # 動作圖片(預設摺疊,需要才打開)
                with st.expander("🖼️ 點擊查看動作示範", expanded=False):
                    if ex["filename"] and ex["filename"] in IMAGES_DATA:
                        st.image(IMAGES_DATA[ex["filename"]], use_container_width=True)
                    else:
                        st.info("⏳ 圖片準備中")
                
                # 執行技巧
                st.markdown("**💡 執行技巧:**")
                for tip in ex["tips"]:
                    st.write(f"✅ {tip}")
                
                st.caption(f"目標肌群:{ex['target_muscle']} · 難度:{ex['difficulty']} · 器材:{ex['equipment']}")
                
                st.divider()
                
                # 下一組 / 下一動作預告
                if current_set < ex["sets"]:
                    next_text = f"⏭️ **下一組**:第 {current_set + 1} 組 / 共 {ex['sets']} 組"
                elif current_ex_idx + 1 < len(exs):
                    next_ex = exs[current_ex_idx + 1]
                    next_text = f"⏭️ **下個動作**:{next_ex['nameCN']} ({next_ex['sets']}組 × {next_ex['reps']}次)"
                else:
                    next_text = "🎉 **這是最後一組!**"
                st.info(next_text)
            
            # ─────── Tab 2:紀錄這組(簡化版) ───────
            with tab_record:
                records = get_records(user_id) or []
                workout_log = st.session_state.get("workout_log", {})
                last_set = get_last_set_data(workout_log, ex['nameCN'], current_set)
                
                # 上一組數據顯示(已砍疲勞度)
                if last_set:
                    last_weight_str = f" · 重量 {last_set.get('weight', 0)}kg" if last_set.get('weight') else ""
                    st.caption(f"📋 上一組:{last_set.get('reps', 0)} 次{last_weight_str}")
                
                # ----- 次數輸入(已砍 +/- 按鈕)-----
                past_best_reps = get_past_best_reps(records, ex['nameCN'])
                reps_label = "💪 完成次數"
                if past_best_reps:
                    reps_label += f" (歷史最高 {past_best_reps})"
                
                ex_key = f"ex_{ex['id']}"
                reps_input_key = f"reps_input_{current_ex_idx}_{current_set}"
                
                if reps_input_key not in st.session_state:
                    default_reps = st.session_state.exercise_reps.get(ex_key, ex['reps'])
                    st.session_state[reps_input_key] = default_reps
                
                actual_reps = st.number_input(
                    reps_label,
                    min_value=0,
                    max_value=ex['reps'] + 50,
                    key=reps_input_key
                )
                
                if past_best_reps and actual_reps > past_best_reps:
                    st.toast("🔥 突破紀錄了!", icon="🎉")
                
                # ----- 重量輸入(已砍 +/- 按鈕)-----
                weight = 0
                if ex['require_weight']:
                    past_best_weight = get_past_best_weight(records, ex['nameCN'])
                    weight_label = "🏋️ 重量 (kg)"
                    if past_best_weight:
                        weight_label += f" (歷史最高 {past_best_weight})"
                    
                    weight_input_key = f"weight_input_{current_ex_idx}_{current_set}"
                    
                    if weight_input_key not in st.session_state:
                        default_weight = st.session_state.exercise_weights.get(ex_key, 0.0)
                        st.session_state[weight_input_key] = default_weight
                    
                    weight = st.number_input(
                        weight_label,
                        min_value=0.0,
                        step=0.5,
                        key=weight_input_key
                    )
                    st.session_state.exercise_weights[ex_key] = weight
                    
                    if past_best_weight and weight > past_best_weight:
                        st.toast("🔥 突破紀錄了!", icon="🎉")
                
                # 已砍掉疲勞度滑桿
                
                st.divider()
                
                # ===== 主操作按鈕(完成這組) =====
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
                        "fatigue": 5,  # 預設值,不再要求使用者填
                        "volume": volume
                    }
                    
                    st.session_state.exercise_reps[ex_key] = actual_reps
                    
                    # 振動回饋
                    st.markdown("""
                    <script>
                        if (navigator.vibrate) { navigator.vibrate([100, 50, 100]); }
                    </script>
                    """, unsafe_allow_html=True)
                    
                    if current_set < ex["sets"]:
                        rest_setting = st.session_state.workout.get("rest_setting", "auto")
                        if rest_setting == "auto":
                            rest_time = REST_TIMES.get(ex['difficulty'], 60)
                        else:
                            rest_time = int(rest_setting)
                        
                        st.session_state.rest_timer_active = True
                        st.session_state.rest_end_time = datetime.now() + timedelta(seconds=rest_time)
                        st.session_state.rest_total_seconds = rest_time
                        st.session_state.rest_skipped = False
                        st.session_state.current_set += 1
                    else:
                        st.session_state.current_ex_idx += 1
                        st.session_state.current_set = 1
                    st.rerun()
            
            # ===== 次要操作(折疊,放在 Tab 外面)=====
            with st.expander("⚙️ 其他操作"):
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("⏭️ 跳過動作", use_container_width=True, key="btn_skip"):
                        st.session_state.current_ex_idx += 1
                        st.session_state.current_set = 1
                        st.rerun()
                with col2:
                    # 結束訓練(二次確認)
                    if st.button("⏹️ 結束訓練", use_container_width=True, key="btn_finish"):
                        st.session_state.confirm_finish = True
                        st.rerun()
                
                if st.session_state.get("confirm_finish"):
                    st.warning("⚠️ 確定要結束訓練嗎?目前進度會被保存。")
                    cc1, cc2 = st.columns(2)
                    with cc1:
                        if st.button("✅ 確定結束", use_container_width=True, type="primary", key="btn_confirm_finish"):
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
                            st.session_state.confirm_finish = False
                            st.session_state.page = "stats"
                            st.balloons()
                            st.rerun()
                    with cc2:
                        if st.button("↩️ 取消", use_container_width=True, key="btn_cancel_finish"):
                            st.session_state.confirm_finish = False
                            st.rerun()
        else:
            # 訓練完成
            st.success("🎉 訓練完成!")
            st.divider()
            
            dur = int((datetime.now() - st.session_state.workout["start"]).total_seconds() / 60)
            total_volume = sum(log.get("volume", 0) for log in st.session_state.workout_log.values())
            
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
            c1, c2 = st.columns(2)
            c1.metric("訓練次數", len(records))
            c2.metric("總組數", int(df['組數'].sum()))
            c3, c4 = st.columns(2)
            c3.metric("總時長", f"{int(df['時長(分)'].sum())}分")
            c4.metric("總熱量", int(df['熱量'].sum()))
            st.metric("累計 Volume", f"{int(df['總Volume'].sum())}")
            
            st.divider()
            st.markdown("#### 📋 訓練紀錄")
            
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
            # 清除 URL 參數
            st.query_params.clear()
            st.rerun()
        
        st.divider()
        with st.expander("ℹ️ 版本資訊"):
            st.success("""
            ✅ SmartFit v27 - 極簡操作版
            
            🆕 簡化:
            ✅ 砍掉 +/- 按鈕(直接打數字)
            ✅ 砍掉疲勞度(用不到)
            ✅ 動作圖片預設摺疊(節省空間)
            ✅ 訓練流程更精簡
            
            🎯 既有功能:
            ✅ Tab 分頁設計(動作/紀錄)
            ✅ 目標數醒目顯示
            ✅ 已選動作摺疊
            ✅ 自訂休息時間
            ✅ URL 自動登入
            ✅ Google Sheets 雲端儲存
            
            🎯 v23 修復:
            ✅ +/- 按鈕點擊後數字立即更新
            ✅ +/- 按鈕移到輸入框上方
            
            🎯 既有功能:
            ✅ 首頁可自訂休息時間(30/60/90/120秒)
            ✅ 雲端儲存(Google Sheets)
            ✅ 休息時間 +30/-30 秒調整
            ✅ 下一組/下一動作預告
            ✅ 上一組數據顯示
            ✅ 快速 +/- 重量按鈕
            ✅ 快速 +/- 次數按鈕
            ✅ 緊湊資訊條(免下拉)
            ✅ 動作圖片可折疊
            ✅ 結束訓練二次確認
            ✅ 振動回饋
            
            🎯 核心功能:
            ✅ 重量+次數雙記憶
            ✅ 多用戶獨立記錄
            ✅ 50個動作完整資料庫
            """)
