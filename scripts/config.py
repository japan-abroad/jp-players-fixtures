"""対象リーグ定義。

ESPNの非公式サッカーAPI(site.api.espn.com)を利用する。
リーグはESPN側のスラッグ(例: "eng.1")で指定する。
"""

# 日本人選手が所属しやすい欧州主要リーグ
# country_code はサイト側の国別フィルター・国旗表示に使う短縮コード
LEAGUES = [
    {"espn_slug": "eng.1", "name": "プレミアリーグ", "country": "England", "country_code": "eng", "country_ja": "イングランド"},
    {"espn_slug": "eng.2", "name": "チャンピオンシップ", "country": "England", "country_code": "eng", "country_ja": "イングランド"},
    {"espn_slug": "esp.1", "name": "ラ・リーガ", "country": "Spain", "country_code": "esp", "country_ja": "スペイン"},
    {"espn_slug": "ger.1", "name": "ブンデスリーガ", "country": "Germany", "country_code": "ger", "country_ja": "ドイツ"},
    {"espn_slug": "ita.1", "name": "セリエA", "country": "Italy", "country_code": "ita", "country_ja": "イタリア"},
    {"espn_slug": "fra.1", "name": "リーグ・アン", "country": "France", "country_code": "fra", "country_ja": "フランス"},
    {"espn_slug": "ned.1", "name": "エールディヴィジ", "country": "Netherlands", "country_code": "ned", "country_ja": "オランダ"},
    {"espn_slug": "por.1", "name": "リーガ・ポルトガル", "country": "Portugal", "country_code": "por", "country_ja": "ポルトガル"},
    {"espn_slug": "bel.1", "name": "ベルギー・プロリーグ", "country": "Belgium", "country_code": "bel", "country_ja": "ベルギー"},
    {"espn_slug": "sco.1", "name": "スコティッシュ・プレミアシップ", "country": "Scotland", "country_code": "sco", "country_ja": "スコットランド"},
    {"espn_slug": "tur.1", "name": "スュペル・リグ", "country": "Turkey", "country_code": "tur", "country_ja": "トルコ"},
]

JAPAN_CITIZENSHIP = "Japan"

ESPN_BASE_URL = "https://site.api.espn.com/apis/site/v2/sports/soccer"
