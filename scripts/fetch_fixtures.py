"""jp_clubs.json に登録されたクラブの直近試合予定を取得する。

無料プランでは /fixtures?team=X&next=N が使えないため、直近N日分について
/fixtures?date=YYYY-MM-DD (全世界の試合)を1日1リクエストで取得し、
対象クラブが関わる試合だけを抽出する。

使い方:
    python fetch_fixtures.py
"""

import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import api_client

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CLUBS_PATH = DATA_DIR / "jp_clubs.json"
OUTPUT_PATH = DATA_DIR / "fixtures.json"

DAYS_AHEAD = 10


def main() -> None:
    if not CLUBS_PATH.exists():
        print(f"{CLUBS_PATH} が見つかりません。先に discover_jp_clubs.py を実行してください。", file=sys.stderr)
        sys.exit(1)

    clubs_data = json.loads(CLUBS_PATH.read_text(encoding="utf-8"))
    clubs = clubs_data["clubs"]
    club_by_team_id = {c["team_id"]: c for c in clubs}

    matches_by_team: dict[int, list[dict]] = {team_id: [] for team_id in club_by_team_id}

    today = date.today()
    for offset in range(DAYS_AHEAD):
        day = today + timedelta(days=offset)
        fixtures = api_client.get_fixtures_by_date(day.isoformat())
        for item in fixtures:
            home_id = item["teams"]["home"]["id"]
            away_id = item["teams"]["away"]["id"]
            target_id = home_id if home_id in club_by_team_id else (
                away_id if away_id in club_by_team_id else None
            )
            if target_id is None:
                continue
            fixture = item["fixture"]
            teams = item["teams"]
            league = item["league"]
            matches_by_team[target_id].append(
                {
                    "fixture_id": fixture["id"],
                    "kickoff_utc": fixture["date"],
                    "venue": (fixture.get("venue") or {}).get("name"),
                    "league_name": league.get("name"),
                    "round": league.get("round"),
                    "home_team": teams["home"]["name"],
                    "home_logo": teams["home"]["logo"],
                    "away_team": teams["away"]["name"],
                    "away_logo": teams["away"]["logo"],
                }
            )

    fixtures_by_club = []
    for team_id, club in club_by_team_id.items():
        fixtures_by_club.append(
            {
                "team_id": club["team_id"],
                "team_name": club["team_name"],
                "logo": club["logo"],
                "league_name": club["league_name"],
                "players": club["players"],
                "matches": sorted(matches_by_team[team_id], key=lambda m: m["kickoff_utc"]),
            }
        )

    output = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "clubs": fixtures_by_club,
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    total_matches = sum(len(c["matches"]) for c in fixtures_by_club)
    print(f"完了: {len(fixtures_by_club)}クラブ・{total_matches}試合を {OUTPUT_PATH} に出力しました。")


if __name__ == "__main__":
    main()
