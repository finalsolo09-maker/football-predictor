import streamlit as st
from engine import SimpleFootballEngine

st.title("⚽ 제로코스트 축구 경기 예측 엔진")
st.write("무료 데이터와 몬테카를로 시뮬레이션을 활용한 승무패 예측 시스템입니다.")

# 사이드바 입력 설정
st.sidebar.header("팀 스탯 입력 (최근 5경기 평균)")
home_team = st.sidebar.text_input("홈 팀 이름", "Arsenal")
home_xg = st.sidebar.slider(f"{home_team} 평균 기대 득점(npxG)", 0.5, 3.5, 1.8)

away_team = st.sidebar.text_input("원정 팀 이름", "Chelsea")
away_xg = st.sidebar.slider(f"{away_team} 평균 기대 득점(npxG)", 0.5, 3.5, 1.2)

if st.button("경기 예측 시작하기"):
    engine = SimpleFootballEngine()
    l_home, l_away = engine.calculate_lambdas(home_xg, away_xg)
    result = engine.simulate_match(l_home, l_away)
    
    st.subheader(f"📊 [{home_team} vs {away_team}] 예측 결과")
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label=f"🏠 {home_team} 승", value=f"{result['Home Win']}%")
    col2.metric(label="🤝 무승부", value=f"{result['Draw']}%")
    col3.metric(label=f"✈️ {away_team} 승", value=f"{result['Away Win']}%")
    
    st.markdown("---")
    st.subheader("🎯 가장 확률 높은 예상 스코어 Top 3")
    for score, prob in result['Top Scores']:
        st.write(f"- **{score[0]} : {score[1]}** (확률: {prob}%)")
import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="축구 경기 자동 예측 파이프라인", layout="wide")
st.title("⚽ 축구 경기 실시간 예측 DB 대시보드")

def load_data():
    conn = sqlite3.connect("data/predictions.db")
    df = pd.read_sql_query("SELECT * FROM predictions ORDER BY id DESC", conn)
    conn.close()
    return df

try:
    df_preds = load_data()
    st.subheader("📊 최근 자동 계산된 경기 예측 결과")
    st.dataframe(df_preds, use_container_width=True)

    if not df_preds.empty:
        st.subheader("🎯 최신 매치업 상세 카드")
        latest = df_preds.iloc[0]
        col1, col2, col3 = st.columns(3)
        col1.metric(f"🏠 {latest['home_team']} 승리", f"{latest['home_win_prob']}%")
        col2.metric("🤝 무승부", f"{latest['draw_prob']}%")
        col3.metric(f"✈️ {latest['away_team']} 승리", f"{latest['away_win_prob']}%")
        st.info(f"💡 기대 득점(xG) -> {latest['home_team']}: {latest['lambda_home']} | {latest['away_team']}: {latest['lambda_away']}")
        st.write(f"🏆 상위 예상 스코어: {latest['top_scores']}")
except Exception as e:
    st.warning("아직 데이터베이스에 누적된 예측 결과가 없습니다. main.py를 실행해주세요.")
