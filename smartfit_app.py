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
        "mode": "徒手",
        "icon": "🏋️",
        "description": "經典的徒手胸部訓練動作",
        "tips": ["保持身體成一直線", "降低身體直到胸部接近地面", "推回起始位置"],
        "mistakes": ["臀部下沉", "肘部張得太開", "活動範圍不足"],
        "youtubeKeyword": "push ups perfect form"
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
        "mode": "徒手",
        "icon": "🦵",
        "description": "下身訓練的基礎動作",
        "tips": ["挺胸保持核心緊縮", "臀部向後向下移動", "通過腳跟推起"],
        "mistakes": ["膝蓋內扣", "身體向前傾斜過多", "深度不夠"],
        "youtubeKeyword": "bodyweight squats form"
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
        "mode": "徒手",
        "icon": "💪",
        "description": "上身拉力訓練",
        "tips": ["握距略寬於肩膀", "下巴超過橫杆", "控制下降"],
        "mistakes": ["活動範圍不足", "使用衝力", "肘部張得太開"],
        "youtubeKeyword": "pull ups technique tutorial"
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
        "mode": "徒手",
        "icon": "📍",
        "description": "核心穩定性訓練",
        "tips": ["身體成一直線", "全程核心緊縮", "不要臀部下沉"],
        "mistakes": ["臀部下沉", "頸部過度拉伸", "肩膀過度前傾"],
        "youtubeKeyword": "perfect plank form"
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
        "mode": "健身房",
        "icon": "🏗️",
        "description": "使用啞鈴的胸部訓練",
        "tips": ["身體呈平板狀", "啞鈴降至胸部", "爆發力推起"],
        "mistakes": ["彈跳重量", "推力不均勻", "肘部貼得太近"],
        "youtubeKeyword": "dumbbell bench press form"
    },
    {
        "id": "006",
        "name": "Barbell Squat",
        "nameCN": "槓鈴深蹲",
        "bodyPart": "腿部",
        "difficulty": "中級",
        "sets": 4,
        "reps": 8,
        "restSeconds": 120,
        "mode": "健身房",
        "icon": "⬇️",
        "description": "加重腿部訓練",
        "tips": ["槓鈴放在肩膀", "保持直立姿勢", "深蹲至平行"],
        "mistakes": ["膝蓋超過腳尖", "過度傾斜", "不夠深"],
        "youtubeKeyword": "barbell back squat form"
    },
    {
        "id": "007",
        "name": "Cable Row",
        "nameCN": "拉力機划船",
        "bodyPart": "背部",
        "difficulty": "初級",
        "sets": 4,
        "reps": 12,
        "restSeconds": 60,
        "mode": "健身房",
        "icon": "🔗",
        "description": "背部拉力機訓練",
        "tips": ["坐直保持挺胸", "拉至腹部", "控制回放"],
        "mistakes": ["過度前傾", "手臂主導", "不完整動作"],
        "youtubeKeyword": "cable row machine form"
    },
    {
        "id": "008",
        "name": "Leg Press Machine",
        "nameCN": "腿部推蹬機",
        "bodyPart": "腿部",
        "difficulty": "初級",
        "sets": 3,
        "reps": 15,
        "restSeconds": 90,
        "mode": "健身房",
        "icon": "🚀",
        "description": "機械式腿部推蹬",
        "tips": ["腳放在機器上", "完全伸展", "控制下降"],
        "mistakes": ["膝蓋鎖定", "下降不足", "重量過重"],
        "youtubeKeyword": "leg press machine proper form"
    },
    {
        "id": "009",
        "name": "Chest Press Machine",
        "nameCN": "胸部推蹬機",
        "bodyPart": "胸部",
        "difficulty": "初級",
        "sets": 3,
        "reps": 12,
        "restSeconds": 60,
        "mode": "健身房",
        "icon": "🎯",
        "description": "機械式胸部訓練",
        "tips": ["坐直對齊機器", "完全推出", "控制回放"],
        "mistakes": ["肘部太低", "過度推出", "不穩定"],
        "youtubeKeyword": "chest press machine tutorial"
    },
    {
        "id": "010",
        "name": "Lat Pulldown",
        "nameCN": "下拉機",
        "bodyPart": "背部",
        "difficulty": "初級",
        "sets": 3,
        "reps": 12,
        "restSeconds": 60,
        "mode": "健身房",
        "icon": "⬇️",
        "description": "背闊肌下拉訓練",
        "tips": ["拉至胸部", "控制回放", "全程核心緊縮"],
        "mistakes": ["身體搖晃", "手臂主導", "不完整範圍"],
        "youtubeKeyword": "lat pulldown proper technique"
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
    """获取推荐动作 - 按模式区分"""
    filtered = EXERCISES
    
    # 按模式篩選
    filtered = [e for e in filtered if e["mode"] == mode]
    
    # 按身体部位筛选
    filtered = [e for e in filtered if e["bodyPart"] in body_parts]
    
    # 返回推荐的动作（限制数量）
    return filtered[:4] if len(filtered) > 4 else filtered

def get_youtube_link(keyword):
    """生成 YouTube 搜尋鏈接"""
    search_url = f"https://www.youtube.com/results?search_query={keyword.replace(' ', '+')}"
    return search_url

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
                            if st.button("📺 YT", key=f"yt_{exercise['id']}", help="在 YouTube 上查看"):
                                st.markdown(f"[📺 點擊查看 YouTube 教學]({get_youtube_link(exercise['youtubeKeyword'])})", 
                                           unsafe_allow_html=True)
                        with col_b:
                            if st.button("📋", key=f"view_{exercise['id']}", help="查看詳細"):
                                st.session_state.current_page = "動作詳情"
                                st.session_state.selected_exercise = exercise
                                st.rerun()
            
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
                st.markdown(f"[📺 點擊前往 YouTube]({get_youtube_link(exercise['youtubeKeyword'])})", 
                           unsafe_allow_html=True)

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
        st.metric("應用版本", "2.0.0")
    
    with col2:
        st.metric("動作庫", f"{len(EXERCISES)} 個動作")
    
    with col3:
        st.metric("訓練記錄", len(st.session_state.workout_records))
    
    st.write("---")
    
    st.info("✨ 新功能：添加 YouTube 連結、彩色 Icon、健身房模式區分")
    
    if st.button("💾 保存設置", use_container_width=True):
        st.success("✅ 設置已保存")

# ==================== 主程序 ====================

def main():
    # 侧边栏导航
    with st.sidebar:
        st.title("💪 SmartFit")
        st.write("**v2.0** - 改進版")
        
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
        
        st.write("---")
        
        st.markdown("### 📝 本版本改進：")
        st.markdown("""
        ✅ YouTube 連結  
        ✅ 彩色 Icon  
        ✅ 健身房模式區分  
        ✅ 改進的視覺設計
        """)
    
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
