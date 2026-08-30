"""サッカーキング(soccer-king.jp)から日本人選手所属クラブ一覧を取得する。

https://www.soccer-king.jp/league/japanese には、対象リーグに関わらず
「海外クラブに所属する日本人選手」の一覧(選手名+所属クラブ名(日本語))と、
「所属クラブ」一覧(クラブ名(日本語)+英語公式名)が掲載されている。
これを1回スクレイピングするだけで、API-Footballの全チーム総当たりスキャン
(全チームのスカッドを走査する旧方式、1日100リクエストの上限を数日かけて消費する)を
行わずに対象クラブを特定できる。

API-Footballへのリクエストは一切発生しない(このスクリプト単体では
クオータを消費しない)。robots.txtでもこのページのクロールは許可されている
(Crawl-delay: 10秒のみ、対象ページはDisallowに含まれない)。

出力: data/soccerking_players.json
    {"scraped_at": ..., "players": [{"name_ja": "酒井宏樹", "club_name_ja": "オークランドFC"}, ...],
     "club_name_map": {"オークランドFC": "Auckland FC", ...}}

このファイルを scripts/resolve_jp_clubs.py が読み込み、API-Footballで
クラブ名からteam_idを解決してdata/jp_clubs.jsonを生成する。

使い方:
    python scrape_jp_clubs.py
"""

import html
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SOURCE_URL = "https://www.soccer-king.jp/league/japanese"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_PATH = DATA_DIR / "soccerking_players.json"

PLAYER_ITEM_RE = re.compile(
    r'<div>\s*([^<]+?)<br>\s*<b class="team--players-japanese--team">([^<]+)</b>'
)
CLUB_NAME_RE = re.compile(
    r'<div class="name__jp">([^<]+)</div>\s*<div class="name__abc">([^<]+)</div>'
)


def _clean(text: str) -> str:
    return html.unescape(text).strip()


def fetch_html() -> str:
    resp = requests.get(
        SOURCE_URL,
        headers={"User-Agent": "Mozilla/5.0 (compatible; JapanAbroadBot/1.0)"},
        timeout=20,
    )
    resp.raise_for_status()
    return resp.text


def parse(html_text: str) -> tuple[list[dict], dict[str, str]]:
    players = [
        {"name_ja": _clean(name), "club_name_ja": _clean(club)}
        for name, club in PLAYER_ITEM_RE.findall(html_text)
    ]
    club_name_map = {
        _clean(name_ja): _clean(name_en) for name_ja, name_en in CLUB_NAME_RE.findall(html_text)
    }
    return players, club_name_map


def main() -> None:
    html_text = fetch_html()
    players, club_name_map = parse(html_text)

    if not players:
        print("エラー: 選手一覧を取得できませんでした。ページ構造が変わった可能性があります。", file=sys.stderr)
        sys.exit(1)

    unresolved = sorted({p["club_name_ja"] for p in players} - set(club_name_map))
    if unresolved:
        print(f"注意: 英語名が見つからないクラブが{len(unresolved)}件あります: {unresolved}")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output = {
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "source_url": SOURCE_URL,
        "players": players,
        "club_name_map": club_name_map,
    }
    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"完了: 選手{len(players)}人・クラブ{len(club_name_map)}件を "
        f"{OUTPUT_PATH} に出力しました。"
    )


if __name__ == "__main__":
    main()
