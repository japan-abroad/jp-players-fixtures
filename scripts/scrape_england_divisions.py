"""Yahoo!スポーツ(soccer.yahoo.co.jp)からイングランド国内の実際の所属
ディビジョン(プレミアリーグ/チャンピオンシップ)を取得する。

API-Football無料プランはシーズン2022〜2024しか参照できず、config.pyの
ENGLAND_DIVISION_JA(/leagues?team=X&season=Y)による自動判定は2024-25
シーズン時点のディビジョンに固定されてしまう。シーズンが進むごとに
実態とズレていくため(2026-09-09発覚、Leeds/Hull City/Coventryが
プレミアリーグに昇格していたのにチャンピオンシップのままだった等)、
現在のシーズンの順位表を直接参照する方式に切り替える。

順位表ページ(https://soccer.yahoo.co.jp/ws/category/eng/standings?gk=52
がプレミアリーグ、gk=152がチャンピオンシップ)はJavaScript無効でも
サーバー側でチーム名・チームIDを含む完全な順位表が返る(要検証確認済み、
2026-09-09)。このスクリプトはAPI-Footballを一切使わない(クオータ消費なし)。

出力: data/england_divisions.json
    {"fetched_at": ..., "premier_league": ["ウェストハム", ...], "championship": [...]}

resolve_jp_clubs.pyがこのファイルを読み込み、team_name_ja(サッカーキング
側の表記)と正規化・エイリアス突き合わせでディビジョンを決定する。
一致しないクラブが出た場合はYAHOO_CLUB_JA_ALIASESで個別に吸収する。

使い方:
    python scrape_england_divisions.py
"""

import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_PATH = DATA_DIR / "england_divisions.json"

STANDINGS_URL = "https://soccer.yahoo.co.jp/ws/category/eng/standings"
DIVISIONS = [
    ("gk52", "プレミアリーグ", {"gk": "52"}),
    ("gk152", "チャンピオンシップ", {"gk": "152"}),
]
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

TEAM_ROW_RE = re.compile(
    r'class="sc-tableValue__team"\s+href="https://soccer\.yahoo\.co\.jp/ws/team/(\d+)"[^>]*>([^<]+)</a>',
    re.S,
)


def _fetch_division(params: dict) -> list[str]:
    resp = requests.get(STANDINGS_URL, headers=REQUEST_HEADERS, params=params, timeout=20)
    resp.raise_for_status()
    seen_ids: set[str] = set()
    names: list[str] = []
    for team_id, name in TEAM_ROW_RE.findall(resp.text):
        if team_id in seen_ids:
            continue
        seen_ids.add(team_id)
        names.append(unicodedata.normalize("NFKC", name).strip())
    return names


def main() -> None:
    result: dict[str, list[str]] = {}
    for key, label, params in DIVISIONS:
        names = _fetch_division(params)
        if not names:
            print(f"エラー: {label}の順位表を取得できませんでした。ページ構造が変わった可能性があります。", file=sys.stderr)
            sys.exit(1)
        result[key] = names
        print(f"{label}: {len(names)}チーム取得")

    output = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "premier_league": result["gk52"],
        "championship": result["gk152"],
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"完了: {OUTPUT_PATH} に出力しました。")


if __name__ == "__main__":
    main()
