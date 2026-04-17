import streamlit as st
import json
from datetime import datetime
import pandas as pd
from pathlib import Path
import time

# 页面配置
st.set_page_config(
    page_title="SmartFit 健身 APP",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 改進的 CSS - 更鮮豔的顏色
st.markdown("""
<style>
    .main {
        padding: 0rem 0rem;
    }
    .exercise-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 4px solid #ff6b6b;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .exercise-card-gym {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 4px solid #ff9999;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .success-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        color: white;
    }
    .icon-large {
        font-size: 40px;
        margin-right: 10px;
    }
    .timer-display {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        color: #ff6b6b;
        padding: 20px;
        background: #f0f2f6;
        border-radius: 10px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 50 個動作數據 ====================

EXERCISES = [
    # 徒手 - 胸部 (5)
    {"id": "001", "name": "Push-ups", "nameCN": "俯臥撑", "bodyPart": "胸部", "difficulty": "初級", "sets": 3, "reps": 12, "restSeconds": 60, "mode": "徒手", "icon": "🏋️", "description": "經典的徒手胸部訓練動作", "tips": ["保持身體成一直線", "降低身體直到胸部接近地面", "推回起始位置"], "mistakes": ["臀部下沉", "肘部張得太開", "活動範圍不足"], "youtubeKeyword": "push ups proper form"},
    {"id": "002", "name": "Wide Push-ups", "nameCN": "寬距俯臥撑", "bodyPart": "胸部", "difficulty": "初級", "sets": 3, "reps": 10, "restSeconds": 60, "mode": "徒手", "icon": "🏋️", "description": "寬距俯臥撑更針對胸部外側", "tips": ["雙手距離比肩膀寬", "保持直線", "完整範圍"], "mistakes": ["太寬容易傷肩", "肘部內彎", "不穩定"], "youtubeKeyword": "wide grip push ups"},
    {"id": "003", "name": "Diamond Push-ups", "nameCN": "菱形俯臥撑", "bodyPart": "胸部", "difficulty": "中級", "sets": 3, "reps": 8, "restSeconds": 60, "mode": "徒手", "icon": "💎", "description": "針對三頭肌和內胸", "tips": ["雙手在胸下方", "肘部靠近身體", "完全伸展"], "mistakes": ["肘部張太開", "身體搖晃", "範圍太小"], "youtubeKeyword": "diamond push ups form"},
    {"id": "004", "name": "Pseudo Planche Push-ups", "nameCN": "偽前水平俯臥撑", "bodyPart": "胸部", "difficulty": "高級", "sets": 3, "reps": 5, "restSeconds": 90, "mode": "徒手", "icon": "✈️", "description": "進階版俯臥撑訓練", "tips": ["身體向前傾", "手在腰部", "保持平衡"], "mistakes": ["傾斜角度不夠", "肘部張太開", "頭不穩"], "youtubeKeyword": "pseudo planche push ups"},
    {"id": "005", "name": "Archer Push-ups", "nameCN": "箭手俯臥撑", "bodyPart": "胸部", "difficulty": "高級", "sets": 3, "reps": 6, "restSeconds": 90, "mode": "徒手", "icon": "🏹", "description": "單臂俯臥撑進階", "tips": ["一側手臂彎曲", "另一側伸直", "平衡很重要"], "mistakes": ["身體旋轉", "速度太快", "不穩定"], "youtubeKeyword": "archer push ups technique"},

    # 徒手 - 背部 (5)
    {"id": "006", "name": "Pull-ups", "nameCN": "引體向上", "bodyPart": "背部", "difficulty": "中級", "sets": 3, "reps": 8, "restSeconds": 120, "mode": "徒手", "icon": "💪", "description": "上身拉力訓練", "tips": ["握距略寬於肩膀", "下巴超過橫杆", "控制下降"], "mistakes": ["活動範圍不足", "使用衝力", "肘部張得太開"], "youtubeKeyword": "pull ups proper form"},
    {"id": "007", "name": "Chin-ups", "nameCN": "窄握引體向上", "bodyPart": "背部", "difficulty": "中級", "sets": 3, "reps": 8, "restSeconds": 120, "mode": "徒手", "icon": "🤸", "description": "窄握引體更侧重二頭肌", "tips": ["掌心朝向自己", "肘部靠近身體", "平順動作"], "mistakes": ["搖晃身體", "不完整範圍", "速度不穩"], "youtubeKeyword": "chin ups form"},
    {"id": "008", "name": "Reverse Rows", "nameCN": "反向划船", "bodyPart": "背部", "difficulty": "初級", "sets": 3, "reps": 12, "restSeconds": 60, "mode": "徒手", "icon": "🔄", "description": "低檯面划船訓練背部", "tips": ["身體保持直線", "拉至胸部", "控制下降"], "mistakes": ["臀部下沉", "不完整動作", "太快速度"], "youtubeKeyword": "inverted rows beginner"},
    {"id": "009", "name": "Superman Hold", "nameCN": "超人式", "bodyPart": "背部", "difficulty": "初級", "sets": 3, "reps": 30, "restSeconds": 60, "mode": "徒手", "icon": "🦸", "description": "背部肌群穩定訓練", "tips": ["手臂向前伸", "腿向後伸", "胸部離地"], "mistakes": ["脖子過度後仰", "下背過度彎曲", "臀部沒收緊"], "youtubeKeyword": "superman hold exercise"},
    {"id": "010", "name": "Scapular Pull-ups", "nameCN": "肩胛骨引體向上", "bodyPart": "背部", "difficulty": "初級", "sets": 3, "reps": 10, "restSeconds": 60, "mode": "徒手", "icon": "⬆️", "description": "背部啟動訓練", "tips": ["只用背部拉", "手臂不彎曲", "小幅度動作"], "mistakes": ["臂力主導", "範圍太大", "不穩定"], "youtubeKeyword": "scapular pull ups"},

    # 徒手 - 腿部 (5)
    {"id": "011", "name": "Squats", "nameCN": "深蹲", "bodyPart": "腿部", "difficulty": "初級", "sets": 3, "reps": 15, "restSeconds": 90, "mode": "徒手", "icon": "🦵", "description": "下身訓練的基礎動作", "tips": ["挺胸保持核心緊縮", "臀部向後向下移動", "通過腳跟推起"], "mistakes": ["膝蓋內扣", "身體向前傾斜過多", "深度不夠"], "youtubeKeyword": "bodyweight squats form"},
    {"id": "012", "name": "Jump Squats", "nameCN": "跳躍深蹲", "bodyPart": "腿部", "difficulty": "中級", "sets": 3, "reps": 12, "restSeconds": 90, "mode": "徒手", "icon": "⬆️", "description": "爆發力腿部訓練", "tips": ["全力跳躍", "軟著陸", "快速站起"], "mistakes": ["著陸時膝蓋內扣", "沒有完整深蹲", "容易傷膝"], "youtubeKeyword": "jump squats proper technique"},
    {"id": "013", "name": "Lunges", "nameCN": "弓步", "bodyPart": "腿部", "difficulty": "初級", "sets": 3, "reps": 12, "restSeconds": 60, "mode": "徒手", "icon": "🚶", "description": "單邊腿部訓練", "tips": ["前腳膝蓋成 90 度", "後腳膝蓋接近地面", "保持直立"], "mistakes": ["膝蓋超過腳尖", "身體前傾", "步幅不夠"], "youtubeKeyword": "lunges proper form"},
    {"id": "014", "name": "Single Leg Squats", "nameCN": "單腿深蹲", "bodyPart": "腿部", "difficulty": "高級", "sets": 3, "reps": 5, "restSeconds": 120, "mode": "徒手", "icon": "🦵", "description": "進階單邊腿部訓練", "tips": ["一隻腳懸空", "保持平衡", "完整深蹲"], "mistakes": ["身體旋轉", "不夠深", "失去平衡"], "youtubeKeyword": "pistol squat progression"},
    {"id": "015", "name": "Calf Raises", "nameCN": "提踵", "bodyPart": "腿部", "difficulty": "初級", "sets": 3, "reps": 20, "restSeconds": 60, "mode": "徒手", "icon": "👟", "description": "小腿訓練", "tips": ["站直或在台階上", "提起腳跟", "控制下降"], "mistakes": ["身體搖晃", "速度太快", "範圍太小"], "youtubeKeyword": "calf raises form"},

    # 徒手 - 核心 (5)
    {"id": "016", "name": "Plank", "nameCN": "棒式", "bodyPart": "核心", "difficulty": "初級", "sets": 3, "reps": 30, "restSeconds": 60, "mode": "徒手", "icon": "📍", "description": "核心穩定性訓練", "tips": ["身體成一直線", "全程核心緊縮", "不要臀部下沉"], "mistakes": ["臀部下沉", "頸部過度拉伸", "肩膀過度前傾"], "youtubeKeyword": "perfect plank form"},
    {"id": "017", "name": "Side Plank", "nameCN": "側棒式", "bodyPart": "核心", "difficulty": "初級", "sets": 3, "reps": 20, "restSeconds": 60, "mode": "徒手", "icon": "◀️", "description": "側核心訓練", "tips": ["身體成直線", "核心收緊", "臀部不要下沉"], "mistakes": ["身體下垂", "扭轉身體", "太快速度"], "youtubeKeyword": "side plank exercise"},
    {"id": "018", "name": "Sit-ups", "nameCN": "仰臥起坐", "bodyPart": "核心", "difficulty": "初級", "sets": 3, "reps": 15, "restSeconds": 60, "mode": "徒手", "icon": "⬆️", "description": "腹部訓練", "tips": ["膝蓋彎曲", "不要拉脖子", "胸部朝膝蓋"], "mistakes": ["拉脖子", "速度過快", "腿部踢動"], "youtubeKeyword": "proper sit ups form"},
    {"id": "019", "name": "Mountain Climbers", "nameCN": "爬山者", "bodyPart": "核心", "difficulty": "中級", "sets": 3, "reps": 20, "restSeconds": 60, "mode": "徒手", "icon": "🏔️", "description": "動態核心訓練", "tips": ["快速交替腿部", "保持俯臥撑姿勢", "核心緊縮"], "mistakes": ["臀部抬起", "速度不一", "核心放鬆"], "youtubeKeyword": "mountain climbers exercise"},
    {"id": "020", "name": "Leg Raises", "nameCN": "抬腿", "bodyPart": "核心", "difficulty": "初級", "sets": 3, "reps": 12, "restSeconds": 60, "mode": "徒手", "icon": "🦵", "description": "下腹部訓練", "tips": ["躺下背部貼地", "腿部保持直", "控制速度"], "mistakes": ["背部離地", "太快速度", "腿部彎曲"], "youtubeKeyword": "leg raises core exercise"},

    # 健身房 - 胸部 (5)
    {"id": "021", "name": "Dumbbell Bench Press", "nameCN": "啞鈴臥推", "bodyPart": "胸部", "difficulty": "中級", "sets": 4, "reps": 10, "restSeconds": 90, "mode": "健身房", "icon": "🏗️", "description": "使用啞鈴的胸部訓練", "tips": ["身體呈平板狀", "啞鈴降至胸部", "爆發力推起"], "mistakes": ["彈跳重量", "推力不均勻", "肘部貼得太近"], "youtubeKeyword": "dumbbell bench press form"},
    {"id": "022", "name": "Barbell Bench Press", "nameCN": "槓鈴臥推", "bodyPart": "胸部", "difficulty": "中級", "sets": 4, "reps": 8, "restSeconds": 120, "mode": "健身房", "icon": "⬆️", "description": "槓鈴胸部訓練", "tips": ["背部貼板", "肩膀穩定", "平順動作"], "mistakes": ["反弓背部", "不穩定", "速度不均"], "youtubeKeyword": "barbell bench press technique"},
    {"id": "023", "name": "Incline Dumbbell Press", "nameCN": "上斜啞鈴推", "bodyPart": "胸部", "difficulty": "中級", "sets": 3, "reps": 10, "restSeconds": 90, "mode": "健身房", "icon": "📈", "description": "上胸部訓練", "tips": ["調至 45 度", "控制範圍", "穩定推起"], "mistakes": ["傾斜角度不當", "肘部位置差", "搖晃身體"], "youtubeKeyword": "incline dumbbell press"},
    {"id": "024", "name": "Cable Flyes", "nameCN": "拉力機夾胸", "bodyPart": "胸部", "difficulty": "中級", "sets": 3, "reps": 12, "restSeconds": 60, "mode": "健身房", "icon": "🔗", "description": "拉力機胸部孤立訓練", "tips": ["手臂微彎", "控制回放", "集中收縮"], "mistakes": ["手臂完全伸直", "太快速度", "重量過重"], "youtubeKeyword": "cable chest flyes exercise"},
    {"id": "025", "name": "Chest Press Machine", "nameCN": "胸部推蹬機", "bodyPart": "胸部", "difficulty": "初級", "sets": 3, "reps": 12, "restSeconds": 60, "mode": "健身房", "icon": "🎯", "description": "機械式胸部訓練", "tips": ["坐直對齊機器", "完全推出", "控制回放"], "mistakes": ["肘部太低", "過度推出", "不穩定"], "youtubeKeyword": "chest press machine proper form"},

    # 健身房 - 背部 (5)
    {"id": "026", "name": "Barbell Squat", "nameCN": "槓鈴深蹲", "bodyPart": "腿部", "difficulty": "中級", "sets": 4, "reps": 8, "restSeconds": 120, "mode": "健身房", "icon": "⬇️", "description": "加重腿部訓練", "tips": ["槓鈴放在肩膀", "保持直立姿勢", "深蹲至平行"], "mistakes": ["膝蓋超過腳尖", "過度傾斜", "不夠深"], "youtubeKeyword": "barbell back squat form"},
    {"id": "027", "name": "Cable Row", "nameCN": "拉力機划船", "bodyPart": "背部", "difficulty": "初級", "sets": 4, "reps": 12, "restSeconds": 60, "mode": "健身房", "icon": "🔗", "description": "背部拉力機訓練", "tips": ["坐直保持挺胸", "拉至腹部", "控制回放"], "mistakes": ["過度前傾", "手臂主導", "不完整動作"], "youtubeKeyword": "cable row machine form"},
    {"id": "028", "name": "Lat Pulldown", "nameCN": "下拉機", "bodyPart": "背部", "difficulty": "初級", "sets": 3, "reps": 12, "restSeconds": 60, "mode": "健身房", "icon": "⬇️", "description": "背闊肌下拉訓練", "tips": ["拉至胸部", "控制回放", "全程核心緊縮"], "mistakes": ["身體搖晃", "手臂主導", "不完整範圍"], "youtubeKeyword": "lat pulldown proper technique"},
    {"id": "029", "name": "Barbell Rows", "nameCN": "槓鈴划船", "bodyPart": "背部", "difficulty": "中級", "sets": 4, "reps": 8, "restSeconds": 120, "mode": "健身房", "icon": "💪", "description": "槓鈴背部訓練", "tips": ["膝蓋微彎", "背部直", "拉至腹部"], "mistakes": ["過度彎腰", "不穩定", "速度不一"], "youtubeKeyword": "barbell row form tutorial"},
    {"id": "030", "name": "Dumbbell Rows", "nameCN": "啞鈴划船", "bodyPart": "背部", "difficulty": "中級", "sets": 4, "reps": 10, "restSeconds": 90, "mode": "健身房", "icon": "💪", "description": "背部划船訓練", "tips": ["單膝跪地或側身", "保持核心穩定", "啞鈴拉至腰部"], "mistakes": ["轉動身體獲得動力", "不完全收縮", "肩膀過度內收"], "youtubeKeyword": "dumbbell row technique"},

    # 健身房 - 肩膀 (5)
    {"id": "031", "name": "Shoulder Press", "nameCN": "肩推", "bodyPart": "肩膀", "difficulty": "中級", "sets": 3, "reps": 12, "restSeconds": 60, "mode": "健身房", "icon": "⬆️", "description": "肩膀推力訓練", "tips": ["啞鈴至肩膀高度", "上推至頭頂", "控制下降"], "mistakes": ["過度拱腰", "肘部位置不當", "活動不完全"], "youtubeKeyword": "shoulder press proper form"},
    {"id": "032", "name": "Lateral Raises", "nameCN": "側平舉", "bodyPart": "肩膀", "difficulty": "初級", "sets": 3, "reps": 12, "restSeconds": 60, "mode": "健身房", "icon": "➡️", "description": "側肩訓練", "tips": ["手臂微彎", "抬至肩高", "控制速度"], "mistakes": ["太重太快", "身體搖晃", "肘部張太開"], "youtubeKeyword": "lateral raises exercise"},
    {"id": "033", "name": "Front Raises", "nameCN": "前平舉", "bodyPart": "肩膀", "difficulty": "初級", "sets": 3, "reps": 12, "restSeconds": 60, "mode": "健身房", "icon": "📤", "description": "前肩訓練", "tips": ["手臂微彎", "抬至肩高", "緩慢上下"], "mistakes": ["動量太大", "太重", "不穩定"], "youtubeKeyword": "front raises form"},
    {"id": "034", "name": "Reverse Pec Deck", "nameCN": "反向夾胸機", "bodyPart": "肩膀", "difficulty": "初級", "sets": 3, "reps": 12, "restSeconds": 60, "mode": "健身房", "icon": "🔄", "description": "後肩訓練", "tips": ["坐直", "手臂向外", "控制回放"], "mistakes": ["身體搖晃", "太重", "不完整"], "youtubeKeyword": "reverse pec deck machine"},
    {"id": "035", "name": "Shrugs", "nameCN": "聳肩", "bodyPart": "肩膀", "difficulty": "初級", "sets": 3, "reps": 15, "restSeconds": 60, "mode": "健身房", "icon": "⬆️", "description": "上背和陷阱肌訓練", "tips": ["聳肩至耳朵", "停頓一秒", "緩慢下降"], "mistakes": ["旋轉肩膀", "搖晃身體", "太快速度"], "youtubeKeyword": "shrugs exercise form"},

    # 健身房 - 手臂 (5)
    {"id": "036", "name": "Bicep Curls", "nameCN": "二頭肌彎舉", "bodyPart": "手臂", "difficulty": "初級", "sets": 3, "reps": 12, "restSeconds": 60, "mode": "健身房", "icon": "💪", "description": "二頭肌孤立訓練", "tips": ["靠在牆上保持穩定", "只有前臂移動", "充分收縮"], "mistakes": ["使用衝力搖晃", "不完全伸展", "肘部移動"], "youtubeKeyword": "bicep curls proper form"},
    {"id": "037", "name": "Tricep Dips", "nameCN": "三頭肌撐體", "bodyPart": "手臂", "difficulty": "中級", "sets": 3, "reps": 10, "restSeconds": 90, "mode": "健身房", "icon": "⬇️", "description": "三頭肌訓練動作", "tips": ["身體向前稍微傾斜", "肘部彎曲至90度", "通過三頭肌推起"], "mistakes": ["向前傾斜太多", "下降不足", "肘部外張太寬"], "youtubeKeyword": "tricep dips proper form"},
    {"id": "038", "name": "Tricep Rope Pushdown", "nameCN": "三頭肌繩索下壓", "bodyPart": "手臂", "difficulty": "初級", "sets": 3, "reps": 12, "restSeconds": 60, "mode": "健身房", "icon": "🔗", "description": "繩索三頭肌訓練", "tips": ["肘部不動", "完全伸展", "控制回放"], "mistakes": ["肘部移動", "太快速度", "範圍太小"], "youtubeKeyword": "tricep rope pushdown"},
    {"id": "039", "name": "Hammer Curls", "nameCN": "錘式彎舉", "bodyPart": "手臂", "difficulty": "初級", "sets": 3, "reps": 12, "restSeconds": 60, "mode": "健身房", "icon": "🔨", "description": "握法不同的二頭肌訓練", "tips": ["掌心相對", "只有前臂動", "控制速度"], "mistakes": ["肘部張開", "身體搖晃", "太快速度"], "youtubeKeyword": "hammer curls exercise"},
    {"id": "040", "name": "Cable Curls", "nameCN": "拉力機彎舉", "bodyPart": "手臂", "difficulty": "初級", "sets": 3, "reps": 12, "restSeconds": 60, "mode": "健身房", "icon": "🔗", "description": "拉力機二頭肌訓練", "tips": ["肘部固定", "張力持續", "控制回放"], "mistakes": ["肘部移動", "晃動身體", "速度不一"], "youtubeKeyword": "cable bicep curls"},

    # 健身房 - 腿部 (5)
    {"id": "041", "name": "Leg Press Machine", "nameCN": "腿部推蹬機", "bodyPart": "腿部", "difficulty": "初級", "sets": 3, "reps": 15, "restSeconds": 90, "mode": "健身房", "icon": "🚀", "description": "機械式腿部推蹬", "tips": ["腳放在機器上", "完全伸展", "控制下降"], "mistakes": ["膝蓋鎖定", "下降不足", "重量過重"], "youtubeKeyword": "leg press machine form"},
    {"id": "042", "name": "Leg Curl", "nameCN": "腿部卷舉機", "bodyPart": "腿部", "difficulty": "初級", "sets": 3, "reps": 12, "restSeconds": 60, "mode": "健身房", "icon": "↪️", "description": "腿後肌訓練", "tips": ["坐直", "卷起至胸部", "控制回放"], "mistakes": ["身體搖晃", "太快速度", "不完整"], "youtubeKeyword": "leg curl machine exercise"},
    {"id": "043", "name": "Leg Extension", "nameCN": "腿部伸展機", "bodyPart": "腿部", "difficulty": "初級", "sets": 3, "reps": 12, "restSeconds": 60, "mode": "健身房", "icon": "⬆️", "description": "股四頭肌訓練", "tips": ["坐直", "完全伸展", "控制回放"], "mistakes": ["速度太快", "不完整", "搖晃身體"], "youtubeKeyword": "leg extension machine form"},
    {"id": "044", "name": "Hack Squat", "nameCN": "哈克深蹲機", "bodyPart": "腿部", "difficulty": "中級", "sets": 3, "reps": 12, "restSeconds": 90, "mode": "健身房", "icon": "📍", "description": "機械式深蹲訓練", "tips": ["肩膀靠機器", "深蹲至平行", "完整動作"], "mistakes": ["膝蓋內扣", "不夠深", "傾斜身體"], "youtubeKeyword": "hack squat machine"},
    {"id": "045", "name": "Smith Machine Squats", "nameCN": "史密斯機深蹲", "bodyPart": "腿部", "difficulty": "初級", "sets": 3, "reps": 12, "restSeconds": 90, "mode": "健身房", "icon": "📐", "description": "導軌式深蹲訓練", "tips": ["槓在肩膀", "直線下降", "平行深蹲"], "mistakes": ["身體傾斜", "膝蓋超前", "不夠深"], "youtubeKeyword": "smith machine squats form"},

    # 健身房 - 核心 (5)
    {"id": "046", "name": "Cable Crunches", "nameCN": "拉力機卷腹", "bodyPart": "核心", "difficulty": "初級", "sets": 3, "reps": 12, "restSeconds": 60, "mode": "健身房", "icon": "🔗", "description": "拉力機核心訓練", "tips": ["膝蓋彎曲", "卷起至膝蓋", "控制回放"], "mistakes": ["不完整卷起", "太快速度", "肘部位置"], "youtubeKeyword": "cable crunches exercise"},
    {"id": "047", "name": "Ab Wheel", "nameCN": "腹肌滑輪", "bodyPart": "核心", "difficulty": "中級", "sets": 3, "reps": 10, "restSeconds": 60, "mode": "健身房", "icon": "⭕", "description": "滾輪核心訓練", "tips": ["膝蓋跪地", "向前滾", "回收時縮腹"], "mistakes": ["背部過度彎曲", "不完整", "太快速度"], "youtubeKeyword": "ab wheel exercise"},
    {"id": "048", "name": "Weighted Vest Plank", "nameCN": "負重棒式", "bodyPart": "核心", "difficulty": "中級", "sets": 3, "reps": 30, "restSeconds": 60, "mode": "健身房", "icon": "🦺", "description": "加重棒式訓練", "tips": ["穿上負重背心", "保持直線", "全程緊縮"], "mistakes": ["臀部下沉", "身體搖晃", "頭不穩"], "youtubeKeyword": "weighted plank exercise"},
    {"id": "049", "name": "Machine Ab Crunch", "nameCN": "腹肌卷腹機", "bodyPart": "核心", "difficulty": "初級", "sets": 3, "reps": 12, "restSeconds": 60, "mode": "健身房", "icon": "🎯", "description": "機械式卷腹訓練", "tips": ["坐直對齊", "卷起完整", "控制回放"], "mistakes": ["身體搖晃", "太快速度", "不完整"], "youtubeKeyword": "ab crunch machine form"},
    {"id": "050", "name": "Hanging Leg Raises", "nameCN": "懸掛抬腿", "bodyPart": "核心", "difficulty": "中級", "sets": 3, "reps": 10, "restSeconds": 90, "mode": "健身房", "icon": "🏃", "description": "進階下腹訓練", "tips": ["雙手握把", "雙腿抬至水平", "控制下降"], "mistakes": ["搖晃身體", "速度太快", "範圍太小"], "youtubeKeyword": "hanging leg raises exercise"},
]

BODY_PARTS = ["胸部", "背部", "肩膀", "手臂", "腿部", "核心", "全身"]

# ==================== 初始化 Session State ====================

if "current_page" not in st.session_state:
    st.session_state.current_page = "首頁"

if "user_data" not in st.session_state:
    st.session_state.user_data = {
        "name": "",
        "age": 25,
        "mode": "徒手",
        "experience": "初級"
    }

if "workout_records" not in st.session_state:
    st.session_state.workout_records = []

if "current_workout" not in st.session_state:
    st.session_state.current_workout = None

if "workout_progress" not in st.session_state:
    st.session_state.workout_progress = {}

if "selected_exercise" not in st.session_state:
    st.session_state.selected_exercise = None

if "timer_active" not in st.session_state:
    st.session_state.timer_active = False

if "timer_time" not in st.session_state:
    st.session_state.timer_time = 0

# ==================== 功能函数 ====================

def get_recommended_exercises(body_parts, duration, mode):
    """获取推荐动作 - 按模式区分"""
    filtered = EXERCISES
    
    # 按模式筛选
    filtered = [e for e in filtered if e["mode"] == mode]
    
    # 按身体部位筛选
    filtered = [e for e in filtered if e["bodyPart"] in body_parts]
    
    # 返回推荐的动作（限制数量）
    return filtered[:4] if len(filtered) > 4 else filtered

def get_youtube_embed(keyword):
    """生成 YouTube 嵌入 HTML"""
    return f"""
    <iframe width="100%" height="400" src="https://www.youtube.com/embed?listType=search&list={keyword.replace(' ', '%20')}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
    """

def save_workout_record(exercises, duration):
    """保存训练记录"""
    record = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "exercises": exercises,
        "duration": duration,
        "calories": duration * 7
    }
    st.session_state.workout_records.append(record)

# ==================== 页面 1: 首页 ====================

def page_home():
    st.title("💪 SmartFit - 您的私人健身教練")
    st.write("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 選擇訓練模式")
        mode = st.radio("模式", ["🏠 徒手訓練", "🏋️ 健身房"], key="mode_select")
        st.session_state.user_data["mode"] = "徒手" if "徒手" in mode else "健身房"
    
    with col2:
        st.subheader("📊 選擇訓練時長")
        duration = st.radio("時長", [15, 30, 45, 60], horizontal=True, key="duration_select")
    
    st.write("---")
    
    st.subheader("🎯 選擇訓練部位（可多選）")
    
    # 创建网格布局
    cols = st.columns(3)
    selected_parts = []
    
    for i, part in enumerate(BODY_PARTS):
        with cols[i % 3]:
            if st.checkbox(part, key=f"part_{i}"):
                selected_parts.append(part)
    
    st.write("---")
    
    if selected_parts:
        st.success(f"✅ 已選擇: {', '.join(selected_parts)}")
        
        # 获取推荐动作
        recommended = get_recommended_exercises(selected_parts, duration, st.session_state.user_data["mode"])
        
        if not recommended:
            st.warning(f"⚠️ 沒有找到適合 {st.session_state.user_data['mode']} 訓練的 {', '.join(selected_parts)} 動作")
            st.info("💡 提示：健身房模式會推薦需要器材的動作，徒手模式推薦無需器材的動作")
        else:
            st.subheader(f"🏆 推薦訓練動作 ({len(recommended)} 個)")
            
            for exercise in recommended:
                # 根據模式選擇背景顏色
                card_class = "exercise-card-gym" if exercise["mode"] == "健身房" else "exercise-card"
                
                with st.container():
                    col1, col2, col3 = st.columns([1, 3, 1])
                    
                    with col1:
                        st.markdown(f"<div style='font-size: 40px; margin-top: 10px;'>{exercise['icon']}</div>", 
                                   unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class='{card_class}'>
                            <strong>{exercise['nameCN']}</strong> ({exercise['name']})<br>
                            難度: {exercise['difficulty']} | 部位: {exercise['bodyPart']}<br>
                            {exercise['sets']} 組 × {exercise['reps']} 次 | 休息: {exercise['restSeconds']} 秒
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("📺", key=f"yt_{exercise['id']}", help="YouTube"):
                                st.session_state.current_page = "YouTube教學"
                                st.session_state.selected_exercise = exercise
                                st.rerun()
                        with col_b:
                            if st.button("📋", key=f"view_{exercise['id']}", help="詳細"):
                                st.session_state.current_page = "動作詳情"
                                st.session_state.selected_exercise = exercise
                                st.rerun()
            
            st.write("---")
            
            if st.button("🎬 開始訓練", key="start_workout", use_container_width=True):
                st.session_state.current_workout = {
                    "exercises": [e["nameCN"] for e in recommended],
                    "exercise_objects": recommended,
                    "duration": duration,
                    "body_parts": selected_parts,
                    "start_time": datetime.now()
                }
                st.session_state.workout_progress = {
                    "current_exercise": 0,
                    "sets": 1,
                    "reps": 1
                }
                st.session_state.current_page = "訓練執行"
                st.rerun()
    else:
        st.info("👈 請先選擇要訓練的部位")

# ==================== 页面 2: 动作库 ====================

def page_exercise_list():
    st.title("💪 動作庫")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_text = st.text_input("🔍 搜尋動作", "")
    
    with col2:
        selected_body_part = st.selectbox("篩選部位", ["全部"] + BODY_PARTS)
    
    st.write("---")
    
    # 筛选动作
    filtered_exercises = EXERCISES
    
    if selected_body_part != "全部":
        filtered_exercises = [e for e in filtered_exercises if e["bodyPart"] == selected_body_part]
    
    if search_text:
        filtered_exercises = [e for e in filtered_exercises 
                            if search_text.lower() in e["nameCN"].lower() 
                            or search_text.lower() in e["name"].lower()]
    
    if not filtered_exercises:
        st.info("沒有找到相符的動作")
        return
    
    st.write(f"找到 {len(filtered_exercises)} 個動作")
    
    for exercise in filtered_exercises:
        card_class = "exercise-card-gym" if exercise["mode"] == "健身房" else "exercise-card"
        
        with st.expander(f"{exercise['icon']} **{exercise['nameCN']}** - {exercise['difficulty']} ({exercise['mode']})", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**英文名稱**: {exercise['name']}")
                st.write(f"**目標部位**: {exercise['bodyPart']}")
                st.write(f"**難度**: {exercise['difficulty']}")
                st.write(f"**推薦**: {exercise['sets']}組 × {exercise['reps']}次")
                st.write(f"**休息時間**: {exercise['restSeconds']}秒")
            
            with col2:
                st.write(f"**描述**: {exercise['description']}")
            
            st.write("---")
            
            st.write("**執行技巧**:")
            for tip in exercise["tips"]:
                st.write(f"✅ {tip}")
            
            st.write("**常見錯誤**:")
            for mistake in exercise["mistakes"]:
                st.write(f"❌ {mistake}")
            
            st.write("---")
            
            if st.button(f"📺 在 YouTube 查看《{exercise['nameCN']}》教學", key=f"yt_detail_{exercise['id']}"):
                st.session_state.current_page = "YouTube教學"
                st.session_state.selected_exercise = exercise
                st.rerun()

# ==================== 页面 3: YouTube教學 ====================

def page_youtube():
    if not st.session_state.selected_exercise:
        st.error("沒有選擇動作")
        return
    
    exercise = st.session_state.selected_exercise
    
    st.title(f"📺 {exercise['nameCN']} - YouTube 教學")
    
    st.write(f"**動作**: {exercise['name']}")
    st.write(f"**部位**: {exercise['bodyPart']} | **難度**: {exercise['difficulty']}")
    
    st.write("---")
    
    st.subheader("熱門教學視頻")
    
    # 嵌入 YouTube iframe
    search_url = f"https://www.youtube.com/results?search_query={exercise['youtubeKeyword'].replace(' ', '+')}"
    
    # 使用簡化的嵌入方式
    st.markdown(f"""
    <div style="position: relative; width: 100%; padding-bottom: 56.25%; height: 0; overflow: hidden;">
        <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" 
                src="https://www.youtube.com/embed?listType=search&list={exercise['youtubeKeyword'].replace(' ', '%20')}" 
                frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                allowfullscreen></iframe>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    
    st.markdown(f"[🔗 點擊查看更多視頻]({search_url})")
    
    if st.button("⬅️ 返回首頁"):
        st.session_state.current_page = "首頁"
        st.rerun()

# ==================== 页面 4: 训练执行 ====================

def page_workout_execution():
    st.title("🏃 訓練中...")
    
    if not st.session_state.current_workout:
        st.error("沒有進行中的訓練")
        if st.button("返回首頁"):
            st.session_state.current_page = "首頁"
            st.rerun()
        return
    
    workout = st.session_state.current_workout
    
    # 進度條
    total_exercises = len(workout["exercises"])
    current_index = st.session_state.workout_progress.get("current_exercise", 0)
    
    progress = current_index / total_exercises if total_exercises > 0 else 0
    st.progress(progress, text=f"進度: {current_index}/{total_exercises}")
    
    st.write("---")
    
    # 显示当前动作
    if current_index < total_exercises:
        current_exercise = workout["exercise_objects"][current_index]
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            st.markdown(f"<div style='font-size: 80px; text-align: center;'>{current_exercise['icon']}</div>", 
                       unsafe_allow_html=True)
        
        with col2:
            st.subheader(f"當前動作: {current_exercise['nameCN']}")
            st.write(f"部位: {current_exercise['bodyPart']} | 難度: {current_exercise['difficulty']}")
        
        with col3:
            st.metric("組", st.session_state.workout_progress.get("sets", 1))
            st.metric("次", st.session_state.workout_progress.get("reps", 1))
        
        st.write("---")
        
        st.write("**執行技巧**:")
        for tip in current_exercise["tips"]:
            st.write(f"✅ {tip}")
        
        st.write("---")
        
        # 休息計時器
        col_timer = st.columns(1)[0]
        with col_timer:
            st.subheader(f"⏱️ 組間休息計時: {current_exercise['restSeconds']} 秒")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("⏭️ 跳過動作", use_container_width=True):
                st.session_state.workout_progress["current_exercise"] = current_index + 1
                st.session_state.workout_progress["sets"] = 1
                st.session_state.workout_progress["reps"] = 1
                st.rerun()
        
        with col2:
            if st.button("✅ 完成一次", use_container_width=True):
                current_reps = st.session_state.workout_progress.get("reps", 1)
                max_reps = current_exercise["reps"]
                
                if current_reps < max_reps:
                    st.session_state.workout_progress["reps"] = current_reps + 1
                    st.success(f"✅ 完成第 {current_reps} 次")
                else:
                    current_sets = st.session_state.workout_progress.get("sets", 1)
                    if current_sets < current_exercise["sets"]:
                        st.session_state.workout_progress["sets"] = current_sets + 1
                        st.session_state.workout_progress["reps"] = 1
                        st.info(f"✅ 組間休息 {current_exercise['restSeconds']} 秒，準備好按『完成一次』開始下一組")
                    else:
                        st.session_state.workout_progress["current_exercise"] = current_index + 1
                        st.session_state.workout_progress["sets"] = 1
                        st.session_state.workout_progress["reps"] = 1
                        st.success(f"🎉 {current_exercise['nameCN']} 完成！進入下一個動作")
                
                st.rerun()
        
        with col3:
            if st.button("⏹️ 結束訓練", use_container_width=True):
                duration = int((datetime.now() - workout["start_time"]).total_seconds() / 60)
                save_workout_record(workout["exercises"], duration)
                st.session_state.current_workout = None
                st.session_state.workout_progress = {}
                st.session_state.current_page = "統計"
                st.success(f"✅ 訓練完成！耗時 {duration} 分鐘")
                st.balloons()
                st.rerun()
    else:
        # 训练完成
        st.success("🎉 訓練完成！")
        duration = int((datetime.now() - workout["start_time"]).total_seconds() / 60)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("動作完成", len(workout["exercises"]))
        with col2:
            st.metric("訓練時長", f"{duration} 分鐘")
        with col3:
            st.metric("預估熱量", f"{duration * 7}")
        
        if st.button("返回首頁"):
            st.session_state.current_page = "首頁"
            st.rerun()

# ==================== 页面 5: 动作詳情 ====================

def page_exercise_detail():
    if not st.session_state.selected_exercise:
        st.error("沒有選擇動作")
        return
    
    exercise = st.session_state.selected_exercise
    
    st.title(f"{exercise['icon']} {exercise['nameCN']} - 詳細說明")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**英文名稱**: {exercise['name']}")
        st.write(f"**目標部位**: {exercise['bodyPart']}")
        st.write(f"**難度**: {exercise['difficulty']}")
        st.write(f"**推薦**: {exercise['sets']}組 × {exercise['reps']}次")
    
    with col2:
        st.write(f"**模式**: {exercise['mode']}")
        st.write(f"**休息時間**: {exercise['restSeconds']}秒")
        st.write(f"**描述**: {exercise['description']}")
    
    st.write("---")
    
    st.subheader("執行步驟")
    st.write(exercise['description'])
    
    st.subheader("✅ 執行技巧")
    for i, tip in enumerate(exercise["tips"], 1):
        st.write(f"{i}. {tip}")
    
    st.subheader("❌ 常見錯誤")
    for i, mistake in enumerate(exercise["mistakes"], 1):
        st.write(f"{i}. {mistake}")
    
    st.write("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📺 查看 YouTube 教學", use_container_width=True):
            st.session_state.current_page = "YouTube教學"
            st.rerun()
    
    with col2:
        if st.button("⬅️ 返回", use_container_width=True):
            st.session_state.current_page = "動作庫"
            st.rerun()

# ==================== 页面 6: 统计 ====================

def page_statistics():
    st.title("📊 訓練統計")
    
    if not st.session_state.workout_records:
        st.info("還沒有訓練記錄，開始你的第一次訓練吧！")
        return
    
    records = st.session_state.workout_records
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("訓練次數", len(records))
    
    with col2:
        total_minutes = sum(r["duration"] for r in records)
        st.metric("總訓練時長", f"{total_minutes} 分鐘")
    
    with col3:
        total_calories = sum(r["calories"] for r in records)
        st.metric("預估熱量", f"{total_calories}")
    
    st.write("---")
    
    st.subheader("訓練歷史")
    
    # 创建数据框
    records_data = []
    for record in reversed(records):
        records_data.append({
            "日期": record["date"],
            "動作數": len(record["exercises"]),
            "時長 (分)": record["duration"],
            "熱量": record["calories"],
            "動作": ", ".join(record["exercises"][:3]) + ("..." if len(record["exercises"]) > 3 else "")
        })
    
    df = pd.DataFrame(records_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ==================== 页面 7: 设置 ====================

def page_settings():
    st.title("⚙️ 設置")
    
    st.subheader("👤 個人信息")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("姓名", value=st.session_state.user_data["name"])
        st.session_state.user_data["name"] = name
    
    with col2:
        age = st.slider("年齡", 15, 100, st.session_state.user_data["age"])
        st.session_state.user_data["age"] = age
    
    st.write("---")
    
    st.subheader("🏋️ 訓練偏好")
    
    col1, col2 = st.columns(2)
    
    with col1:
        mode = st.selectbox("訓練模式", ["徒手", "健身房"], 
                           index=0 if st.session_state.user_data["mode"] == "徒手" else 1)
        st.session_state.user_data["mode"] = mode
    
    with col2:
        experience = st.selectbox("經驗水平", ["初級", "中級", "高級"],
                                 index=["初級", "中級", "高級"].index(st.session_state.user_data["experience"]))
        st.session_state.user_data["experience"] = experience
    
    st.write("---")
    
    st.subheader("ℹ️ 關於應用")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("應用版本", "3.0.0")
    
    with col2:
        st.metric("動作庫", f"{len(EXERCISES)} 個動作")
    
    with col3:
        st.metric("訓練記錄", len(st.session_state.workout_records))
    
    st.write("---")
    
    st.success("✨ v3.0 新功能已上線！")
    st.markdown("""
    ✅ 50+ 完整動作庫  
    ✅ 真正的計數系統  
    ✅ 嵌入式 YouTube 教學  
    ✅ 完整的動作詳情頁面  
    ✅ 健身房 vs 徒手區分  
    """)
    
    if st.button("💾 保存設置", use_container_width=True):
        st.success("✅ 設置已保存")

# ==================== 主程序 ====================

def main():
    # 侧边栏导航
    with st.sidebar:
        st.title("💪 SmartFit")
        st.write("**v3.0** - 完整版本")
        
        pages = ["首頁", "動作庫", "訓練執行", "動作詳情", "YouTube教學", "統計", "設置"]
        
        if st.session_state.current_page not in pages:
            st.session_state.current_page = "首頁"
        
        selected_page = st.radio("選擇頁面", pages, 
                                key="nav",
                                label_visibility="collapsed",
                                index=pages.index(st.session_state.current_page) if st.session_state.current_page in pages else 0)
        
        st.session_state.current_page = selected_page
        
        st.write("---")
        
        if st.session_state.user_data["name"]:
            st.write(f"👤 {st.session_state.user_data['name']}")
            st.write(f"📅 年齡: {st.session_state.user_data['age']}")
            st.write(f"🏋️ 模式: {st.session_state.user_data['mode']}")
        
        st.write("---")
        
        st.markdown("### 📝 本版本改進：")
        st.markdown("""
        ✅ 50+ 動作  
        ✅ 完整計數系統  
        ✅ YouTube 嵌入  
        ✅ 詳情頁面  
        ✅ 健身房區分
        """)
    
    # 根据当前页面显示内容
    if st.session_state.current_page == "首頁":
        page_home()
    elif st.session_state.current_page == "動作庫":
        page_exercise_list()
    elif st.session_state.current_page == "訓練執行":
        page_workout_execution()
    elif st.session_state.current_page == "動作詳情":
        page_exercise_detail()
    elif st.session_state.current_page == "YouTube教學":
        page_youtube()
    elif st.session_state.current_page == "統計":
        page_statistics()
    elif st.session_state.current_page == "設置":
        page_settings()

if __name__ == "__main__":
    main()
