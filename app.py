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
