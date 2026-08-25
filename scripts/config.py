"""対象リーグ・シーズン定義。

API-FootballのリーグIDは https://www.api-football.com/documentation-v3#tag/Leagues の
一覧、または /leagues エンドポイントで確認できる。
"""

# 日本人選手が所属しやすい欧州主要リーグ
# country_code/country_ja はサイト側の国別フィルター・国旗表示に使う
LEAGUES = [
    {"id": 39, "name": "プレミアリーグ", "country_code": "eng", "country_ja": "イングランド"},
    # 要検証: API-Footballのリーグ一覧が取得できる状態になったら
    # /leagues?name=Championship&country=England で正しいIDか確認すること
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
# 要検証: 無料枠が復活したら /leagues?id=<id> で正しいIDか確認すること。
CUP_LEAGUES = [
    {"id": 45, "name": "FAカップ", "country_code": "eng", "country_ja": "イングランド"},
    {"id": 48, "name": "EFLカップ", "country_code": "eng", "country_ja": "イングランド"},
    {"id": 143, "name": "コパ・デル・レイ", "country_code": "esp", "country_ja": "スペイン"},
    {"id": 81, "name": "DFBポカール", "country_code": "ger", "country_ja": "ドイツ"},
    {"id": 137, "name": "コッパ・イタリア", "country_code": "ita", "country_ja": "イタリア"},
    {"id": 66, "name": "クープ・ド・フランス", "country_code": "fra", "country_ja": "フランス"},
    {"id": 90, "name": "KNVBベーカー", "country_code": "ned", "country_ja": "オランダ"},
    {"id": 97, "name": "ポルトガルカップ", "country_code": "por", "country_ja": "ポルトガル"},
    {"id": 147, "name": "ベルギーカップ", "country_code": "bel", "country_ja": "ベルギー"},
    {"id": 180, "name": "スコティッシュカップ", "country_code": "sco", "country_ja": "スコットランド"},
    {"id": 206, "name": "トルコカップ", "country_code": "tur", "country_ja": "トルコ"},
]

# fetch_fixtures.py用: discover(所属クラブ発見)は上のLEAGUES(1部+2部)だけを
# 対象にする(カップ戦は下部リーグの弱小クラブも大量に参加するため、
# discoverの対象に含めると無関係なチームまで走査してしまう)。
# fixtures取得側だけ、カップ戦を含めたこちらを使う。
FIXTURE_LEAGUES = LEAGUES + CUP_LEAGUES

# API-Football無料プランの /players/squads は国籍情報を返さないため、
# 現在の登録選手名をこの名字リストと照合して日本人選手かどうかを判定する。
# (ローマ字表記は "K. Mitoma" のように「頭文字. 名字」形式で入ってくる)
# 移籍によるクラブの変化は自動追従するが、このリスト自体は
# 新戦力の台頭・引退などに応じて年に数回程度の手動更新が必要。
JAPANESE_SURNAMES = [
    "Mitoma", "Kubo", "Endo", "Tomiyasu", "Kamada", "Doan", "Minamino", "Maeda",
    "Asano", "Ueda", "Taniguchi", "Itakura", "Hatate", "Suzuki", "Nakamura",
    "Morita", "Kawashima", "Sugawara", "Hashioka", "Seko", "Machida", "Osako",
    "Tanaka", "Yamane", "Sakai", "Ito", "Abe", "Mitsuta", "Hirakawa", "Kobayashi",
    # 2026-08時点でスポーツサイト(addfoot.net)を参照して追加した実在選手の名字
    "Sakamoto", "Takai", "Matsuki", "Ohashi", "Morishita", "Iwata", "Fujimoto",
    "Yokota", "Kokubo", "Matsuzawa", "Hata", "Shinkawa", "Ishiwatari", "Araki",
    "Mizuta", "Osada", "Yamamoto", "Goto", "Shiogai", "Sano", "Kawasaki",
    "Machino", "Uno", "Kosugi", "Fujita", "Ando", "Hara", "Sekine", "Takahashi",
    "Onoda", "Fukui", "Fukuda", "Karashima",
]

# API-Football無料プランは2022〜2024シーズンのデータのみアクセス可能
FREE_PLAN_SEASON = 2024

API_BASE_URL = "https://v3.football.api-sports.io"
