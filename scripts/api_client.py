"""API-Football (v3.football.api-sports.io) への薄いHTTPラッパー。

無料プランは1日100リクエスト・1分10リクエストの上限がある。
また、レート超過やプラン制限のエラーはHTTP 200のままレスポンスJSONの
"errors" フィールドに載って返ってくる(HTTPステータスだけでは判定できない)ため、
毎回レスポンスボディのerrorsを確認する必要がある。
"""

import os
import time

import requests
from dotenv import load_dotenv

from config import API_BASE_URL

load_dotenv()
_API_KEY = os.environ.get("API_FOOTBALL_KEY")

request_count = 0

# 無料プランは1分10リクエストまで。安全マージンを取って1リクエストあたり7秒間隔にする。
_MIN_INTERVAL_SEC = 7.0
_last_request_at = 0.0


def _headers():
    if not _API_KEY:
        raise RuntimeError("環境変数 API_FOOTBALL_KEY が設定されていません")
    return {"x-apisports-key": _API_KEY}


def _throttle():
    global _last_request_at
    elapsed = time.monotonic() - _last_request_at
    wait = _MIN_INTERVAL_SEC - elapsed
    if wait > 0:
        time.sleep(wait)
    _last_request_at = time.monotonic()


def _is_rate_limit_error(errors) -> bool:
    if isinstance(errors, dict):
        return "rateLimit" in errors
    return False


def _get(path: str, params: dict) -> dict:
    global request_count
    url = f"{API_BASE_URL}{path}"
    for attempt in range(4):
        _throttle()
        resp = requests.get(url, headers=_headers(), params=params, timeout=15)
        request_count += 1
        if resp.status_code == 429:
            raise RuntimeError(
                f"API-Footballの1日リクエスト上限に達しました (path={path}, params={params})"
            )
        resp.raise_for_status()
        body = resp.json()
        errors = body.get("errors")
        if errors:
            if _is_rate_limit_error(errors) and attempt < 3:
                time.sleep(65)  # 1分あたりのレート制限が明けるのを待つ
                continue
            raise RuntimeError(f"API-Footballエラー: {errors} (path={path}, params={params})")
        return body
    raise RuntimeError(f"レート制限のリトライ上限に達しました (path={path}, params={params})")


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


def get_fixtures_by_date(date_str: str) -> list[dict]:
    """指定日(YYYY-MM-DD)の世界中の全試合を返す。

    無料プランでは /fixtures?team=X&next=N や season指定の未来日程取得が
    ブロックされているため、日付だけを指定して全件取得し、呼び出し側で
    対象チームにマッチするものを絞り込む方式を取る。
    """
    data = _get("/fixtures", {"date": date_str})
    return data.get("response", [])
