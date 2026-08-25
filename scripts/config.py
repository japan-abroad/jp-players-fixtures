"""対象リーグ・シーズン定義。

API-FootballのリーグIDは https://www.api-football.com/documentation-v3#tag/Leagues の
一覧、または /leagues エンドポイントで確認できる。
"""

import datetime

# 現在シーズンの開始年(欧州は秋開幕・年またぎのため8月以降は当年、それ以前は前年を使う)
_now = datetime.date.today()
CURRENT_SEASON = _now.year if _now.month >= 7 else _now.year - 1

# 日本人選手が所属しやすい欧州主要リーグ(1部)
LEAGUES = [
    {"id": 39, "name": "プレミアリーグ", "country": "England"},
    {"id": 140, "name": "ラ・リーガ", "country": "Spain"},
    {"id": 78, "name": "ブンデスリーガ", "country": "Germany"},
    {"id": 135, "name": "セリエA", "country": "Italy"},
    {"id": 61, "name": "リーグ・アン", "country": "France"},
    {"id": 88, "name": "エールディヴィジ", "country": "Netherlands"},
    {"id": 94, "name": "リーガ・ポルトガル", "country": "Portugal"},
    {"id": 144, "name": "ベルギー・プロリーグ", "country": "Belgium"},
    {"id": 179, "name": "スコティッシュ・プレミアシップ", "country": "Scotland"},
    {"id": 203, "name": "スュペル・リグ", "country": "Turkey"},
]

JAPAN_NATIONALITY = "Japan"

API_BASE_URL = "https://v3.football.api-sports.io"
