"""ゲキサカ(web.gekisaka.jp)の「海外組ガイド」から日本人選手所属クラブ一覧を取得する。

soccer-king.jp(scripts/scrape_jp_clubs.py)を一次情報源としているが、
soccer-king側は移籍から数週間〜数ヶ月遅れて掲載されるケースがある
(2026-09-06発覚: 佐藤龍之介のバレンシア加入(2026-07)が2ヶ月経っても
未掲載だった)。ゲキサカの「海外組ガイド」は同じ抜けを補完できることを
確認済みのため、2つ目のソースとして追加する。

対象はプレミアリーグ/ラ・リーガ/セリエA/ブンデスリーガ/リーグアン/
エールディビジ/ベルギー・リーグの主要7リーグのみ(soccer-kingより
カバー範囲は狭いが、この7リーグに関しては移籍反映が速い傾向がある)。

このページのrobots.txtは"User-Agent: *"に対し"/search*"以外を許可している
(https://web.gekisaka.jp/robots.txt で確認済み)。

出力: data/gekisaka_players.json
    {"scraped_at": ..., "source_url": ...,
     "players": [{"name_ja": "佐藤龍之介", "club_name_ja": "バレンシア",
                  "gekisaka_club_id": "673"}, ...]}

このファイルは scripts/resolve_jp_clubs.py が読み込み、soccer-king側の
データに無い選手・クラブを補完する。

使い方:
    python scrape_gekisaka_players.py
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SOURCE_URL = "https://web.gekisaka.jp/pickup/detail/?116647-72690-fl"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_PATH = DATA_DIR / "gekisaka_players.json"

# 各選手名の直前にある <a name="選手ID" class="anchor-link"></a> と、
# 直後の(所属クラブへのリンク)をセットで拾う。育成年代・国内組との混同を
# 避けるため、「海外組ガイド」ページ本文中の該当形式のみが対象。
PLAYER_ITEM_RE = re.compile(
    r'<a name="\d+" class="anchor-link"></a>'
    r'<a href="[^"]*">([^<]+)</a>'
    r'\(<a href="[^"]*club_id=\d+">([^<]+)</a>\)'
)


def fetch_html() -> str:
    resp = requests.get(
        SOURCE_URL,
        headers={"User-Agent": "Mozilla/5.0 (compatible; JapanAbroadBot/1.0)"},
        timeout=20,
    )
    resp.raise_for_status()
    return resp.text


def parse(html_text: str) -> list[dict]:
    return [
        {"name_ja": name.strip(), "club_name_ja": club.strip()}
        for name, club in PLAYER_ITEM_RE.findall(html_text)
    ]


def main() -> None:
    html_text = fetch_html()
    players = parse(html_text)

    if not players:
        print("エラー: 選手一覧を取得できませんでした。ページ構造が変わった可能性があります。", file=sys.stderr)
        sys.exit(1)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output = {
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "source_url": SOURCE_URL,
        "players": players,
    }
    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"完了: 選手{len(players)}人を {OUTPUT_PATH} に出力しました。")


if __name__ == "__main__":
    main()
