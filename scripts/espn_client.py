"""ESPNの非公式サッカーAPI (site.api.espn.com) への薄いHTTPラッパー。

注意: これはESPNが公式に公開・保証しているAPIではなく、ESPN公式サイトが
内部で利用しているエンドポイントを間借りする形で使っている。
予告なく仕様変更・提供終了する可能性があるため、失敗時は例外を投げて
早期に気づけるようにする。APIキーやレート制限の公式情報が無いため、
サーバーへの配慮として1リクエストごとに間隔を空ける。
"""

import time

import requests

from config import ESPN_BASE_URL

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}
_MIN_INTERVAL_SEC = 0.5
_last_request_at = 0.0

request_count = 0


def _throttle():
    global _last_request_at
    elapsed = time.monotonic() - _last_request_at
    wait = _MIN_INTERVAL_SEC - elapsed
    if wait > 0:
        time.sleep(wait)
    _last_request_at = time.monotonic()


def _get(path: str, params: dict | None = None) -> dict:
    global request_count
    _throttle()
    resp = requests.get(f"{ESPN_BASE_URL}{path}", headers=_HEADERS, params=params, timeout=15)
    request_count += 1
    resp.raise_for_status()
    return resp.json()


def get_teams(league_slug: str) -> list[dict]:
    """指定リーグの全チームを返す ([{id, name, logo}, ...])。"""
    data = _get(f"/{league_slug}/teams")
    leagues = data.get("sports", [{}])[0].get("leagues", [{}])
    if not leagues:
        return []
    teams = []
    for item in leagues[0].get("teams", []):
        t = item["team"]
        logo = next((l["href"] for l in t.get("logos", []) if "default" in l.get("rel", [])), None)
        teams.append({"id": t["id"], "name": t["displayName"], "logo": logo})
    return teams


def get_roster(league_slug: str, team_id: str) -> list[dict]:
    """指定チームの登録選手一覧を返す([{name, citizenship, position}, ...])。"""
    data = _get(f"/{league_slug}/teams/{team_id}/roster")
    players = []
    for a in data.get("athletes", []):
        players.append(
            {
                "name": a.get("fullName"),
                "citizenship": a.get("citizenship"),
                "position": (a.get("position") or {}).get("displayName"),
            }
        )
    return players


def get_fixtures(league_slug: str, date_from: str, date_to: str) -> list[dict]:
    """指定リーグの指定期間(YYYYMMDD形式)の試合一覧を返す。"""
    data = _get(f"/{league_slug}/scoreboard", params={"dates": f"{date_from}-{date_to}"})
    matches = []
    for event in data.get("events", []):
        comp = event["competitions"][0]
        home = next(c for c in comp["competitors"] if c["homeAway"] == "home")
        away = next(c for c in comp["competitors"] if c["homeAway"] == "away")

        def _logo(team):
            return team["team"].get("logo")

        matches.append(
            {
                "fixture_id": event["id"],
                "kickoff_utc": event["date"],
                "venue": (comp.get("venue") or {}).get("fullName"),
                "round": None,
                "home_team_id": home["team"]["id"],
                "home_team": home["team"]["displayName"],
                "home_logo": _logo(home),
                "away_team_id": away["team"]["id"],
                "away_team": away["team"]["displayName"],
                "away_logo": _logo(away),
            }
        )
    return matches
