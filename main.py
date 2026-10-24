import os
import sqlite3
import pandas as pd
import numpy as np
from scipy.stats import poisson
from datetime import datetime

# 프리미어리그 2025/2026 시즌 공식 오픈 CSV 데이터 링크 (실시간 연동 가능)
# (연도 코드는 시즌에 맞게 변경 가능: 예시 25/26 시즌 -> mmz2526/E0.csv)
DATA_URL = "https://www.football-data.co.uk/mmz2526/E0.csv"

def init_db(db_path="data/predictions.db"):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            update_time TEXT,
            home_team TEXT,
            away_team TEXT,
            home_goals_avg REAL,
            away_goals_avg REAL,
            home_win_prob REAL,
            draw_prob REAL,
            away_win_prob REAL,
            top_scores TEXT
        )
    """)
    conn.commit()
    conn.close()

def fetch_real_data():
    print("🌐 웹에서 최신 축구 오픈 데이터를 다운로드 중...")
    try:
        df = pd.read_csv(DATA_URL)
        # 결측치(아직 치르지 않은 경기 등) 제거
        df = df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])
        return df
    except Exception as e:
        print(f"데이터 다운로드 실패: {e}")
        return pd.DataFrame()

def calculate_team_strengths(df):
    """팀별 평균 득점력과 실점력 계산"""
    if df.empty:
        return {}, {}, 1.2, 1.2
    
    home_attack = df.groupby('HomeTeam')['FTHG'].mean().to_dict()
    home_defense = df.groupby('HomeTeam')['FTAG'].mean().to_dict()
    away_attack = df.groupby('AwayTeam')['FTAG'].mean().to_dict()
    away_defense = df.groupby('AwayTeam')['FTHG'].mean().to_dict()
    
    league_avg_home = df['FTHG'].mean()
    league_avg_away = df['FTAG'].mean()
    
    return home_attack, home_defense, away_attack, away_defense, league_avg_home, league_avg_away

def run_simulation(lambda_home, lambda_away, n_sims=20000):
    np.random.seed(42)
    home_goals = np.random.poisson(max(lambda_home, 0.2), n_sims)
    away_goals = np.random.poisson(max(lambda_away, 0.2), n_sims)

    home_wins = np.sum(home_goals > away_goals)
    draws = np.sum(home_goals == away_goals)
    away_wins = np.sum(home_goals < away_goals)

    scores, counts = np.unique(list(zip(home_goals, away_goals)), axis=0, return_counts=True)
    top_idx = np.argsort(counts)[::-1][:3]
    top_scores = [f"{scores[i][0]}-{scores[i][1]} ({counts[i]/n_sims*100:.1f}%)" for i in top_idx]

    return {
        "home_win": round((home_wins / n_sims) * 100, 2),
        "draw": round((draws / n_sims) * 100, 2),
        "away_win": round((away_wins / n_sims) * 100, 2),
        "top_scores": ", ".join(top_scores)
    }

def main():
    print("=== 축구 자동 예측 파이프라인 시작 ===")
    init_db()
    
    df_matches = fetch_real_data()
    if df_matches.empty:
        print("분석할 데이터가 없습니다.")
        return

    h_att, h_def, a_att, a_def, avg_h, avg_a = calculate_team_strengths(df_matches)

    # 예측을 수행할 대표적인 이번 주 매치업 선정 (데이터에 존재하는 팀 기준)
    teams = list(h_att.keys())
    if len(teams) < 2:
        print("팀 데이터가 부족합니다.")
        return

    # 예시로 데이터에 있는 상위 팀들 간의 가상/실제 매치업 예측 수행
    sample_matchups = [
        (teams[0], teams[1]),
        (teams[2], teams[3]) if len(teams) > 3 else (teams[0], teams[2])
    ]

    conn = sqlite3.connect("data/predictions.db")
    cursor = conn.cursor()

    for home, away in sample_matchups:
        # 공격력과 수비력을 결합한 독스-콜스 간이 람다(기대 득점) 산출
        h_g_avg = (h_att.get(home, avg_h) + a_def.get(away, avg_a)) / 2
        a_g_avg = (a_att.get(away, avg_a) + h_def.get(home, avg_h)) / 2

        res = run_simulation(h_g_avg, a_g_avg)

        cursor.execute("""
            INSERT INTO predictions (update_time, home_team, away_team, home_goals_avg, away_goals_avg, home_win_prob, draw_prob, away_win_prob, top_scores)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            home, away,
            round(h_g_avg, 2), round(a_g_avg, 2),
            res['home_win'], res['draw'], res['away_win'],
            res['top_scores']
        ))
        print(f"✅ [{home} vs {away}] 예측 완료 -> 홈승: {res['home_win']}% | 무: {res['draw']}% | 원정승: {res['away_win']}%")

    conn.commit()
    conn.close()
    print("=== 파이프라인 연산 및 DB 저장 완료 ===")

if __name__ == "__main__":
    main()
