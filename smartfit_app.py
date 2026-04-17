import streamlit as st
import json
from datetime import datetime
import pandas as pd
from pathlib import Path

# 页面配置
st.set_page_config(
    page_title="SmartFit 健身 APP",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS
st.markdown("""
<style>
    .main {
        padding: 0rem 0rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .exercise-card {
        background-color: #e8f4f8;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #1f77b4;
    }
    .success-card {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 数据模型 ====================

EXERCISES = [
    {
        "id": "001",
        "name": "Push-ups",
        "nameCN": "俯臥撑",
        "bodyPart": "胸部",
        "difficulty": "初級",
        "sets": 3,
        "reps": 12,
        "restSeconds": 60,
        "description": "經典的徒手胸部訓練動作",
        "tips": ["保持身體成一直線", "降低身體直到胸部接近地面", "推回起始位置"],
        "mistakes": ["臀部下沉", "肘部張得太開", "活動範圍不足"]
    },
    {
        "id": "002",
        "name": "Squats",
        "nameCN": "深蹲",
        "bodyPart": "腿部",
        "difficulty": "初級",
        "sets": 3,
        "reps": 15,
        "restSeconds": 90,
        "description": "下身訓練的基礎動作",
        "tips": ["挺胸保持核心緊縮", "臀部向後向下移動", "通過腳跟推起"],
        "mistakes": ["膝蓋內扣", "身體向前傾斜過多", "深度不夠"]
    },
    {
        "id": "003",
        "name": "Pull-ups",
        "nameCN": "引體向上",
        "bodyPart": "背部",
        "difficulty": "中級",
        "sets": 3,
        "reps": 8,
        "restSeconds": 120,
        "description": "上身拉力訓練",
        "tips": ["握距略寬於肩膀", "下巴超過橫杆", "控制下降"],
        "mistakes": ["活動範圍不足", "使用衝力", "肘部張得太開"]
    },
    {
        "id": "004",
        "name": "Plank",
        "nameCN": "棒式",
        "bodyPart": "核心",
        "difficulty": "初級",
        "sets": 3,
        "reps": 30,
        "restSeconds": 60,
        "description": "核心穩定性訓練",
        "tips": ["身體成一直線", "全程核心緊縮", "不要臀部下沉"],
        "mistakes": ["臀部下沉", "頸部過度拉伸", "肩膀過度前傾"]
    },
    {
        "id": "005",
        "name": "Dumbbell Bench Press",
        "nameCN": "啞鈴臥推",
        "bodyPart": "胸部",
        "difficulty": "中級",
        "sets": 4,
        "reps": 10,
        "restSeconds": 90,
        "description": "使用啞鈴的胸部訓練",
        "tips": ["身體呈平板狀", "啞鈴降至胸部", "爆發力推起"],
        "mistakes": ["彈跳重量", "推力不均勻", "肘部貼得太近"]
    },
    {
        "id": "006",
        "name": "Dumbbell Rows",
        "nameCN": "啞鈴划船",
        "bodyPart": "背部",
        "difficulty": "中級",
        "sets": 4,
        "reps": 10,
        "restSeconds": 90,
        "description": "背部划船訓練",
        "tips": ["單膝跪地或側身", "保持核心穩定", "啞鈴拉至腰部"],
        "mistakes": ["轉動身體獲得動力", "不完全收縮", "肩膀過度內收"]
    },
    {
        "id": "007",
        "name": "Shoulder Press",
        "nameCN": "肩推",
        "bodyPart": "肩膀",
        "difficulty": "中級",
        "sets": 3,
        "reps": 12,
        "restSeconds": 60,
        "description": "肩膀推力訓練",
        "tips": ["啞鈴至肩膀高度", "上推至頭頂", "控制下降"],
        "mistakes": ["過度拱腰", "肘部位置不當", "活動不完全"]
    },
    {
        "id": "008",
        "name": "Bicep Curls",
        "nameCN": "二頭肌彎舉",
        "bodyPart": "手臂",
        "difficulty": "初級",
        "sets": 3,
        "reps": 12,
        "restSeconds": 60,
        "description": "二頭肌孤立訓練",
        "tips": ["靠在牆上保持穩定", "只有前臂移動", "充分收縮"],
        "mistakes": ["使用衝力搖晃", "不完全伸展", "肘部移動"]
    },
    {
        "id": "009",
        "name": "Tricep Dips",
        "nameCN": "三頭肌撐體",
        "bodyPart": "手臂",
        "difficulty": "中級",
        "sets": 3,
        "reps": 10,
        "restSeconds": 90,
        "description": "三頭肌訓練動作",
        "tips": ["身體向前稍微傾斜", "肘部彎曲至90度", "通過三頭肌推起"],
        "mistakes": ["向前傾斜太多", "下降不足", "肘部外張太寬"]
    },
    {
        "id": "010",
        "name": "Leg Press",
        "nameCN": "腿部推舉",
        "bodyPart": "腿部",
        "difficulty": "中級",
        "sets": 4,
        "reps": 12,
        "restSeconds": 90,
        "description": "下身力量訓練",
        "tips": ["腳放在肩膀寬度", "完全伸展腿部", "控制下降速度"],
        "mistakes": ["膝蓋超過腳尖", "只做部分動作", "重量過重"]
    }
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

# ==================== 功能函数 ====================

def get_recommended_exercises(body_parts, duration, mode):
    """获取推荐动作"""
    filtered = EXERCISES
    
    # 按身体部位筛选
    filtered = [e for e in filtered if e["bodyPart"] in body_parts]
    
    # 按模式筛选（暂时全部支持）
    
    # 按时长和难度调整
    experience_map = {"初級": "初級", "中級": "中級", "高級": "高級"}
    
    # 返回推荐的动作（限制数量）
    return filtered[:4] if len(filtered) > 4 else filtered

def format_duration(seconds):
    """格式化时间"""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"

def save_workout_record(exercises, duration):
    """保存训练记录"""
    record = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "exercises": exercises,
        "duration": duration,
        "calories": duration * 7  # 粗略估算
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
        
        st.subheader(f"🏆 推薦訓練動作 ({len(recommended)} 個)")
        
        for exercise in recommended:
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{exercise['nameCN']}** ({exercise['name']})")
                    st.caption(f"難度: {exercise['difficulty']} | 部位: {exercise['bodyPart']}")
                    st.caption(f"{exercise['sets']} 組 × {exercise['reps']} 次 | 休息: {exercise['restSeconds']} 秒")
                with col2:
                    if st.button("查看", key=f"view_{exercise['id']}"):
                        st.session_state.current_page = "動作詳情"
                        st.session_state.selected_exercise = exercise
        
        st.write("---")
        
        if st.button("🎬 開始訓練", key="start_workout", use_container_width=True):
            st.session_state.current_workout = {
                "exercises": [e["nameCN"] for e in recommended],
                "duration": duration,
                "body_parts": selected_parts,
                "start_time": datetime.now()
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
    
    for exercise in filtered_exercises:
        with st.expander(f"**{exercise['nameCN']}** - {exercise['difficulty']}", expanded=False):
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

# ==================== 页面 3: 训练执行 ====================

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
        exercise_name = workout["exercises"][current_index]
        current_exercise = next((e for e in EXERCISES if e["nameCN"] == exercise_name), None)
        
        if current_exercise:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader(f"當前動作: {current_exercise['nameCN']}")
                st.write(f"部位: {current_exercise['bodyPart']}")
                st.write(f"難度: {current_exercise['difficulty']}")
            
            with col2:
                st.metric("組", st.session_state.workout_progress.get("sets", 1))
                st.metric("次", st.session_state.workout_progress.get("reps", 1))
            
            st.write("---")
            
            st.write("**執行技巧**:")
            for tip in current_exercise["tips"]:
                st.write(f"✅ {tip}")
            
            st.write("---")
            
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
                    else:
                        current_sets = st.session_state.workout_progress.get("sets", 1)
                        if current_sets < current_exercise["sets"]:
                            st.session_state.workout_progress["sets"] = current_sets + 1
                            st.session_state.workout_progress["reps"] = 1
                        else:
                            st.session_state.workout_progress["current_exercise"] = current_index + 1
                            st.session_state.workout_progress["sets"] = 1
                            st.session_state.workout_progress["reps"] = 1
                    
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

# ==================== 页面 4: 统计 ====================

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

# ==================== 页面 5: 设置 ====================

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
        st.metric("應用版本", "1.0.0")
    
    with col2:
        st.metric("動作庫", f"{len(EXERCISES)} 個動作")
    
    with col3:
        st.metric("訓練記錄", len(st.session_state.workout_records))
    
    st.write("---")
    
    if st.button("💾 保存設置", use_container_width=True):
        st.success("✅ 設置已保存")

# ==================== 主程序 ====================

def main():
    # 侧边栏导航
    with st.sidebar:
        st.title("SmartFit")
        
        pages = ["首頁", "動作庫", "訓練執行", "統計", "設置"]
        
        selected_page = st.radio("選擇頁面", pages, 
                                key="nav",
                                label_visibility="collapsed")
        
        st.session_state.current_page = selected_page
        
        st.write("---")
        
        if st.session_state.user_data["name"]:
            st.write(f"👤 {st.session_state.user_data['name']}")
            st.write(f"📅 年齡: {st.session_state.user_data['age']}")
            st.write(f"🏋️ 模式: {st.session_state.user_data['mode']}")
    
    # 根据当前页面显示内容
    if st.session_state.current_page == "首頁":
        page_home()
    elif st.session_state.current_page == "動作庫":
        page_exercise_list()
    elif st.session_state.current_page == "訓練執行":
        page_workout_execution()
    elif st.session_state.current_page == "統計":
        page_statistics()
    elif st.session_state.current_page == "設置":
        page_settings()

if __name__ == "__main__":
    main()
