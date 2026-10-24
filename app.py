import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="오픈 데이터 축구 예측 엔진", layout="wide")
st.title("⚽ 실시간 오픈 데이터 기반 축구 예측 대시보드")
st.write("`football-data.co.uk`의 실제 오픈 데이터를 바탕으로 통계 시뮬레이션을 거친 결과입니다.")

def load_predictions():
    try:
        conn = sqlite3.connect("data/predictions.db")
        df = pd.read_sql_query("SELECT * FROM predictions ORDER BY id DESC", conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

df_preds = load_predictions()

if df_preds.empty:
    st.warning("⚠️ 아직 생성된 예측 데이터가 없습니다. 깃허브 액션이 실행되었거나 로컬에서 `main.py`를 먼저 실행해주세요.")
else:
    st.subheader("📊 최신 경기 예측 결과 리스트")
    st.dataframe(df_preds, use_container_width=True)

    st.markdown("---")
    st.subheader("🔥 가장 최근 분석된 매치업 하이라이트")
    latest = df_preds.iloc[0]
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label=f"🏠 {latest['home_team']} 승", value=f"{latest['home_win_prob']}%")
    col2.metric(label="🤝 무승부", value=f"{latest['draw_prob']}%")
    col3.metric(label=f"✈️ {latest['away_team']} 승", value=f"{latest['away_win_prob']}%")
    
    st.info(f"📈 양 팀 기대 득점(Lambda) -> **{latest['home_team']}**: {latest['home_goals_avg']} 골 / **{latest['away_team']}**: {latest['away_goals_avg']} 골")
    st.success(f"🎯 몬테카를로 시뮬레이션 Top 3 예상 스코어: **{latest['top_scores']}**")
