"""試合予定を取得する(ESPN版)。

サイトの一覧は「対象リーグの全試合」を表示し、日本人選手が所属するクラブの
試合にはタグを付けて強調する方式にした(以前は日本人選手所属クラブの
試合だけに絞り込んでいたが、それ以外の試合も見たいという要望に対応)。

ESPNの/scoreboardは「リーグ単位・期間指定」で全試合を1リクエストで返すため、
対象リーグの数だけリクエストすればよい。

使い方:
    python fetch_fixtures.py
"""

import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import espn_client
from config import LEAGUES

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CLUBS_PATH = DATA_DIR / "jp_clubs.json"
OUTPUT_PATH = DATA_DIR / "fixtures.json"

DAYS_AHEAD = 14


def main() -> None:
    if not CLUBS_PATH.exists():
        print(f"{CLUBS_PATH} が見つかりません。先に discover_jp_clubs.py を実行してください。", file=sys.stderr)
        sys.exit(1)

    clubs_data = json.loads(CLUBS_PATH.read_text(encoding="utf-8"))
    clubs = clubs_data["clubs"]
    club_by_team_id = {str(c["team_id"]): c for c in clubs}

    today = date.today()
    date_from = today.strftime("%Y%m%d")
    date_to = (today + timedelta(days=DAYS_AHEAD)).strftime("%Y%m%d")

    # 同じリーグを複数回叩かないよう espn_slug でまとめて処理する
    seen_slugs: dict[str, dict] = {}
    for league in LEAGUES:
        seen_slugs.setdefault(league["espn_slug"], league)

    matches_by_team: dict[str, list[dict]] = {team_id: [] for team_id in club_by_team_id}
    all_matches: list[dict] = []

    for slug, league in seen_slugs.items():
        fixtures = espn_client.get_fixtures(slug, date_from, date_to)
        for m in fixtures:
            home_id = str(m["home_team_id"])
            away_id = str(m["away_team_id"])

            jp_players = []
            for team_id in (home_id, away_id):
                club = club_by_team_id.get(team_id)
                if club:
                    jp_players.extend(
                        {"name": p["name"], "team_id": club["team_id"]} for p in club["players"]
                    )

            match = {
                "fixture_id": m["fixture_id"],
                "kickoff_utc": m["kickoff_utc"],
                "venue": m["venue"],
                "league_name": league["name"],
                "country_code": league["country_code"],
                "country_ja": league["country_ja"],
                "round": m["round"],
                "home_team_id": m["home_team_id"],
                "home_team": m["home_team"],
                "home_logo": m["home_logo"],
                "away_team_id": m["away_team_id"],
                "away_team": m["away_team"],
                "away_logo": m["away_logo"],
                "jp_players": jp_players,
            }
            all_matches.append(match)

            for team_id in (home_id, away_id):
                if team_id in matches_by_team:
                    matches_by_team[team_id].append(match)

    all_matches.sort(key=lambda m: m["kickoff_utc"])

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
        "matches": all_matches,
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    jp_count = sum(1 for m in all_matches if m["jp_players"])
    print(
        f"完了: 全{len(all_matches)}試合(うち日本人選手所属{jp_count}試合)を {OUTPUT_PATH} に出力しました。"
    )


if __name__ == "__main__":
    main()
