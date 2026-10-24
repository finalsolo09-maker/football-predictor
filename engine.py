import numpy as np
import pandas as pd
from datetime import datetime
import os

class AutoFootballPredictor:
    def __init__(self, n_sims=10000):
        self.n_sims = n_sims

    def fetch_todays_fixtures(self):
import requests
import pandas as pd

API_KEY = "YOUR_API_TOKEN_HERE"  # 발급받은 API 토큰 입력
HEADERS = {"X-Auth-Token": API_KEY}

def get_upcoming_matches(competition_code="PL"):
    """
    지정한 리그의 예정된 경기 일정을 가져옵니다.
    - PL: 프리미어리그, PD: 라리가, CL: 챔피언스리그 등
    """
    url = f"https://api.football-data.org/v4/competitions/{competition_code}/matches?status=SCHEDULED"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        matches = []
        for match in data.get('matches', []):
            matches.append({
                'match_id': match['id'],
                'date': match['utcDate'],
                'home_team': match['homeTeam']['name'],
                'away_team': match['awayTeam']['name'],
                'matchday': match.get('matchday')
            })
        return pd.DataFrame(matches)
    else:
        print(f"API 요청 실패 (상태 코드: {response.status_code}): {response.text}")
        return pd.DataFrame()

# 실행 예시
if __name__ == "__main__":
    df_fixtures = get_upcoming_matches("PL") # 프리미어리그 예정 경기 수집
    print(df_fixtures.head())
    def simulate_match(self, home_xg, away_xg):
        # 몬테카를로 시뮬레이션
        home_goals = np.random.poisson(max(home_xg, 0.2), self.n_sims)
        away_goals = np.random.poisson(max(away_xg, 0.2), self.n_sims)

        home_wins = np.sum(home_goals > away_goals)
        draws = np.sum(home_goals == away_goals)
        away_wins = np.sum(home_goals < away_goals)

        return {
            "Home Win (%)": round((home_wins / self.n_sims) * 100, 2),
            "Draw (%)": round((draws / self.n_sims) * 100, 2),
            "Away Win (%)": round((away_wins / self.n_sims) * 100, 2)
        }

    def run_daily_prediction(self):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S]')} 자동 예측 프로그램을 실행합니다...")
        matches = self.fetch_todays_fixtures()
        
        results = []
        for match in matches:
            pred = self.simulate_match(match["home_xG"], match["away_xG"])
            results.append({
                "Date": datetime.now().strftime('%Y-%m-%d'),
                "Home": match["home_team"],
                "Away": match["away_team"],
                "Home Win%": pred["Home Win (%)"],
                "Draw%": pred["Draw (%)"],
                "Away Win%": pred["Away Win (%)"]
            })
            
        df_results = pd.DataFrame(results)
        
        # 결과를 CSV 파일로 저장 (깃허브에 자동 누적)
        output_file = "daily_predictions.csv"
        if os.path.exists(output_file):
            df_existing = pd.read_csv(output_file)
            df_final = pd.concat([df_existing, df_results]).drop_duplicates()
        else:
            df_final = df_results
            
        df_final.to_csv(output_file, index=False)
        print("모든 오늘의 경기 예측이 완료되어 파일에 저장되었습니다!")

if __name__ == "__main__":
    predictor = AutoFootballPredictor()
    predictor.run_daily_prediction()
