import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client

# ── 1. 페이지 설정 ──
st.set_page_config(
    page_title="교사용 대시보드",
    page_icon="📊",
    layout="wide"  # 가로로 넓게 보기
)

# ── 2. Supabase 연결 설정 (캐싱 사용) ──
@st.cache_resource
def get_supabase_client() -> Client:
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]
        return create_client(url, key)
    except KeyError:
        st.error("Secrets가 설정되지 않았습니다. .streamlit/secrets.toml을 확인하세요.")
        st.stop()

# ── 3. 데이터 로드 함수 (캐싱 사용, 새로고침 시 갱신) ──
# ttl=60: 60초마다 데이터 캐시 만료 (실시간성 확보)
@st.cache_data(ttl=60)
def load_data():
    supabase = get_supabase_client()
    # 'student_submissions' 테이블의 모든 데이터를 가져옴 (최신순 정렬)
    response = supabase.table("student_submissions") \
        .select("*") \
        .order("created_at", desc=True) \
        .execute()
    
    if not response.data:
        return pd.DataFrame() # 데이터가 없으면 빈 DF 반환

    df = pd.DataFrame(response.data)
    
    # 날짜 형식 변환 (UTC -> KST 보기 편하게)
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"])
    
    return df

# ── 4. 데이터 전처리 (O/X 분석용) ──
def process_grading_status(df):
    """피드백 텍스트(O:..., X:...)에서 정오답 여부만 추출"""
    # 분석할 피드백 컬럼들
    feedback_cols = ["feedback_1", "feedback_2", "feedback_3"]
    
    status_df = df.copy()
    
    for col in feedback_cols:
        if col in status_df.columns:
            # 'O'로 시작하면 '정답', 아니면 '오답'으로 라벨링
            status_df[f"{col}_status"] = status_df[col].apply(
                lambda x: "정답 (O)" if str(x).strip().startswith("O") else "보완 필요 (X)"
            )
    return status_df

# ==================================================
# 메인 대시보드 UI
# ==================================================

st.title("📊 서술형 평가 결과 대시보드")
st.markdown("학생들의 제출 현황과 AI 채점 결과를 실시간으로 확인하세요.")

# [새로고침 버튼] - 캐시를 비우고 최신 데이터 로드
if st.button("🔄 데이터 새로고침"):
    load_data.clear()
    st.experimental_rerun()

# 데이터 로드
raw_df = load_data()

if raw_df.empty:
    st.warning("아직 제출된 데이터가 없습니다.")
else:
    # 데이터 가공
    df = process_grading_status(raw_df)

    # ── 5. 핵심 지표 (Metrics) ──
    st.markdown("### 1. 전체 현황")
    col1, col2, col3 = st.columns(3)
    
    total_students = df["student_id"].nunique()
    total_submissions = len(df)
    last_submit = df["created_at"].iloc[0].strftime("%Y-%m-%d %H:%M")

    col1.metric("총 제출 학생 수", f"{total_students}명")
    col2.metric("누적 제출 횟수", f"{total_submissions}건")
    col3.metric("최근 제출 시간", last_submit)

    st.markdown("---")

    # ── 6. 시각화 (Charts) ──
    st.markdown("### 2. 문항별 성취도 분석")
    
    # 문항별 정답률 데이터를 재구조화 (Wide -> Long format)
    # 시각화를 위해 Q1, Q2, Q3 상태를 하나의 컬럼으로 모음
    melted_df = df.melt(
        id_vars=["student_id"], 
        value_vars=["feedback_1_status", "feedback_2_status", "feedback_3_status"],
        var_name="Question", 
        value_name="Status"
    )
    
    # 컬럼 이름 예쁘게 변경 (feedback_1_status -> 문제 1)
    melted_df["Question"] = melted_df["Question"].replace({
        "feedback_1_status": "문제 1 (온도와 입자)",
        "feedback_2_status": "문제 2 (보일 법칙)",
        "feedback_3_status": "문제 3 (열의 이동)"
    })

    # Plotly 차트 생성 (누적 막대 그래프)
    fig = px.histogram(
        melted_df, 
        x="Question", 
        color="Status", 
        barmode="group",
        title="문항별 정답(O) / 보완필요(X) 분포",
        color_discrete_map={"정답 (O)": "#4CAF50", "보완 필요 (X)": "#FF5252"}, # 초록/빨강
        text_auto=True
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── 7. 상세 데이터 조회 (Drill-down) ──
    st.markdown("---")
    st.markdown("### 3. 학생별 상세 피드백 조회")

    # 검색 필터
    search_student = st.selectbox(
        "확인할 학생의 학번을 선택하세요:", 
        options=["전체 보기"] + list(df["student_id"].unique())
    )

    if search_student != "전체 보기":
        # 특정 학생 필터링
        student_df = df[df["student_id"] == search_student]
        
        for idx, row in student_df.iterrows():
            with st.expander(f"📝 {row['student_id']} - 제출일시: {row['created_at'].strftime('%m/%d %H:%M')}", expanded=True):
                c1, c2, c3 = st.columns(3)
                
                # 문제 1
                with c1:
                    st.markdown("**문제 1 (온도와 입자)**")
                    st.info(f"학생 답안: {row['answer_1']}")
                    feedback_color = "green" if row['feedback_1_status'] == "정답 (O)" else "red"
                    st.markdown(f":{feedback_color}[**AI 피드백:** {row['feedback_1']}]")
                
                # 문제 2
                with c2:
                    st.markdown("**문제 2 (보일 법칙)**")
                    st.info(f"학생 답안: {row['answer_2']}")
                    feedback_color = "green" if row['feedback_2_status'] == "정답 (O)" else "red"
                    st.markdown(f":{feedback_color}[**AI 피드백:** {row['feedback_2']}]")

                # 문제 3
                with c3:
                    st.markdown("**문제 3 (열의 이동)**")
                    st.info(f"학생 답안: {row['answer_3']}")
                    feedback_color = "green" if row['feedback_3_status'] == "정답 (O)" else "red"
                    st.markdown(f":{feedback_color}[**AI 피드백:** {row['feedback_3']}]")
    else:
        # 전체 데이터 테이블 보여주기
        st.dataframe(
            df[["student_id", "answer_1", "feedback_1", "answer_2", "feedback_2", "answer_3", "feedback_3", "created_at"]],
            use_container_width=True,
            hide_index=True
        )
