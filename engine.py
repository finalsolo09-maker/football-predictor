import numpy as np
import pandas as pd
from datetime import datetime
import os

class AutoFootballPredictor:
    def __init__(self, n_sims=10000):
        self.n_sims = n_sims

    def fetch_todays_fixtures(self):
        # [실전 팁] 이 부분에 무료 API(football-data.org 등)나 크롤링 코드를 넣습니다.
        # 예시를 위해 오늘 예정된 가상의 경기 리스트를 만듭니다.
        todays_matches = [
            {"home_team": "Arsenal", "away_team": "Chelsea", "home_xG": 1.9, "away_xG": 1.1},
            {"home_team": "Liverpool", "away_team": "Man City", "home_xG": 1.6, "away_xG": 1.7},
        ]
        return todays_matches

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
