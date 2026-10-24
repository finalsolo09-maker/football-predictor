import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import poisson

class FeaturePipeline:
    def __init__(self):
        pass

    def calculate_rolling_features(self, df_matches, window=5):
        """
        최근 N경기(기본 5경기)의 npxG, xGA 롤링 이동평균을 계산합니다.
        """
        df = df_matches.copy()
        # 최근 폼 수치화
        df['home_npxG_roll'] = df['home_npxG'].rolling(window=window, min_periods=1).mean()
        df['away_npxG_roll'] = df['away_npxG'].rolling(window=window, min_periods=1).mean()
        df['home_xGA_roll'] = df['home_xGA'].rolling(window=window, min_periods=1).mean()
        df['away_xGA_roll'] = df['away_xGA'].rolling(window=window, min_periods=1).mean()
        return df

    def fit_dixon_coles(self, df_history):
        """
        최근 경기 기록을 바탕으로 각 팀의 Dixon-Coles 공격력(alpha), 수비력(beta),
        홈 이점(gamma), 저득점 보정계수(rho)를 수치 최적화(L-BFGS-B)로 산출합니다.
        """
        teams = np.unique(np.concatenate([df_history['home_team'], df_history['away_team']]))
        n_teams = len(teams)
        team_map = {team: i for i, team in enumerate(teams)}
        
        init_params = np.concatenate([
            np.ones(n_teams) * 0.1,   # alpha (공격력)
            np.ones(n_teams) * -0.1,  # beta (수비력)
            [0.25],                    # gamma (홈 이점)
            [-0.05]                    # rho (저득점 보정계수)
        ])

        def log_likelihood(params):
            att = params[:n_teams]
            defe = params[n_teams:2*n_teams]
            home_adv = params[-2]
            rho = params[-1]
            
            ll = 0
            for _, row in df_history.iterrows():
                h_idx = team_map.get(row['home_team'])
                a_idx = team_map.get(row['away_team'])
                if h_idx is None or a_idx is None:
                    continue
                
                lambda_h = np.exp(att[h_idx] + defe[a_idx] + home_adv)
                lambda_a = np.exp(att[a_idx] + defe[h_idx])
                
                prob_h = poisson.pmf(row['home_goals'], lambda_h)
                prob_a = poisson.pmf(row['away_goals'], lambda_a)
                
                # 저득점 상호의존성 보정
                adj = 1.0
                x, y = row['home_goals'], row['away_goals']
                if x == 0 and y == 0:
                    adj = 1 - (lambda_h * lambda_a * rho)
                elif x == 0 and y == 1:
                    adj = 1 + (lambda_h * rho)
                elif x == 1 and y == 0:
                    adj = 1 + (lambda_a * rho)
                elif x == 1 and y == 1:
                    adj = 1 - rho
                    
                p = max(prob_h * prob_a * adj, 1e-10)
                ll -= np.log(p)
            return ll

        res = minimize(log_likelihood, init_params, method='L-BFGS-B')
        
        # 파라미터 추출
        att = res.x[:n_teams]
        defe = res.x[n_teams:2*n_teams]
        home_adv = res.x[-2]
        
        return {team: {'att': att[i], 'def': defe[i]} for team, i in team_map.items()}, home_adv
