import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="SmartFit", page_icon="💪", layout="wide")

st.markdown("""<style>
.exercise-card {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
padding: 15px; border-radius: 12px; margin: 10px 0; color: white;}
</style>""", unsafe_allow_html=True)

# ==================== 50個動作 - 健身房限定器材 ====================
EXERCISES = [
    # 徒手 - 胸部
    {"id": "001", "nameCN": "俯臥撑", "bodyPart": "胸部", "difficulty": "初級", "sets": 3, "reps": 12, "mode": "徒手", "icon": "🏋️", "image": "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=600&h=400&fit=crop", "equipment": "無", "tips": ["保持身體直線", "降低至胸部", "推回起始位置"]},
    {"id": "002", "nameCN": "寬距俯臥撑", "bodyPart": "胸部", "difficulty": "初級", "sets": 3, "reps": 10, "mode": "徒手", "icon": "🏋️", "image": "https://images.unsplash.com/photo-1552072092-74b88bb57967?w=600&h=400&fit=crop", "equipment": "無", "tips": ["雙手寬距", "保持直線", "完整範圍"]},
    {"id": "003", "nameCN": "菱形俯臥撑", "bodyPart": "胸部", "difficulty": "中級", "sets": 3, "reps": 8, "mode": "徒手", "icon": "💎", "image": "https://images.unsplash.com/photo-1549960110-cb953e50b5a0?w=600&h=400&fit=crop", "equipment": "無", "tips": ["雙手在胸下", "肘部靠近", "完全伸展"]},
    {"id": "004", "nameCN": "下斜俯臥撑", "bodyPart": "胸部", "difficulty": "中級", "sets": 3, "reps": 10, "mode": "徒手", "icon": "⬇️", "image": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=600&h=400&fit=crop", "equipment": "無", "tips": ["雙腳放高", "身體直線", "完整動作"]},
    {"id": "005", "nameCN": "箭手俯臥撑", "bodyPart": "胸部", "difficulty": "高級", "sets": 3, "reps": 6, "mode": "徒手", "icon": "🏹", "image": "https://images.unsplash.com/photo-1595909496304-da811f5ec6ff?w=600&h=400&fit=crop", "equipment": "無", "tips": ["一側彎曲", "一側伸直", "平衡訓練"]},

    # 徒手 - 背部
    {"id": "006", "nameCN": "引體向上", "bodyPart": "背部", "difficulty": "中級", "sets": 3, "reps": 8, "mode": "徒手", "icon": "💪", "image": "https://images.unsplash.com/photo-1623924157356-a1be4ad71fda?w=600&h=400&fit=crop", "equipment": "無", "tips": ["握距寬", "下巴超杆", "控制下降"]},
    {"id": "007", "nameCN": "窄握引體", "bodyPart": "背部", "difficulty": "中級", "sets": 3, "reps": 8, "mode": "徒手", "icon": "🤸", "image": "https://images.unsplash.com/photo-1590721741760-f2e67dab3d0d?w=600&h=400&fit=crop", "equipment": "無", "tips": ["掌心向內", "肘部靠近", "平順動作"]},
    {"id": "008", "nameCN": "反向划船", "bodyPart": "背部", "difficulty": "初級", "sets": 3, "reps": 12, "mode": "徒手", "icon": "🔄", "image": "https://images.unsplash.com/photo-1608287061620-e1401b515a78?w=600&h=400&fit=crop", "equipment": "無", "tips": ["身體直線", "拉至胸部", "控制下降"]},
    {"id": "009", "nameCN": "超人式", "bodyPart": "背部", "difficulty": "初級", "sets": 3, "reps": 30, "mode": "徒手", "icon": "🦸", "image": "https://images.unsplash.com/photo-1589426662646-4a8bc1edc42b?w=600&h=400&fit=crop", "equipment": "無", "tips": ["手臂前伸", "腿後伸", "胸部離地"]},
    {"id": "010", "nameCN": "肩胛骨拉", "bodyPart": "背部", "difficulty": "初級", "sets": 3, "reps": 10, "mode": "徒手", "icon": "⬆️", "image": "https://images.unsplash.com/photo-1593693411088-f1344a4e0fdf?w=600&h=400&fit=crop", "equipment": "無", "tips": ["背部拉", "手臂不彎", "小幅動作"]},

    # 徒手 - 腿部
    {"id": "011", "nameCN": "深蹲", "bodyPart": "腿部", "difficulty": "初級", "sets": 3, "reps": 15, "mode": "徒手", "icon": "🦵", "image": "https://images.unsplash.com/photo-1599058917212-d217cde485da?w=600&h=400&fit=crop", "equipment": "無", "tips": ["挺胸", "臀部後坐", "腳跟推起"]},
    {"id": "012", "nameCN": "跳躍深蹲", "bodyPart": "腿部", "difficulty": "中級", "sets": 3, "reps": 12, "mode": "徒手", "icon": "⬆️", "image": "https://images.unsplash.com/photo-1594381898348-846ce150fbbb?w=600&h=400&fit=crop", "equipment": "無", "tips": ["全力跳", "軟著陸", "快速起身"]},
    {"id": "013", "nameCN": "弓步", "bodyPart": "腿部", "difficulty": "初級", "sets": 3, "reps": 12, "mode": "徒手", "icon": "🚶", "image": "https://images.unsplash.com/photo-1616092785832-8e1a08c99e64?w=600&h=400&fit=crop", "equipment": "無", "tips": ["前腳90度", "後腳接地", "保持直立"]},
    {"id": "014", "nameCN": "單腿深蹲", "bodyPart": "腿部", "difficulty": "高級", "sets": 3, "reps": 5, "mode": "徒手", "icon": "🦵", "image": "https://images.unsplash.com/photo-1586766338604-2d8cdd982a6c?w=600&h=400&fit=crop", "equipment": "無", "tips": ["一腳懸空", "保持平衡", "完整深蹲"]},
    {"id": "015", "nameCN": "提踵", "bodyPart": "腿部", "difficulty": "初級", "sets": 3, "reps": 20, "mode": "徒手", "icon": "👟", "image": "https://images.unsplash.com/photo-1571731828596-b01e949c8e6a?w=600&h=400&fit=crop", "equipment": "無", "tips": ["站直", "提起腳跟", "控制下降"]},

    # 徒手 - 核心
    {"id": "016", "nameCN": "棒式", "bodyPart": "核心", "difficulty": "初級", "sets": 3, "reps": 30, "mode": "徒手", "icon": "📍", "image": "https://images.unsplash.com/photo-1598971457318-b345dd953d3f?w=600&h=400&fit=crop", "equipment": "無", "tips": ["身體直線", "核心緊縮", "臀部不下沉"]},
    {"id": "017", "nameCN": "側棒式", "bodyPart": "核心", "difficulty": "初級", "sets": 3, "reps": 20, "mode": "徒手", "icon": "◀️", "image": "https://images.unsplash.com/photo-1608287061620-e1401b515a78?w=600&h=400&fit=crop", "equipment": "無", "tips": ["身體直線", "核心收緊", "臀部不下沉"]},
    {"id": "018", "nameCN": "仰臥起坐", "bodyPart": "核心", "difficulty": "初級", "sets": 3, "reps": 15, "mode": "徒手", "icon": "⬆️", "image": "https://images.unsplash.com/photo-1605296867424-35fc241ee099?w=600&h=400&fit=crop", "equipment": "無", "tips": ["膝蓋彎曲", "不拉脖子", "胸部向膝"]},
    {"id": "019", "nameCN": "爬山者", "bodyPart": "核心", "difficulty": "中級", "sets": 3, "reps": 20, "mode": "徒手", "icon": "🏔️", "image": "https://images.unsplash.com/photo-1588444784947-7873f6fbf9a7?w=600&h=400&fit=crop", "equipment": "無", "tips": ["快速交替", "保持俯臥撑", "核心緊縮"]},
    {"id": "020", "nameCN": "抬腿", "bodyPart": "核心", "difficulty": "初級", "sets": 3, "reps": 12, "mode": "徒手", "icon": "🦵", "image": "https://images.unsplash.com/photo-1614289371518-722f2b8c4979?w=600&h=400&fit=crop", "equipment": "無", "tips": ["背部貼地", "腿部直", "控制速度"]},

    # 健身房 - 胸部
    {"id": "021", "nameCN": "啞鈴臥推", "bodyPart": "胸部", "difficulty": "中級", "sets": 4, "reps": 10, "mode": "健身房", "icon": "🏋️", "image": "https://images.unsplash.com/photo-1575831372957-821eea258ca2?w=600&h=400&fit=crop", "equipment": "啞鈴", "tips": ["啞鈴至胸", "爆發推起", "控制下降"]},
    {"id": "022", "nameCN": "槓鈴臥推", "bodyPart": "胸部", "difficulty": "中級", "sets": 4, "reps": 8, "mode": "健身房", "icon": "⬆️", "image": "https://images.unsplash.com/photo-1505886637051-465fda13b650?w=600&h=400&fit=crop", "equipment": "槓鈴", "tips": ["背貼板", "肩膀穩定", "平順動作"]},
    {"id": "023", "nameCN": "胸部推蹬機", "bodyPart": "胸部", "difficulty": "初級", "sets": 3, "reps": 12, "mode": "健身房", "icon": "🎯", "image": "https://images.unsplash.com/photo-1574480611857-e80fcf6a9c9d?w=600&h=400&fit=crop", "equipment": "推蹬機", "tips": ["坐直對齊", "完全推出", "控制回放"]},
    {"id": "024", "nameCN": "拉力機夾胸", "bodyPart": "胸部", "difficulty": "中級", "sets": 3, "reps": 12, "mode": "健身房", "icon": "🔗", "image": "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=600&h=400&fit=crop", "equipment": "拉力機", "tips": ["手臂微彎", "控制回放", "集中收縮"]},
    {"id": "025", "nameCN": "史密斯機臥推", "bodyPart": "胸部", "difficulty": "初級", "sets": 4, "reps": 12, "mode": "健身房", "icon": "📐", "image": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=600&h=400&fit=crop", "equipment": "史密斯機", "tips": ["槓在肩", "直線下降", "完整動作"]},

    # 健身房 - 背部
    {"id": "026", "nameCN": "下拉機", "bodyPart": "背部", "difficulty": "初級", "sets": 3, "reps": 12, "mode": "健身房", "icon": "⬇️", "image": "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=600&h=400&fit=crop", "equipment": "下拉機", "tips": ["拉至胸", "控制回放", "核心緊縮"]},
    {"id": "027", "nameCN": "拉力機划船", "bodyPart": "背部", "difficulty": "初級", "sets": 4, "reps": 12, "mode": "健身房", "icon": "🔗", "image": "https://images.unsplash.com/photo-1581003829941-3cce02241e8d?w=600&h=400&fit=crop", "equipment": "拉力機", "tips": ["坐直挺胸", "拉至腹", "控制回放"]},
    {"id": "028", "nameCN": "槓鈴划船", "bodyPart": "背部", "difficulty": "中級", "sets": 4, "reps": 8, "mode": "健身房", "icon": "💪", "image": "https://images.unsplash.com/photo-1534367519131-fe8f84d1c9b0?w=600&h=400&fit=crop", "equipment": "槓鈴", "tips": ["膝蓋微彎", "背部直", "拉至腹"]},
    {"id": "029", "nameCN": "啞鈴划船", "bodyPart": "背部", "difficulty": "中級", "sets": 4, "reps": 10, "mode": "健身房", "icon": "💪", "image": "https://images.unsplash.com/photo-1574289603b67b16f032dc535e75271ce51ce28df?w=600&h=400&fit=crop", "equipment": "啞鈴", "tips": ["膝蓋跪", "核心穩定", "拉至腰"]},
    {"id": "030", "nameCN": "T槓划船", "bodyPart": "背部", "difficulty": "中級", "sets": 4, "reps": 10, "mode": "健身房", "icon": "📍", "image": "https://images.unsplash.com/photo-1517836357463-d25ddfcbf042?w=600&h=400&fit=crop", "equipment": "T槓", "tips": ["身體穩定", "拉至胸", "控制下降"]},

    # 健身房 - 肩膀
    {"id": "031", "nameCN": "啞鈴肩推", "bodyPart": "肩膀", "difficulty": "中級", "sets": 3, "reps": 12, "mode": "健身房", "icon": "⬆️", "image": "https://images.unsplash.com/photo-1567016432779-094069f00d4b?w=600&h=400&fit=crop", "equipment": "啞鈴", "tips": ["啞啞至肩", "上推至頂", "控制下降"]},
    {"id": "032", "nameCN": "側平舉", "bodyPart": "肩膀", "difficulty": "初級", "sets": 3, "reps": 12, "mode": "健身房", "icon": "➡️", "image": "https://images.unsplash.com/photo-1599058917212-d217cde485da?w=600&h=400&fit=crop", "equipment": "啞鈴", "tips": ["手臂微彎", "抬至肩高", "控制速度"]},
    {"id": "033", "nameCN": "前平舉", "bodyPart": "肩膀", "difficulty": "初級", "sets": 3, "reps": 12, "mode": "健身房", "icon": "📤", "image": "https://images.unsplash.com/photo-1596357614634-fac73f9b37dd?w=600&h=400&fit=crop", "equipment": "啞鈴", "tips": ["手臂微彎", "抬至肩高", "緩慢上下"]},
    {"id": "034", "nameCN": "反向夾胸機", "bodyPart": "肩膀", "difficulty": "初級", "sets": 3, "reps": 12, "mode": "健身房", "icon": "🔄", "image": "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=600&h=400&fit=crop", "equipment": "夾胸機", "tips": ["坐直", "手臂向外", "控制回放"]},
    {"id": "035", "nameCN": "聳肩", "bodyPart": "肩膀", "difficulty": "初級", "sets": 3, "reps": 15, "mode": "健身房", "icon": "⬆️", "image": "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=600&h=400&fit=crop", "equipment": "啞鈴", "tips": ["聳至耳朵", "停頓一秒", "緩慢下降"]},

    # 健身房 - 手臂
    {"id": "036", "nameCN": "啞鈴彎舉", "bodyPart": "手臂", "difficulty": "初級", "sets": 3, "reps": 12, "mode": "健身房", "icon": "💪", "image": "https://images.unsplash.com/photo-1570829477519-40735bb7385f?w=600&h=400&fit=crop", "equipment": "啞鈴", "tips": ["靠牆穩定", "前臂動", "充分收縮"]},
    {"id": "037", "nameCN": "三頭撐體機", "bodyPart": "手臂", "difficulty": "初級", "sets": 3, "reps": 12, "mode": "健身房", "icon": "⬇️", "image": "https://images.unsplash.com/photo-1574289603b67b16f032dc535e75271ce51ce28df?w=600&h=400&fit=crop", "equipment": "撐體機", "tips": ["身體向前", "肘部90度", "三頭推起"]},
    {"id": "038", "nameCN": "繩索下壓", "bodyPart": "手臂", "difficulty": "初級", "sets": 3, "reps": 12, "mode": "健身房", "icon": "🔗", "image": "https://images.unsplash.com/photo-1578262996442-48f60103fc96?w=600&h=400&fit=crop", "equipment": "拉力機", "tips": ["肘部不動", "完全伸展", "控制回放"]},
    {"id": "039", "nameCN": "錘式彎舉", "bodyPart": "手臂", "difficulty": "初級", "sets": 3, "reps": 12, "mode": "健身房", "icon": "🔨", "image": "https://images.unsplash.com/photo-1595909496304-da811f5ec6ff?w=600&h=400&fit=crop", "equipment": "啞鈴", "tips": ["掌心相對", "前臂動", "控制速度"]},
    {"id": "040", "nameCN": "拉力機彎舉", "bodyPart": "手臂", "difficulty": "初級", "sets": 3, "reps": 12, "mode": "健身房", "icon": "🔗", "image": "https://images.unsplash.com/photo-1581003829941-3cce02241e8d?w=600&h=400&fit=crop", "equipment": "拉力機", "tips": ["肘部固定", "張力持續", "控制回放"]},

    # 健身房 - 腿部
    {"id": "041", "nameCN": "推蹬機", "bodyPart": "腿部", "difficulty": "初級", "sets": 3, "reps": 15, "mode": "健身房", "icon": "🚀", "image": "https://images.unsplash.com/photo-1574127134224-f6b0ff6f8b83?w=600&h=400&fit=crop", "equipment": "推蹬機", "tips": ["腳在機器", "完全伸展", "控制下降"]},
    {"id": "042", "nameCN": "腿部卷舉", "bodyPart": "腿部", "difficulty": "初級", "sets": 3, "reps": 12, "mode": "健身房", "icon": "↪️", "image": "https://images.unsplash.com/photo-1584735730920-3d78b99baed6?w=600&h=400&fit=crop", "equipment": "卷舉機", "tips": ["坐直", "卷至胸", "控制回放"]},
    {"id": "043", "nameCN": "腿部伸展", "bodyPart": "腿部", "difficulty": "初級", "sets": 3, "reps": 12, "mode": "健身房", "icon": "⬆️", "image": "https://images.unsplash.com/photo-1582266945968-55b56f96abbb?w=600&h=400&fit=crop", "equipment": "伸展機", "tips": ["坐直", "完全伸展", "控制回放"]},
    {"id": "044", "nameCN": "哈克深蹲", "bodyPart": "腿部", "difficulty": "中級", "sets": 3, "reps": 12, "mode": "健身房", "icon": "📍", "image": "https://images.unsplash.com/photo-1612136122212-99b3978d6eaa?w=600&h=400&fit=crop", "equipment": "哈克機", "tips": ["肩膀靠機", "深蹲至平行", "完整動作"]},
    {"id": "045", "nameCN": "槓鈴深蹲", "bodyPart": "腿部", "difficulty": "中級", "sets": 4, "reps": 8, "mode": "健身房", "icon": "⬇️", "image": "https://images.unsplash.com/photo-1546483328-2716635f7fa8?w=600&h=400&fit=crop", "equipment": "槓鈴", "tips": ["槓在肩", "直立姿勢", "深蹲至平行"]},

    # 健身房 - 核心
    {"id": "046", "nameCN": "拉力卷腹", "bodyPart": "核心", "difficulty": "初級", "sets": 3, "reps": 12, "mode": "健身房", "icon": "🔗", "image": "https://images.unsplash.com/photo-1598971457318-b345dd953d3f?w=600&h=400&fit=crop", "equipment": "拉力機", "tips": ["膝蓋彎", "卷至膝", "控制回放"]},
    {"id": "047", "nameCN": "滑輪卷腹", "bodyPart": "核心", "difficulty": "中級", "sets": 3, "reps": 10, "mode": "健身房", "icon": "⭕", "image": "https://images.unsplash.com/photo-1588444784947-7873f6fbf9a7?w=600&h=400&fit=crop", "equipment": "滑輪", "tips": ["膝蓋跪", "向前滾", "回收縮腹"]},
    {"id": "048", "nameCN": "負重棒式", "bodyPart": "核心", "difficulty": "中級", "sets": 3, "reps": 30, "mode": "健身房", "icon": "🦺", "image": "https://images.unsplash.com/photo-1598971457318-b345dd953d3f?w=600&h=400&fit=crop", "equipment": "背心", "tips": ["穿背心", "保持直線", "全程緊縮"]},
    {"id": "049", "nameCN": "機械卷腹", "bodyPart": "核心", "difficulty": "初級", "sets": 3, "reps": 12, "mode": "健身房", "icon": "🎯", "image": "https://images.unsplash.com/photo-1612122234789-86c5e40e1a20?w=600&h=400&fit=crop", "equipment": "卷腹機", "tips": ["坐直對齊", "卷起完整", "控制回放"]},
    {"id": "050", "nameCN": "懸掛抬腿", "bodyPart": "核心", "difficulty": "中級", "sets": 3, "reps": 10, "mode": "健身房", "icon": "🏃", "image": "https://images.unsplash.com/photo-1614289371518-722f2b8c4979?w=600&h=400&fit=crop", "equipment": "單槓", "tips": ["握把", "腿抬至水平", "控制下降"]},
]

BODY_PARTS = ["胸部", "背部", "肩膀", "手臂", "腿部", "核心"]
EQUIPMENT = ["啞鈴", "槓鈴", "推蹬機", "下拉機", "拉力機", "史密斯機", "卷舉機", "伸展機", "哈克機", "夾胸機", "撐體機", "滑輪", "背心", "卷腹機", "單槓", "T槓"]

# ==================== Session State ====================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "user" not in st.session_state:
    st.session_state.user = {"name": "", "age": 25, "mode": "徒手"}
if "records" not in st.session_state:
    st.session_state.records = []
if "workout" not in st.session_state:
    st.session_state.workout = None
if "current_ex" not in st.session_state:
    st.session_state.current_ex = None
if "progress" not in st.session_state:
    st.session_state.progress = {"ex_idx": 0, "sets": 1, "reps": 1}
if "selected_exercises" not in st.session_state:
    st.session_state.selected_exercises = []
if "selected_equipment" not in st.session_state:
    st.session_state.selected_equipment = []

# ==================== 函數 ====================
def get_exercises(body_parts, mode, equipment=None):
    exs = [e for e in EXERCISES if e["mode"] == mode and e["bodyPart"] in body_parts]
    if equipment and mode == "健身房":
        exs = [e for e in exs if e["equipment"] in equipment]
    return exs

# ==================== 側邊欄 ====================
with st.sidebar:
    st.title("💪 SmartFit v5.2")
    if st.button("🏠 首頁", use_container_width=True, key="nav_home"):
        st.session_state.page = "home"
        st.rerun()
    if st.button("📊 統計", use_container_width=True, key="nav_stats"):
        st.session_state.page = "stats"
        st.rerun()
    if st.button("⚙️ 設置", use_container_width=True, key="nav_settings"):
        st.session_state.page = "settings"
        st.rerun()
    st.write("---")
    st.info(f"✨ 50個真實圖片動作\n📱 徒手: 20個\n🏋️ 健身房: 30個")

# ==================== 首頁 ====================
if st.session_state.page == "home":
    st.title("💪 SmartFit - 您的私人健身教練")
    
    col1, col2 = st.columns(2)
    with col1:
        mode = st.radio("訓練模式", ["🏠 徒手", "🏋️ 健身房"], key="mode_select")
        st.session_state.user["mode"] = "徒手" if "徒手" in mode else "健身房"
    with col2:
        duration = st.radio("訓練時長", [15, 30, 45, 60], horizontal=True, key="duration_select")
    
    st.divider()
    
    # 健身房選擇器材
    selected_equipment = []
    if st.session_state.user["mode"] == "健身房":
        st.subheader("🏋️ 選擇可用的器材")
        cols = st.columns(4)
        for i, equip in enumerate(EQUIPMENT):
            with cols[i % 4]:
                if st.checkbox(equip, key=f"equip_{equip}"):
                    selected_equipment.append(equip)
        st.session_state.selected_equipment = selected_equipment
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
        
        all_exercises = get_exercises(selected_parts, st.session_state.user["mode"], selected_equipment if selected_equipment else None)
        
        if all_exercises:
            st.subheader(f"🏆 可用動作 ({len(all_exercises)}個) - 請選擇要訓練的動作")
            
            st.session_state.selected_exercises = []
            
            for ex in all_exercises:
                col1, col2, col3, col4 = st.columns([1.5, 1, 0.8, 1.2])
                with col1:
                    st.write(f"**{ex['nameCN']}** ({ex['difficulty']})")
                    st.caption(f"器材: {ex['equipment']}")
                with col2:
                    if st.checkbox("選擇", key=f"select_{ex['id']}"):
                        if ex not in st.session_state.selected_exercises:
                            st.session_state.selected_exercises.append(ex)
                with col3:
                    st.write(f"{ex['sets']}×{ex['reps']}")
                with col4:
                    if st.button("👀", key=f"btn_detail_{ex['id']}", help="查看詳情和圖片"):
                        st.session_state.current_ex = ex
                        st.session_state.page = "detail"
                        st.rerun()
            
            st.divider()
            
            if st.session_state.selected_exercises:
                st.success(f"✅ 已選擇 {len(st.session_state.selected_exercises)} 個動作")
                if st.button("🎬 開始訓練", use_container_width=True, key="btn_start"):
                    st.session_state.workout = {"exercises": st.session_state.selected_exercises, "start": datetime.now(), "duration": duration}
                    st.session_state.progress = {"ex_idx": 0, "sets": 1, "reps": 1}
                    st.session_state.page = "workout"
                    st.rerun()
            else:
                st.info("👈 請先選擇要訓練的動作")
        else:
            st.warning(f"沒有找到相符的動作")

# ==================== 動作詳情 ====================
elif st.session_state.page == "detail":
    if st.session_state.current_ex:
        ex = st.session_state.current_ex
        st.title(f"{ex['nameCN']}")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.write(f"**難度**: {ex['difficulty']} | **部位**: {ex['bodyPart']}")
            st.write(f"**推薦**: {ex['sets']}×{ex['reps']} | **器材**: {ex['equipment']}")
            st.subheader("✅ 執行技巧")
            for tip in ex["tips"]:
                st.write(f"• {tip}")
        with col2:
            st.write("**動作圖示：**")
            st.image(ex['image'], use_column_width=True)
        
        if st.button("⬅️ 返回首頁"):
            st.session_state.page = "home"
            st.rerun()

# ==================== 訓練執行 ====================
elif st.session_state.page == "workout":
    if st.session_state.workout:
        exs = st.session_state.workout["exercises"]
        prog = st.session_state.progress
        idx = prog["ex_idx"]
        
        st.progress(idx / len(exs) if len(exs) > 0 else 0, text=f"進度: {idx}/{len(exs)}")
        
        if idx < len(exs):
            ex = exs[idx]
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.title(f"{ex['nameCN']}")
                st.write(f"部位: {ex['bodyPart']} | 難度: {ex['difficulty']}")
                st.write(f"器材: {ex['equipment']}")
            with col2:
                st.image(ex['image'], use_column_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("組", prog["sets"])
            with col2:
                st.metric("次", prog["reps"])
            
            st.divider()
            st.subheader("執行技巧:")
            for tip in ex["tips"]:
                st.write(f"✅ {tip}")
            
            st.divider()
            c1, c2, c3 = st.columns(3)
            
            with c1:
                if st.button("⏭️ 跳過", use_container_width=True, key="btn_skip"):
                    st.session_state.progress["ex_idx"] += 1
                    st.session_state.progress["sets"] = 1
                    st.session_state.progress["reps"] = 1
                    st.rerun()
            
            with c2:
                if st.button("✅ 完成一次", use_container_width=True, key="btn_done"):
                    if prog["reps"] < ex["reps"]:
                        st.session_state.progress["reps"] += 1
                    else:
                        if prog["sets"] < ex["sets"]:
                            st.session_state.progress["sets"] += 1
                            st.session_state.progress["reps"] = 1
                        else:
                            st.session_state.progress["ex_idx"] += 1
                            st.session_state.progress["sets"] = 1
                            st.session_state.progress["reps"] = 1
                    st.rerun()
            
            with c3:
                if st.button("⏹️ 結束", use_container_width=True, key="btn_finish"):
                    dur = int((datetime.now() - st.session_state.workout["start"]).total_seconds() / 60)
                    st.session_state.records.append({
                        "日期": datetime.now().strftime("%Y-%m-%d"),
                        "動作": len(exs),
                        "時長(分)": dur,
                        "熱量": dur * 7
                    })
                    st.session_state.workout = None
                    st.session_state.page = "stats"
                    st.balloons()
                    st.rerun()
        else:
            st.success("🎉 訓練完成！")
            dur = int((datetime.now() - st.session_state.workout["start"]).total_seconds() / 60)
            c1, c2, c3 = st.columns(3)
            c1.metric("動作", len(exs))
            c2.metric("時長", f"{dur}分")
            c3.metric("熱量", dur * 7)

# ==================== 統計 ====================
elif st.session_state.page == "stats":
    st.title("📊 訓練統計")
    if st.session_state.records:
        df = pd.DataFrame(st.session_state.records)
        c1, c2, c3 = st.columns(3)
        c1.metric("訓練次", len(st.session_state.records))
        c2.metric("總時長", f"{df['時長(分)'].sum()}分")
        c3.metric("總熱量", df['熱量'].sum())
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("還沒有訓練記錄")

# ==================== 設置 ====================
elif st.session_state.page == "settings":
    st.title("⚙️ 設置")
    st.session_state.user["name"] = st.text_input("姓名", st.session_state.user["name"])
    st.session_state.user["age"] = st.slider("年齡", 15, 100, st.session_state.user["age"])
    c1, c2, c3 = st.columns(3)
    c1.metric("版本", "5.2")
    c2.metric("動作", len(EXERCISES))
    c3.metric("記錄", len(st.session_state.records))
