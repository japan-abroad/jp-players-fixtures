"""対象リーグ・シーズン定義。

API-FootballのリーグIDは https://www.api-football.com/documentation-v3#tag/Leagues の
一覧、または /leagues エンドポイントで確認できる。
"""

# 日本人選手が所属しやすい欧州主要リーグ(1部)
LEAGUES = [
    {"id": 39, "name": "プレミアリーグ", "country": "England"},
    # 要検証: API-Footballのリーグ一覧が取得できる状態になったら
    # /leagues?name=Championship&country=England で正しいIDか確認すること
    {"id": 40, "name": "チャンピオンシップ", "country": "England"},
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

# API-Football無料プランの /players/squads は国籍情報を返さないため、
# 現在の登録選手名をこの名字リストと照合して日本人選手かどうかを判定する。
# (ローマ字表記は "K. Mitoma" のように「頭文字. 名字」形式で入ってくる)
# 移籍によるクラブの変化は自動追従するが、このリスト自体は
# 新戦力の台頭・引退などに応じて年に数回程度の手動更新が必要。
JAPANESE_SURNAMES = [
    "Mitoma",
    "Kubo",
    "Endo",
    "Tomiyasu",
    "Kamada",
    "Doan",
    "Minamino",
    "Maeda",
    "Asano",
    "Ueda",
    "Taniguchi",
    "Itakura",
    "Hatate",
    "Suzuki",
    "Nakamura",
    "Morita",
    "Kawashima",
    "Sugawara",
    "Hashioka",
    "Seko",
    "Machida",
    "Osako",
    "Tanaka",
    "Yamane",
    "Sakai",
    "Ito",
    "Abe",
    "Mitsuta",
    "Hirakawa",
    "Kobayashi",
    # 2026-08時点でスポーツサイト(addfoot.net)を参照して追加した実在選手の名字
    "Sakamoto",
    "Takai",
    "Matsuki",
    "Ohashi",
    "Morishita",
    "Iwata",
    "Fujimoto",
    "Yokota",
    "Kokubo",
    "Matsuzawa",
    "Hata",
    "Shinkawa",
    "Ishiwatari",
    "Araki",
    "Mizuta",
    "Osada",
    "Yamamoto",
    "Goto",
    "Shiogai",
    "Sano",
    "Kawasaki",
    "Machino",
    "Uno",
    "Kosugi",
    "Fujita",
    "Ando",
    "Hara",
    "Sekine",
    "Takahashi",
    "Onoda",
    "Fukui",
    "Fukuda",
    "Karashima",
]

# API-Football無料プランは2022〜2024シーズンのデータのみアクセス可能
FREE_PLAN_SEASON = 2024

API_BASE_URL = "https://v3.football.api-sports.io"
