"""IndexNow(Bing/Yandex等)にサイト更新を即時通知する。

fixtures.jsonの更新は既存ページ(トップ・クラブ/選手ページ)の内容を
変えるだけで新規URLは増えないため、対象は「主要な一覧・詳細ページ全て」
とする。1リクエストで最大10,000件まで送れるため、まとめて1回で送信する。

使い方:
    python notify_indexnow.py
"""

import json
import sys
from pathlib import Path

import requests

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CLUBS_PATH = DATA_DIR / "jp_clubs.json"

HOST = "japan-abroad.github.io"
SITE_URL = f"https://{HOST}/jp-players-fixtures"
INDEXNOW_KEY = "e8b7c55740f7c206cf4fe095cd83f37a"
KEY_LOCATION = f"{SITE_URL}/{INDEXNOW_KEY}.txt"
INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"


def build_url_list() -> list[str]:
    urls = [f"{SITE_URL}/", f"{SITE_URL}/clubs/", f"{SITE_URL}/players/"]

    if not CLUBS_PATH.exists():
        print(f"警告: {CLUBS_PATH} が見つからないため、クラブ/選手ページは通知対象から除外します。", file=sys.stderr)
        return urls

    clubs_data = json.loads(CLUBS_PATH.read_text(encoding="utf-8"))
    for club in clubs_data["clubs"]:
        urls.append(f"{SITE_URL}/clubs/{club['team_id']}/")
        for i in range(len(club["players"])):
            urls.append(f"{SITE_URL}/players/{club['team_id']}-{i}/")
    return urls


def main() -> None:
    url_list = build_url_list()
    payload = {
        "host": HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": url_list,
    }
    resp = requests.post(INDEXNOW_ENDPOINT, json=payload, timeout=20)
    print(f"IndexNow通知: {len(url_list)}件のURLを送信、ステータスコード={resp.status_code}")
    if resp.status_code >= 400:
        print(resp.text, file=sys.stderr)


if __name__ == "__main__":
    main()
