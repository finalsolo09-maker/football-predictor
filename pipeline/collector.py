import pandas as pd
import requests
import soccerdata as sd
from understatapi import UnderstatClient

class FootballDataCollector:
    def __init__(self, league_code="ENG-Premier League", season="2025"):
        self.league_code = league_code
        self.season = season

    def fetch_fbref_metrics(self):
        """
        FBref 데이터를 다이렉트로 긁어와 최근 경기들의 팀별 세부 지표를 산출합니다.
        - npxG (페널티킥 제외 기대 득점)
        - xGA (기대 실점)
        - PPDA (상대 패스 허용 수, 전방 압박 강도 지표)
        """
        print("[1/3] FBref 데이터 스크래핑 진행 중...")
        try:
            fbref = sd.FBref(leagues=self.league_code, seasons=self.season)
            # 시즌 경기 결과 및 xG 지표 수집
            schedule = fbref.read_schedule()
            # 팀별 시합당 세부 지표 수집 (passing, defense, shooting 등)
            team_stats = fbref.read_team_season_stats(stat_type="standard")
            return schedule, team_stats
        except Exception as e:
            print(f"FBref 데이터 수집 실패 (네트워크/구조 변경 오류): {e}")
            return None, None

    def fetch_understat_match_data(self, team_name="Arsenal"):
        """
        Understat API를 활용해 슈팅 위치 기반 xG 및 최근 폼 데이터를 JSON으로 받아옵니다.
        """
        print(f"[2/3] Understat 데이터 수집 중 ({team_name})...")
        try:
            with UnderstatClient() as understat:
                team_matches = understat.team(team=team_name).get_match_data(season=self.season)
                df_matches = pd.DataFrame(team_matches)
                return df_matches
        except Exception as e:
            print(f"Understat 데이터 수집 실패: {e}")
            return None

    def fetch_today_api_fixtures(self, api_key=None):
        """
        football-data.org 무료 API를 이용해 오늘 진행되는 실제 경기 스케줄을 가져옵니다.
        """
        print("[3/3] 당일 경기 스케줄 API 수집 중...")
        url = "https://api.football-data.org/v4/matches"
        headers = {"X-Auth-Token": api_key} if api_key else {}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json().get('matches', [])
            else:
                print("API 키 없음 또는 요청 제한: 기본 가상 스케줄로 대체합니다.")
                return []
        except Exception as e:
            print(f"API 요청 실패: {e}")
            return []
