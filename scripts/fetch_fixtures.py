"""試合予定を取得する(API-Football版)。

サイトの一覧は「対象リーグの全試合」を表示し、日本人選手が所属するクラブの
試合にはタグを付けて強調する。無料プランでは /fixtures?team=X&next=N が
使えないため、直近N日分について /fixtures?date=YYYY-MM-DD (全世界の試合)を
1日1リクエストで取得し、対象リーグの試合だけを抽出する。

このリクエスト数(日数分、クラブ数に依存しない)は discover に比べて
軽量なため、6時間毎の自動実行でも1日100リクエストの上限に収まる。

使い方:
    python fetch_fixtures.py
"""

import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import api_client
from config import COUNTRY_JA, FIXTURE_LEAGUES

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

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
    club_by_team_id = {str(c["team_id"]): c for c in clubs}
    league_by_id = {league["id"]: league for league in FIXTURE_LEAGUES}

    matches_by_team: dict[str, list[dict]] = {team_id: [] for team_id in club_by_team_id}
    all_matches: list[dict] = []
    seen_fixture_ids: set[int] = set()

    today = date.today()
    for offset in range(DAYS_AHEAD):
        day = today + timedelta(days=offset)
        fixtures = api_client.get_fixtures_by_date(day.isoformat())
        for item in fixtures:
            league_id = item["league"]["id"]
            league = league_by_id.get(league_id)

            teams = item["teams"]
            home_id = str(teams["home"]["id"])
            away_id = str(teams["away"]["id"])
            has_jp_club = home_id in club_by_team_id or away_id in club_by_team_id

            if league is None and not has_jp_club:
                continue  # 対象リーグ以外かつ日本人選手所属クラブも絡まない試合は無視

            fixture = item["fixture"]
            if fixture["id"] in seen_fixture_ids:
                continue
            seen_fixture_ids.add(fixture["id"])

            jp_players = []
            for team_id in (home_id, away_id):
                club = club_by_team_id.get(team_id)
                if club:
                    jp_players.extend(
                        {"name": p["name"], "team_id": club["team_id"]} for p in club["players"]
                    )

            if league is not None:
                league_name = league["name"]
                country_code = league["country_code"]
                country_ja = league["country_ja"]
            else:
                # 対象11リーグ以外(オセアニア・北米・アジア等)は日本人選手
                # 所属クラブの試合のみ拾うため、API側の英語名をそのまま使う
                league_name = item["league"]["name"]
                country_en = item["league"].get("country") or ""
                country_ja = COUNTRY_JA.get(country_en, country_en)
                country_code = country_en[:3].lower()

            match = {
                "fixture_id": fixture["id"],
                "kickoff_utc": fixture["date"],
                "venue": (fixture.get("venue") or {}).get("name"),
                "league_name": league_name,
                "country_code": country_code,
                "country_ja": country_ja,
                "round": item["league"].get("round"),
                "home_team_id": teams["home"]["id"],
                "home_team": teams["home"]["name"],
                "home_logo": teams["home"]["logo"],
                "away_team_id": teams["away"]["id"],
                "away_team": teams["away"]["name"],
                "away_logo": teams["away"]["logo"],
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
        f"完了: 全{len(all_matches)}試合(うち日本人選手所属{jp_count}試合)を "
        f"{api_client.request_count}リクエストで {OUTPUT_PATH} に出力しました。"
    )


if __name__ == "__main__":
    main()
