import numpy as np
import xgboost as xgb

class HybridPredictionEngine:
    def __init__(self, n_simulations=50000):
        self.n_sims = n_simulations
        self.xgb_model = xgb.XGBClassifier(
            n_estimators=100,
            learning_rate=0.03,
            max_depth=4,
            eval_metric='mlogloss'
        )

    def calculate_lambdas(self, home_team, away_team, dc_params, home_adv):
        """
        Dixon-Coles 수치 기반 양 팀의 예상 기대 득점(lambda)을 산출합니다.
        """
        h_att = dc_params.get(home_team, {}).get('att', 0.1)
        a_def = dc_params.get(away_team, {}).get('def', 0.0)
        a_att = dc_params.get(away_team, {}).get('att', 0.1)
        h_def = dc_params.get(home_team, {}).get('def', 0.0)

        lambda_home = np.exp(h_att + a_def + home_adv)
        lambda_away = np.exp(a_att + h_def)
        return lambda_home, lambda_away

    def run_monte_carlo(self, lambda_home, lambda_away):
        """
        몬테카를로 50,000회 시뮬레이션을 돌려 세부 스코어 매트릭스를 반환합니다.
        """
        np.random.seed(42) # 재현성을 위한 시드 고정
        home_goals = np.random.poisson(lambda_home, self.n_sims)
        away_goals = np.random.poisson(lambda_away, self.n_sims)

        home_wins = np.sum(home_goals > away_goals)
        draws = np.sum(home_goals == away_goals)
        away_wins = np.sum(home_goals < away_goals)

        scores, counts = np.unique(list(zip(home_goals, away_goals)), axis=0, return_counts=True)
        top_scores_idx = np.argsort(counts)[::-1][:3]
        top_scores = [f"{scores[i][0]}-{scores[i][1]} ({counts[i]/self.n_sims*100:.1f}%)" for i in top_scores_idx]

        return {
            'home_win_prob': round((home_wins / self.n_sims) * 100, 2),
            'draw_prob': round((draws / self.n_sims) * 100, 2),
            'away_win_prob': round((away_wins / self.n_sims) * 100, 2),
            'top_scores': ", ".join(top_scores)
        }
