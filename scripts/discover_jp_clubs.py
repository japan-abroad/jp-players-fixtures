"""日本人選手が所属する欧州クラブを動的に発見するスクリプト(ESPN版)。

ESPNのroster APIには国籍(citizenship)が含まれているため、
API-Football版で必要だった名字リストとの照合は不要になった。
ESPNには明確な1日あたりのリクエスト上限が無い(公式情報なし)ため、
基本的に1回の実行で全チームをスキャンし切る想定だが、万一の中断に
備えて進捗は都度保存し、再実行すれば続きから再開できるようにする。

使い方:
    python discover_jp_clubs.py
"""

import json
import sys
from pathlib import Path

import espn_client
from config import JAPAN_CITIZENSHIP, LEAGUES

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PROGRESS_PATH = DATA_DIR / "discover_progress.json"
OUTPUT_PATH = DATA_DIR / "jp_clubs.json"


def _load_progress() -> dict | None:
    if not PROGRESS_PATH.exists():
        return None
    return json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))


def _init_progress() -> dict:
    pending = []
    for league in LEAGUES:
        teams = espn_client.get_teams(league["espn_slug"])
        for team in teams:
            pending.append(
                {
                    "team_id": team["id"],
                    "team_name": team["name"],
                    "logo": team["logo"],
                    "espn_slug": league["espn_slug"],
                    "league_name": league["name"],
                }
            )
    return {"pending_teams": pending, "found_clubs": {}}


def _save_progress(progress: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROGRESS_PATH.write_text(
        json.dumps(progress, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _write_output(found_clubs: dict) -> None:
    clubs = sorted(found_clubs.values(), key=lambda c: c["team_name"])
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps({"clubs": clubs}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    progress = _load_progress() or _init_progress()
    _save_progress(progress)

    pending = progress["pending_teams"]
    found_clubs = progress["found_clubs"]

    while pending:
        team = pending.pop(0)
        roster = espn_client.get_roster(team["espn_slug"], team["team_id"])
        jp_players = [
            {"name": p["name"], "position": p.get("position")}
            for p in roster
            if p.get("citizenship") == JAPAN_CITIZENSHIP
        ]
        if jp_players:
            found_clubs[str(team["team_id"])] = {
                "team_id": team["team_id"],
                "team_name": team["team_name"],
                "logo": team["logo"],
                "espn_slug": team["espn_slug"],
                "league_name": team["league_name"],
                "players": jp_players,
            }
            print(f"  発見: {team['team_name']} - {[p['name'] for p in jp_players]}")
        _save_progress(progress)

    _write_output(found_clubs)
    PROGRESS_PATH.unlink(missing_ok=True)
    print(f"完了: {len(found_clubs)}クラブを検出し {OUTPUT_PATH} に出力しました。")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        print(f"エラー: {exc}", file=sys.stderr)
        print("進捗は保存済みです。再度実行すれば続きから再開します。", file=sys.stderr)
        sys.exit(1)
