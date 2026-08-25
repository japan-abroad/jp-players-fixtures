"""日本人選手が所属する欧州クラブを動的に発見するスクリプト。

無料APIプラン(1日100リクエスト)の制約に対応するため、--max-requests で
1回の実行あたりのAPI呼び出し数に上限を設け、進捗を data/discover_progress.json に
保存して複数回の実行(=複数日のcron実行)にまたがって完走できるようにする。

使い方:
    python discover_jp_clubs.py --max-requests 90
"""

import argparse
import json
import sys
from pathlib import Path

import api_client
from config import FREE_PLAN_SEASON, JAPANESE_SURNAMES, LEAGUES

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PROGRESS_PATH = DATA_DIR / "discover_progress.json"
OUTPUT_PATH = DATA_DIR / "jp_clubs.json"


def _is_japanese_player(name: str) -> bool:
    # API-Footballの選手名は "K. Mitoma" のように「頭文字. 名字」形式で入っている
    surname = name.split(".")[-1].strip() if "." in name else name
    return surname in JAPANESE_SURNAMES


def _load_progress() -> dict | None:
    if not PROGRESS_PATH.exists():
        return None
    progress = json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))
    if progress.get("season") != FREE_PLAN_SEASON:
        return None
    return progress


def _init_progress() -> dict:
    pending = []
    for league in LEAGUES:
        teams = api_client.get_teams(league["id"], FREE_PLAN_SEASON)
        for team in teams:
            pending.append(
                {
                    "team_id": team["id"],
                    "team_name": team["name"],
                    "logo": team.get("logo"),
                    "league_id": league["id"],
                    "league_name": league["name"],
                }
            )
    return {"season": FREE_PLAN_SEASON, "pending_teams": pending, "found_clubs": {}}


def _save_progress(progress: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROGRESS_PATH.write_text(
        json.dumps(progress, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _write_output(found_clubs: dict) -> None:
    clubs = sorted(found_clubs.values(), key=lambda c: c["team_name"])
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps({"season": FREE_PLAN_SEASON, "clubs": clubs}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main(max_requests: int) -> None:
    progress = _load_progress() or _init_progress()
    _save_progress(progress)

    pending = progress["pending_teams"]
    found_clubs = progress["found_clubs"]

    while pending and api_client.request_count < max_requests:
        team = pending.pop(0)
        squad = api_client.get_squad(team["team_id"])
        jp_players = [
            {"name": p["name"], "position": p.get("position")}
            for p in squad
            if _is_japanese_player(p["name"])
        ]
        if jp_players:
            found_clubs[str(team["team_id"])] = {
                "team_id": team["team_id"],
                "team_name": team["team_name"],
                "logo": team["logo"],
                "league_id": team["league_id"],
                "league_name": team["league_name"],
                "players": jp_players,
            }
        _save_progress(progress)

    if pending:
        print(
            f"進捗保存: 残り{len(pending)}チーム未確認 "
            f"(今回{api_client.request_count}リクエスト消費)。再度実行して続きを処理してください。"
        )
    else:
        _write_output(found_clubs)
        PROGRESS_PATH.unlink(missing_ok=True)
        print(f"完了: {len(found_clubs)}クラブを検出し {OUTPUT_PATH} に出力しました。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-requests", type=int, default=90)
    args = parser.parse_args()
    try:
        main(args.max_requests)
    except Exception as exc:  # noqa: BLE001
        print(f"エラー: {exc}", file=sys.stderr)
        sys.exit(1)
