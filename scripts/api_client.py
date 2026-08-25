"""API-Football (v3.football.api-sports.io) への薄いHTTPラッパー。

無料プランは1日100リクエストの上限があるため、呼び出し側でリクエスト数を
数えられるようにグローバルカウンタを持つ。429が返った場合は少し待って1回だけ再試行する。
"""

import os
import time

import requests
from dotenv import load_dotenv

from config import API_BASE_URL

load_dotenv()
_API_KEY = os.environ.get("API_FOOTBALL_KEY")

request_count = 0


def _headers():
    if not _API_KEY:
        raise RuntimeError("環境変数 API_FOOTBALL_KEY が設定されていません")
    return {"x-apisports-key": _API_KEY}


def _get(path: str, params: dict) -> dict:
    global request_count
    url = f"{API_BASE_URL}{path}"
    for attempt in range(2):
        resp = requests.get(url, headers=_headers(), params=params, timeout=15)
        request_count += 1
        if resp.status_code == 429:
            time.sleep(20)
            continue
        resp.raise_for_status()
        time.sleep(0.3)  # 簡易スロットリング
        return resp.json()
    resp.raise_for_status()
    return resp.json()


def get_teams(league_id: int, season: int) -> list[dict]:
    """指定リーグ・シーズンに所属するチーム一覧を返す。"""
    data = _get("/teams", {"league": league_id, "season": season})
    return [item["team"] for item in data.get("response", [])]


def get_squad(team_id: int) -> list[dict]:
    """指定チームの登録選手一覧(国籍含む)を返す。"""
    data = _get("/players/squads", {"team": team_id})
    response = data.get("response", [])
    if not response:
        return []
    return response[0].get("players", [])


def get_fixtures(team_id: int, next_n: int = 10) -> list[dict]:
    """指定チームの直近の試合予定を返す。"""
    data = _get("/fixtures", {"team": team_id, "next": next_n})
    return data.get("response", [])
