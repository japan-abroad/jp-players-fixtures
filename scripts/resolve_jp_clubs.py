"""scrape_jp_clubs.py の出力(クラブ名一覧)をAPI-Footballのteam_idに解決する。

data/soccerking_players.json の各クラブ(英語公式名)について
/teams?search=<name> を1回だけ叩いてteam_id・ロゴ・国を取得する。
一度解決したクラブはdata/team_id_cache.jsonに保存され、次回以降は
再リクエストしない(クラブ名が変わらない限り恒久的に再利用できる)。

discover_jp_clubs.py同様、残りクオータを自動検出して安全マージンを
引いた範囲でのみ実行し、中断しても次回実行時に続きから再開する。

使い方:
    python resolve_jp_clubs.py            # 残りクオータを自動検出して実行
    python resolve_jp_clubs.py --max-requests 20
"""

import argparse
import json
import sys
from pathlib import Path

import api_client
from config import COUNTRY_JA, COUNTRY_TOP_LEAGUE_JA, FREE_PLAN_SEASON

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PLAYERS_PATH = DATA_DIR / "soccerking_players.json"
CACHE_PATH = DATA_DIR / "team_id_cache.json"
OUTPUT_PATH = DATA_DIR / "jp_clubs.json"


def _load_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def _save_cache(cache: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def _resolve_team(name_en: str) -> dict | None:
    candidates = api_client.search_team(name_en)
    if not candidates:
        return None
    team = candidates[0]
    country_ja = COUNTRY_JA.get(team.get("country"), team.get("country") or "")
    return {
        "team_id": team["id"],
        "team_name": team["name"],
        "logo": team.get("logo"),
        "country_code": (team.get("country") or "")[:3].lower(),
        "country_ja": country_ja,
        "league_name": COUNTRY_TOP_LEAGUE_JA.get(country_ja, country_ja),
    }


def main(max_requests: int | None) -> None:
    if not PLAYERS_PATH.exists():
        print(f"{PLAYERS_PATH} が見つかりません。先に scrape_jp_clubs.py を実行してください。", file=sys.stderr)
        sys.exit(1)

    if max_requests is None:
        remaining = api_client.get_remaining_quota()
        max_requests = max(remaining - api_client.SAFETY_MARGIN, 0)
        print(f"残りクオータ: {remaining} (安全マージン{api_client.SAFETY_MARGIN}を引いた{max_requests}まで使用)")
        if max_requests <= 0:
            print("今日はこれ以上実行できません。日を改めて再実行してください。")
            return

    scraped = json.loads(PLAYERS_PATH.read_text(encoding="utf-8"))
    club_name_map: dict[str, str] = scraped["club_name_map"]
    players_by_club_ja: dict[str, list[dict]] = {}
    for p in scraped["players"]:
        players_by_club_ja.setdefault(p["club_name_ja"], []).append({"name": p["name_ja"], "position": None})

    cache: dict[str, dict] = _load_json(CACHE_PATH, {})

    pending = [
        (club_ja, name_en)
        for club_ja, name_en in club_name_map.items()
        if name_en not in cache
    ]

    while pending and api_client.request_count < max_requests:
        club_ja, name_en = pending.pop(0)
        resolved = _resolve_team(name_en)
        if resolved is None:
            print(f"  未解決: {club_ja} ({name_en}) - 検索結果0件")
            cache[name_en] = {"unresolved": True}
        else:
            cache[name_en] = resolved
            print(f"  解決: {club_ja} -> {resolved['team_name']} (id={resolved['team_id']})")
        _save_cache(cache)

    if pending:
        print(
            f"進捗保存: 残り{len(pending)}クラブ未解決 "
            f"(今回{api_client.request_count}リクエスト消費)。再度実行して続きを処理してください。"
        )
        return

    clubs = []
    for club_ja, name_en in club_name_map.items():
        resolved = cache.get(name_en)
        if not resolved or resolved.get("unresolved"):
            continue
        clubs.append(
            {
                "team_id": resolved["team_id"],
                "team_name": resolved["team_name"],
                "logo": resolved["logo"],
                "league_name": resolved["league_name"],
                "country_code": resolved["country_code"],
                "country_ja": resolved["country_ja"],
                "players": players_by_club_ja.get(club_ja, []),
            }
        )
    clubs.sort(key=lambda c: c["team_name"])

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps({"season": FREE_PLAN_SEASON, "clubs": clubs}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"完了: {len(clubs)}クラブを {OUTPUT_PATH} に出力しました。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-requests", type=int, default=None)
    args = parser.parse_args()
    try:
        main(args.max_requests)
    except Exception as exc:  # noqa: BLE001
        print(f"エラー: {exc}", file=sys.stderr)
        print("進捗(キャッシュ)は保存済みです。再度実行すれば続きから再開します。", file=sys.stderr)
        sys.exit(1)
