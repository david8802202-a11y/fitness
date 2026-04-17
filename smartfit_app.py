import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="SmartFit", page_icon="💪", layout="wide")

st.markdown("""<style>
.exercise-card {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
padding: 15px; border-radius: 12px; margin: 10px 0; color: white;}
.exercise-card-gym {background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
padding: 15px; border-radius: 12px; margin: 10px 0; color: white;}
</style>""", unsafe_allow_html=True)

EXERCISES = [
    {"id": "001", "name": "Push-ups", "nameCN": "俯臥撑", "bodyPart": "胸部", "difficulty": "初級", "sets": 3, "reps": 12, "restSeconds": 60, "mode": "徒手", "icon": "🏋️", "description": "經典的徒手胸部訓練動作", "tips": ["保持身體成一直線", "降低身體直到胸部接近地面", "推回起始位置"], "mistakes": ["臀部下沉", "肘部張得太開", "活動範圍不足"], "youtubeKeyword": "push ups proper form"},
    {"id": "002", "name": "Wide Push-ups", "nameCN": "寬距俯臥撑", "bodyPart": "胸部", "difficulty": "初級", "sets": 3, "reps": 10, "restSeconds": 60, "mode": "徒手", "icon": "🏋️", "description": "寬距俯臥撑更針對胸部外側", "tips": ["雙手距離比肩膀寬", "保持直線", "完整範圍"], "mistakes": ["太寬容易傷肩", "肘部內彎", "不穩定"], "youtubeKeyword": "wide grip push ups"},
    {"id": "003", "name": "Diamond Push-ups", "nameCN": "菱形俯臥撑", "bodyPart": "胸部", "difficulty": "中級", "sets": 3, "reps": 8, "restSeconds": 60, "mode": "徒手", "icon": "💎", "description": "針對三頭肌和內胸", "tips": ["雙手在胸下方", "肘部靠近身體", "完全伸展"], "mistakes": ["肘部張太開", "身體搖晃", "範圍太小"], "youtubeKeyword": "diamond push ups form"},
    {"id": "004", "name": "Squats", "nameCN": "深蹲", "bodyPart": "腿部", "difficulty": "初級", "sets": 3, "reps": 15, "restSeconds": 90, "mode": "徒手", "icon": "🦵", "description": "下身訓練的基礎動作", "tips": ["挺胸保持核心緊縮", "臀部向後向下移動", "通過腳跟推起"], "mistakes": ["膝蓋內扣", "身體向前傾斜過多", "深度不夠"], "youtubeKeyword": "bodyweight squats form"},
    {"id": "005", "name": "Pull-ups", "nameCN": "引體向上", "bodyPart": "背部", "difficulty": "中級", "sets": 3, "reps": 8, "restSeconds": 120, "mode": "徒手", "icon": "💪", "description": "上身拉力訓練", "tips": ["握距略寬於肩膀", "下巴超過橫杆", "控制下降"], "mistakes": ["活動範圍不足", "使用衝力", "肘部張得太開"], "youtubeKeyword": "pull ups proper form"},
    {"id": "006", "name": "Plank", "nameCN": "棒式", "bodyPart": "核心", "difficulty": "初級", "sets": 3, "reps": 30, "restSeconds": 60, "mode": "徒手", "icon": "📍", "description": "核心穩定性訓練", "tips": ["身體成一直線", "全程核心緊縮", "不要臀部下沉"], "mistakes": ["臀部下沉", "頸部過度拉伸", "肩膀過度前傾"], "youtubeKeyword": "perfect plank form"},
    {"id": "007", "name": "Dumbbell Bench Press", "nameCN": "啞鈴臥推", "bodyPart": "胸部", "difficulty": "中級", "sets": 4, "reps": 10, "restSeconds": 90, "mode": "健身房", "icon": "🏗️", "description": "使用啞鈴的胸部訓練", "tips": ["身體呈平板狀", "啞鈴降至胸部", "爆發力推起"], "mistakes": ["彈跳重量", "推力不均勻", "肘部貼得太近"], "youtubeKeyword": "dumbbell bench press form"},
    {"id": "008", "name": "Barbell Squat", "nameCN": "槓鈴深蹲", "bodyPart": "腿部", "difficulty": "中級", "sets": 4, "reps": 8, "restSeconds": 120, "mode": "健身房", "icon": "⬇️", "description": "加重腿部訓練", "tips": ["槓鈴放在肩膀", "保持直立姿勢", "深蹲至平行"], "mistakes": ["膝蓋超過腳尖", "過度傾斜", "不夠深"], "youtubeKeyword": "barbell back squat form"},
    {"id": "009", "name": "Lat Pulldown", "nameCN": "下拉機", "bodyPart": "背部", "difficulty": "初級", "sets": 3, "reps": 12, "restSeconds": 60, "mode": "健身房", "icon": "⬇️", "description": "背闊肌下拉訓練", "tips": ["拉至胸部", "控制回放", "全程核心緊縮"], "mistakes": ["身體搖晃", "手臂主導", "不完整範圍"], "youtubeKeyword": "lat pulldown proper technique"},
    {"id": "010", "name": "Dumbbell Curls", "nameCN": "啞鈴彎舉", "bodyPart": "手臂", "difficulty": "初級", "sets": 3, "reps": 12, "restSeconds": 60, "mode": "健身房", "icon": "💪", "description": "二頭肌孤立訓練", "tips": ["靠在牆上保持穩定", "只有前臂移動", "充分收縮"], "mistakes": ["使用衝力搖晃", "不完全伸展", "肘部移動"], "youtubeKeyword": "bicep curls proper form"},
]

