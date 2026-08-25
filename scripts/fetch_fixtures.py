"""jp_clubs.json に登録されたクラブの直近試合予定を取得する。

使い方:
    python fetch_fixtures.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import api_client

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CLUBS_PATH = DATA_DIR / "jp_clubs.json"
OUTPUT_PATH = DATA_DIR / "fixtures.json"

NEXT_N_MATCHES = 8


def main() -> None:
    if not CLUBS_PATH.exists():
        print(f"{CLUBS_PATH} が見つかりません。先に discover_jp_clubs.py を実行してください。", file=sys.stderr)
        sys.exit(1)

    clubs_data = json.loads(CLUBS_PATH.read_text(encoding="utf-8"))
    clubs = clubs_data["clubs"]

    fixtures_by_club = []
    for club in clubs:
        fixtures = api_client.get_fixtures(club["team_id"], NEXT_N_MATCHES)
        matches = []
        for item in fixtures:
            fixture = item["fixture"]
            teams = item["teams"]
            league = item["league"]
            matches.append(
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
        fixtures_by_club.append(
            {
                "team_id": club["team_id"],
                "team_name": club["team_name"],
                "logo": club["logo"],
                "league_name": club["league_name"],
                "players": club["players"],
                "matches": matches,
            }
        )

    output = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "clubs": fixtures_by_club,
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"完了: {len(fixtures_by_club)}クラブの試合予定を {OUTPUT_PATH} に出力しました。")


if __name__ == "__main__":
    main()
