"""対象リーグ・シーズン定義。

API-FootballのリーグIDは https://www.api-football.com/documentation-v3#tag/Leagues の
一覧、または /leagues エンドポイントで確認できる。
"""

# 日本人選手が所属しやすい欧州主要リーグ
# country_code/country_ja はサイト側の国別フィルター・国旗表示に使う
LEAGUES = [
    {"id": 39, "name": "プレミアリーグ", "country_code": "eng", "country_ja": "イングランド"},
    # 2026-08-30 検証済み: /leagues?id=40 -> "Championship League" (England)
    {"id": 40, "name": "チャンピオンシップ", "country_code": "eng", "country_ja": "イングランド"},
    {"id": 140, "name": "ラ・リーガ", "country_code": "esp", "country_ja": "スペイン"},
    {"id": 78, "name": "ブンデスリーガ", "country_code": "ger", "country_ja": "ドイツ"},
    {"id": 135, "name": "セリエA", "country_code": "ita", "country_ja": "イタリア"},
    {"id": 61, "name": "リーグ・アン", "country_code": "fra", "country_ja": "フランス"},
    {"id": 88, "name": "エールディヴィジ", "country_code": "ned", "country_ja": "オランダ"},
    {"id": 94, "name": "リーガ・ポルトガル", "country_code": "por", "country_ja": "ポルトガル"},
    {"id": 144, "name": "ベルギー・プロリーグ", "country_code": "bel", "country_ja": "ベルギー"},
    {"id": 179, "name": "スコティッシュ・プレミアシップ", "country_code": "sco", "country_ja": "スコットランド"},
    {"id": 203, "name": "スュペル・リグ", "country_code": "tur", "country_ja": "トルコ"},
]

# 国内カップ戦。fetch_fixtures.pyは日付ベースで世界中の試合を取得してから
# LEAGUESに載っている大会だけを抽出する方式のため、ここに追加しても
# APIリクエスト数は増えない(取得後のフィルタ対象が増えるだけ)。
# 2026-08-30 全件 /leagues?id=<id> で検証済み。
# 発覚した誤り: ポルトガルは97(Taça da Liga=リーグカップ)ではなく96
# (Taça de Portugal=本来のカップ戦)、スコットランドは180(Championship=
# 2部リーグ)ではなく181(FA Cup Scotland)が正しい値だった。
CUP_LEAGUES = [
    {"id": 45, "name": "FAカップ", "country_code": "eng", "country_ja": "イングランド"},
    {"id": 48, "name": "EFLカップ", "country_code": "eng", "country_ja": "イングランド"},
    {"id": 143, "name": "コパ・デル・レイ", "country_code": "esp", "country_ja": "スペイン"},
    {"id": 81, "name": "DFBポカール", "country_code": "ger", "country_ja": "ドイツ"},
    {"id": 137, "name": "コッパ・イタリア", "country_code": "ita", "country_ja": "イタリア"},
    {"id": 66, "name": "クープ・ド・フランス", "country_code": "fra", "country_ja": "フランス"},
    {"id": 90, "name": "KNVBベーカー", "country_code": "ned", "country_ja": "オランダ"},
    {"id": 96, "name": "ポルトガルカップ", "country_code": "por", "country_ja": "ポルトガル"},
    {"id": 147, "name": "ベルギーカップ", "country_code": "bel", "country_ja": "ベルギー"},
    {"id": 181, "name": "スコティッシュカップ", "country_code": "sco", "country_ja": "スコットランド"},
    {"id": 206, "name": "トルコカップ", "country_code": "tur", "country_ja": "トルコ"},
]

# サッカーキング(soccer-king.jp)の「海外クラブ在籍日本人選手」一覧には、
# 上記11リーグ以外の国(オセアニア・北米・アジア等)のクラブも登場する。
# API-Footballのteam.country(英語国名)を日本語表示名・代表的リーグ名に
# 変換するための一覧。上記11リーグと重複する国はLEAGUESの表記に合わせてある。
COUNTRY_JA = {
    "England": "イングランド",
    "Scotland": "スコットランド",
    "Germany": "ドイツ",
    "Spain": "スペイン",
    "Italy": "イタリア",
    "France": "フランス",
    "Netherlands": "オランダ",
    "Portugal": "ポルトガル",
    "Belgium": "ベルギー",
    "Turkey": "トルコ",
    "Switzerland": "スイス",
    "Austria": "オーストリア",
    "Poland": "ポーランド",
    "Denmark": "デンマーク",
    "Sweden": "スウェーデン",
    "Norway": "ノルウェー",
    "South-Korea": "韓国",
    "Australia": "オーストラリア",
    "New-Zealand": "ニュージーランド",
    "USA": "アメリカ",
    "Canada": "カナダ",
}

# 国別の代表的な1部リーグ名(要検証: 実際にどのリーグに所属しているかは
# API-Footballの/leagues?team=IDで確認できるが、クオータ節約のため
# ひとまず国からの推定表示名としている)。
COUNTRY_TOP_LEAGUE_JA = {
    "イングランド": "プレミアリーグ",
    "スコットランド": "スコティッシュ・プレミアシップ",
    "ドイツ": "ブンデスリーガ",
    "スペイン": "ラ・リーガ",
    "イタリア": "セリエA",
    "フランス": "リーグ・アン",
    "オランダ": "エールディヴィジ",
    "ポルトガル": "リーガ・ポルトガル",
    "ベルギー": "ベルギー・プロリーグ",
    "トルコ": "スュペル・リグ",
    "スイス": "スイス・スーパーリーグ",
    "オーストリア": "オーストリア・ブンデスリーガ",
    "ポーランド": "エクストラクラサ",
    "デンマーク": "スーペルリーガ",
    "スウェーデン": "アルスヴェンスカン",
    "韓国": "Kリーグ1",
    "オーストラリア": "Aリーグ",
    "ニュージーランド": "ニュージーランド・ナショナルリーグ",
    "アメリカ": "MLS",
    "カナダ": "カナディアン・プレミアリーグ",
}

# API-Football無料プランは2022〜2024シーズンのデータのみアクセス可能
FREE_PLAN_SEASON = 2024

API_BASE_URL = "https://v3.football.api-sports.io"