BODY_PARTS = ["胸部", "背部", "肩膀", "手臂", "腿部", "核心"]

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

def get_exercises(body_parts, mode):
    return [e for e in EXERCISES if e["mode"] == mode and e["bodyPart"] in body_parts][:4]

# 側邊欄導航
with st.sidebar:
    st.title("💪 SmartFit v4")
    
    if st.button("🏠 首頁", use_container_width=True, key="nav_home"):
        st.session_state.page = "home"
        st.rerun()
    if st.button("📊 統計", use_container_width=True, key="nav_stats"):
        st.session_state.page = "stats"
        st.rerun()
    if st.button("⚙️ 設置", use_container_width=True, key="nav_settings"):
        st.session_state.page = "settings"
        st.rerun()

# 首頁
if st.session_state.page == "home":
    st.title("💪 SmartFit - 您的私人健身教練")
    
    col1, col2 = st.columns(2)
    with col1:
        mode = st.radio("訓練模式", ["🏠 徒手", "🏋️ 健身房"], key="mode_select")
        st.session_state.user["mode"] = "徒手" if "徒手" in mode else "健身房"
    with col2:
        duration = st.radio("訓練時長", [15, 30, 45, 60], horizontal=True, key="duration_select")
    
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
        
        exercises = get_exercises(selected_parts, st.session_state.user["mode"])
        
        if exercises:
            st.subheader(f"🏆 推薦訓練動作 ({len(exercises)}個)")
            
            for ex in exercises:
                c1, c2, c3, c4 = st.columns([0.5, 2.5, 1, 1])
                with c1:
                    st.write(ex["icon"])
                with c2:
                    st.write(f"**{ex['nameCN']}** ({ex['difficulty']})")
                    st.caption(f"{ex['sets']}×{ex['reps']} | {ex['bodyPart']}")
                with c3:
                    if st.button("詳情", key=f"btn_detail_{ex['id']}"):
                        st.session_state.current_ex = ex
                        st.session_state.page = "detail"
                        st.rerun()
                with c4:
                    if st.button("YT", key=f"btn_yt_{ex['id']}"):
                        st.session_state.current_ex = ex
                        st.session_state.page = "youtube"
                        st.rerun()
            
            st.divider()
            
            if st.button("🎬 開始訓練", use_container_width=True, key="btn_start"):
                st.session_state.workout = {"exercises": exercises, "start": datetime.now(), "duration": duration}
                st.session_state.progress = {"ex_idx": 0, "sets": 1, "reps": 1}
                st.session_state.page = "workout"
                st.rerun()

# 動作詳情
elif st.session_state.page == "detail":
    if st.session_state.current_ex:
        ex = st.session_state.current_ex
        st.title(f"{ex['icon']} {ex['nameCN']}")
        st.write(f"**難度**: {ex['difficulty']} | **部位**: {ex['bodyPart']}")
        st.write(f"**推薦**: {ex['sets']}×{ex['reps']} | **休息**: {ex['restSeconds']}秒")
        st.divider()
        st.write(f"**描述**: {ex['description']}")
        st.subheader("✅ 執行技巧")
        for tip in ex["tips"]:
            st.write(f"• {tip}")
        st.subheader("❌ 常見錯誤")
        for m in ex["mistakes"]:
            st.write(f"• {m}")
        if st.button("⬅️ 返回首頁"):
            st.session_state.page = "home"
            st.rerun()

# YouTube
elif st.session_state.page == "youtube":
    if st.session_state.current_ex:
        ex = st.session_state.current_ex
        st.title(f"📺 {ex['nameCN']} - YouTube")
        st.markdown(f"""
        <iframe width="100%" height="400" src="https://www.youtube.com/embed?listType=search&list={ex['youtubeKeyword'].replace(' ', '%20')}" 
        frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
        """, unsafe_allow_html=True)
        st.markdown(f"[🔗 更多視頻](https://www.youtube.com/results?search_query={ex['youtubeKeyword'].replace(' ', '+')})")
        if st.button("⬅️ 返回"):
            st.session_state.page = "home"
            st.rerun()

# 訓練執行
elif st.session_state.page == "workout":
    if st.session_state.workout:
        exs = st.session_state.workout["exercises"]
        prog = st.session_state.progress
        idx = prog["ex_idx"]
        
        st.progress(idx / len(exs), text=f"進度: {idx}/{len(exs)}")
        
        if idx < len(exs):
            ex = exs[idx]
            st.title(f"{ex['icon']} {ex['nameCN']}")
            c1, c2 = st.columns([3, 1])
            with c1:
                st.write(f"部位: {ex['bodyPart']} | 難度: {ex['difficulty']}")
            with c2:
                st.metric("組", prog["sets"])
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

# 統計
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

# 設置
elif st.session_state.page == "settings":
    st.title("⚙️ 設置")
    st.session_state.user["name"] = st.text_input("姓名", st.session_state.user["name"])
    st.session_state.user["age"] = st.slider("年齡", 15, 100, st.session_state.user["age"])
    c1, c2, c3 = st.columns(3)
    c1.metric("版本", "4.0")
    c2.metric("動作", len(EXERCISES))
    c3.metric("記錄", len(st.session_state.records))
