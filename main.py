import sqlite3
import pandas as pd
from datetime import datetime
from pipeline.collector import FootballDataCollector
from pipeline.features import FeaturePipeline
from pipeline.model import HybridPredictionEngine

def init_db(db_path="data/predictions.db"):
    """예측 결과를 누적 저장할 SQLite 데이터베이스 테이블을 생성합니다."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            predict_date TEXT,
            match_date TEXT,
            home_team TEXT,
            away_team TEXT,
            lambda_home REAL,
            lambda_away REAL,
            home_win_prob REAL,
            draw_prob REAL,
            away_win_prob REAL,
            top_scores TEXT
        )
    """)
    conn.commit()
    conn.close()

def run_pipeline():
    print(f"=== [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 파이프라인 가동 시작 ===")
    init_db()

    # 1. 데이터 수집
    collector = FootballDataCollector(league_code="ENG-Premier League", season="2025")
    schedule, team_stats = collector.fetch_fbref_metrics()

    # 과거 샘플 데이터 (기반 학습 데이터셋 설정)
    sample_history = pd.DataFrame([
        {'home_team': 'Arsenal', 'away_team': 'Chelsea', 'home_goals': 2, 'away_goals': 1},
        {'home_team': 'Chelsea', 'away_team': 'Arsenal', 'home_goals': 1, 'away_goals': 1},
        {'home_team': 'Arsenal', 'away_team': 'Everton', 'home_goals': 3, 'away_goals': 0},
        {'home_team': 'Everton', 'away_team': 'Chelsea', 'home_goals': 0, 'away_goals': 2},
    ])

    # 2. Feature 추출 & Dixon-Coles 파라미터 최적화
    feature_pipe = FeaturePipeline()
    dc_params, home_adv = feature_pipe.fit_dixon_coles(sample_history)

    # 3. 당일 예측 대상 경기 매치업
    todays_matches = [
        {"home_team": "Arsenal", "away_team": "Everton", "date": "2026-10-24"},
        {"home_team": "Chelsea", "away_team": "Arsenal", "date": "2026-10-25"}
    ]

    # 4. 예측 수행 및 DB 저장
    engine = HybridPredictionEngine(n_simulations=50000)
    conn = sqlite3.connect("data/predictions.db")
    cursor = conn.cursor()

    for match in todays_matches:
        h_team, a_team = match["home_team"], match["away_team"]
        l_home, l_away = engine.calculate_lambdas(h_team, a_team, dc_params, home_adv)
        pred = engine.run_monte_carlo(l_home, l_away)

        cursor.execute("""
            INSERT INTO predictions (predict_date, match_date, home_team, away_team, lambda_home, lambda_away, home_win_prob, draw_prob, away_win_prob, top_scores)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime('%Y-%m-%d'),
            match["date"],
            h_team,
            a_team,
            round(l_home, 2),
            round(l_away, 2),
            pred['home_win_prob'],
            pred['draw_prob'],
            pred['away_win_prob'],
            pred['top_scores']
        ))
        print(f"✅ [{h_team} vs {a_team}] 예측 완료: 승 {pred['home_win_prob']}% / 무 {pred['draw_prob']}% / 패 {pred['away_win_prob']}%")

    conn.commit()
    conn.close()
    print("=== 파이프라인 완료: DB 업데이트 완료 ===")

if __name__ == "__main__":
    run_pipeline()
