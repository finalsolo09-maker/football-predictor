import numpy as np
import pandas as pd
from scipy.stats import poisson

class SimpleFootballEngine:
    def __init__(self, n_sims=10000):
        self.n_sims = n_sims

    def calculate_lambdas(self, home_form_xG, away_form_xG):
        # 팀의 최근 xG(기대 득점) 기반으로 양 팀의 경기 기대 득점(Lambda) 산출
        lambda_home = max(home_form_xG, 0.2)
        lambda_away = max(away_form_xG, 0.2)
        return lambda_home, lambda_away

    def simulate_match(self, lambda_home, lambda_away):
        # 몬테카를로 시뮬레이션 (1만 번 가상 경기)
        home_goals = np.random.poisson(lambda_home, self.n_sims)
        away_goals = np.random.poisson(lambda_away, self.n_sims)

        home_wins = np.sum(home_goals > away_goals)
        draws = np.sum(home_goals == away_goals)
        away_wins = np.sum(home_goals < away_goals)

        # 가장 확률 높은 탑 3 스코어 산출
        scores, counts = np.unique(list(zip(home_goals, away_goals)), axis=0, return_counts=True)
        top_scores_idx = np.argsort(counts)[::-1][:3]
        top_scores = [((scores[i][0], scores[i][1]), round((counts[i] / self.n_sims) * 100, 2)) for i in top_scores_idx]

        return {
            "Home Win": round((home_wins / self.n_sims) * 100, 2),
            "Draw": round((draws / self.n_sims) * 100, 2),
            "Away Win": round((away_wins / self.n_sims) * 100, 2),
            "Top Scores": top_scores
        }
