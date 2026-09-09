"""scrape_jp_clubs.py の出力(クラブ名一覧)をAPI-Footballのteam_idに解決する。

data/soccerking_players.json の各クラブ(英語公式名)について
/teams?search=<name> を1回だけ叩いてteam_id・ロゴ・国を取得する。
一度解決したクラブはdata/team_id_cache.jsonに保存され、次回以降は
再リクエストしない(クラブ名が変わらない限り恒久的に再利用できる)。

残りクオータを自動検出して安全マージンを
引いた範囲でのみ実行し、中断しても次回実行時に続きから再開する。

使い方:
    python resolve_jp_clubs.py            # 残りクオータを自動検出して実行
    python resolve_jp_clubs.py --max-requests 20
"""

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

import api_client
from config import (
    COUNTRY_JA,
    COUNTRY_TOP_LEAGUE_JA,
    ENGLAND_DIVISION_JA,
    ENGLAND_DIVISION_OVERRIDE_BY_TEAM_ID,
    FREE_PLAN_SEASON,
)

# 育成年代・リザーブ・女子チームの命名によく含まれるトークン。検索結果に
# トップチームとこれらが混在する場合、誤ってこちらを拾わないよう除外する。
_NON_FIRST_TEAM_RE = re.compile(
    r"(?:^|\s)(U1[0-9]|U2[0-3]|U9|II|III|IV|B|W|2|Youth|Yth|Reserves?|Res\.?|Fem\w*|Women|Ladies|Girls|Jugend|Jeugd)(?:$|\s)",
    re.IGNORECASE,
)

# 検索クエリから除いても意味が変わらない、クラブ名によくある一般的な
# 接頭辞・接尾辞トークン。例: "Aston Villa F.C." は "Aston Villa" の方が
# ヒットしやすく、"TSG 1899 Hoffenheim" は "TSG" が無い方がヒットする。
_GENERIC_CLUB_TOKENS = {
    "FC", "CF", "AFC", "SC", "AC", "SV", "TSG", "FSV", "VFL", "VFB", "TSV",
    "SPVGG", "AS", "CD", "UD", "1",
}

# 単独の検索クエリとして使うと、別の無関係な実在クラブ("Royal"や
# "Koninklijke"だけの弱小クラブ等)にヒットしてしまう危険な汎用語。
# 複合クエリ(フルネーム)の一部としてはそのまま使ってよいが、
# 段階的単純化のフォールバックでは単独使用を避ける。
# 例: "Royal Antwerp F.C." の先頭語"Royal"だけで検索すると、本来の
# Antwerpとは無関係な"Royal"という名のクラブ(id=8569)がヒットした。
# 2026-09-06発覚: "Union Saint-Gilloise"の先頭語"Union"だけで検索すると、
# ラトビアの無関係なクラブ"Union"(id=21371)に完全一致してしまった。
_UNSAFE_STANDALONE_WORDS = {
    "royal", "koninklijke", "real", "sporting", "deportivo", "atletico",
    "athletic", "club", "international", "olympic", "olympique", "united",
    "city", "town", "national", "stade", "racing", "sport", "union",
}

# サッカーキング側の英語表記とAPI-Football側の登録名が大きく異なり、
# 段階的な単純化でも解決できない既知のクラブ(soccer-king名 -> 検索クエリ)。
_MANUAL_QUERY_OVERRIDES = {
    "Alkmaar Zaanstreek": "AZ",
    "LA Galaxy": "Los Angeles Galaxy",
    # サッカーキング側の表記"Bundby"はデンマーク語"Brøndby"の誤記/文字化けと
    # 思われる(正しくは"Brondby")。
    "Bundby IF": "Brondby",
    # "Antwerpen"単体だと球団史上のBeerschot以外の候補が混ざるため、
    # 現行クラブの正式名の一部を直接指定する。
    "Koninklijke Beerschot Voetbalclub Antwerpen": "Beerschot VA",
    # "Sint-Truidense"はポルトガルの無関係なクラブ"Sintrense"と綴りが
    # 似ているため類似度判定で誤って一致してしまった(2026-08-30発覚、
    # 本来はベルギーのSt. Truiden)。
    "Sint-Truidense": "Truiden",
    # "Olympique Lyonnais"の一般的略称"Lyonnais"だけで検索すると無関係な
    # 弱小クラブ"Val Lyonnais"に誤ヒットする(API-Football側の正式登録名は
    # 単に"Lyon")。2026-09-06発覚。
    "Olympique Lyonnais": "Lyon",
    # "Bolton Wanderers"で検索するとレギュラーの"Bolton"がヒットせず
    # リザーブチーム表記("Res.")のみ返る(2026-09-06発覚、除外正規表現に
    # "Res."追加で対応済みだが、そもそも"Bolton Wanderers"というクエリでは
    # 一軍"Bolton"がAPI検索結果に出てこないため明示指定する)。
    "Bolton Wanderers F.C.": "Bolton",
    # "Queens Park Rangers"で検索するとAPI-Football側に同名で別登録されている
    # 実体不明のチーム(id=18212、国内リーグの試合が一切無くFA女子カップの
    # 記録しかない)がフルネーム一致で誤って選ばれてしまう(2026-09-09発覚)。
    # 本来の男子トップチームはAPI-Football側で"QPR"という略称で登録されている。
    "Queens Park Rangers F.C.": "QPR",
    # 注意: "F.C. Bayern Munich"(男子トップチームはドイツ語表記"München"で
    # 登録されている)はここでは解決できない — "München"はAPIの検索クエリ
    # (英数字とスペースのみ許可)に使えず、"Bayern"単体だと無関係な弱小クラブ
    # (Bayern Hof等)が短い候補として類似度で誤って勝ってしまうため。
    # data/team_id_cache.json に id=157 を直接手動登録している。
}

# API-Footballの/teams?searchは短すぎる語をエラーにするため、これ未満の
# クエリは投げずにスキップする。
_MIN_QUERY_LENGTH = 3

# 候補との類似度がこれを下回る場合は「見つからなかった」扱いにする。
# 閾値を設けないと、フォールバック段階の緩いクエリで無関係なクラブを
# 誤って採用し、気づかれないままキャッシュに残ってしまう。
# 0.65では "Hammarby"→"Hammarby Talang"(下部組織) のような、クエリを
# そのまま接頭辞に含むだけの別チームまで通ってしまったため、0.75に引き上げた。
_MIN_MATCH_RATIO = 0.75

# 類似度比較の際に無視する、クラブ名によくある一般的な単語。
# 例: "Ipswich" (クエリ) と "Afro Foot Club" (無関係な候補)は、
# 両方に"Club"系の単語を含むだけで類似度が不当に高く出てしまうため、
# 比較前にこうした語を取り除く。
# 注意: "United"は入れない — "Coventry"というクエリに対し"Coventry"(本物)と
# "Coventry United"(別の無関係なクラブ)が"United"除去で同一視され、
# どちらが選ばれるか運任せになる事故が実際に発生したため。
_MATCH_STOPWORDS = {
    "football", "club", "afc", "fc", "sc",
}


class _BudgetExceeded(Exception):
    """クラブ解決の途中で残りリクエスト数の上限に達したことを示す。"""

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PLAYERS_PATH = DATA_DIR / "soccerking_players.json"
CACHE_PATH = DATA_DIR / "team_id_cache.json"
OUTPUT_PATH = DATA_DIR / "jp_clubs.json"
# soccer-king.jpの一覧ページに掲載が間に合っていない選手を補うための
# 手動追加リスト(2026-09-06新設)。移籍報道が出てから同ページに反映
# されるまでにタイムラグがあり、佐藤龍之介(バレンシア加入)が
# 2026-09-06時点で未掲載だったことが発端。各エントリは複数の一次
# 報道で移籍を確認したうえで追加すること。
MANUAL_PLAYERS_PATH = DATA_DIR / "manual_players.json"

# scrape_gekisaka_players.py(ゲキサカ「海外組ガイド」、主要7リーグのみ)の
# 出力。soccer-kingより移籍反映が速い傾向があり、2026-09-06に佐藤龍之介
# (バレンシア)ほか2名の掲載漏れを補完できることを確認したため、
# 自動突合する第2ソースとして追加(2026-09-06)。
GEKISAKA_PLAYERS_PATH = DATA_DIR / "gekisaka_players.json"

# ゲキサカ側のクラブ表記が中黒有無・「ヴ/ビ」表記ゆれの正規化だけでは
# soccer-king側の既存クラブ名に一致しない既知のケース。ゲキサカのクラブ名
# (表記そのまま) -> soccer-king側の既存club_name_ja。ここで解決できれば
# 別クラブとして重複登録されるのを防げる(2026-09-06発覚: "アントワープ"が
# 正規化しても"ロイヤル・アントワープ"と一致せず、同じチームが2件の
# クラブとして重複表示される事故があった)。
GEKISAKA_CLUB_JA_ALIASES: dict[str, str] = {
    "アントワープ": "ロイヤル・アントワープ",
    "アストン・ビラ": "アストン・ヴィラ",
    "コベントリー": "コヴェントリー",
    "ル・アーブル": "ル・アーヴル",
    "ルーベン": "ルーヴェン",
    "ソシエダ": "レアル・ソシエダ",
}

# soccer-king側に該当クラブがそもそも存在しない場合の、ゲキサカのクラブ名
# (表記そのまま) -> API-Football検索用の英語名。
GEKISAKA_CLUB_EN_OVERRIDES: dict[str, str] = {
    "サンジロワーズ": "Union Saint-Gilloise",
    "シャルルロワ": "Charleroi",
    "バレンシア": "Valencia",
}


def _normalize_club_ja(name: str) -> str:
    for ch in "・ ":
        name = name.replace(ch, "")
    return name


def _load_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def _save_cache(cache: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def _sanitize_search_query(name_en: str) -> str:
    # API-Footballの/teams?searchは英数字とスペースのみ許可(記号はエラーになる)。
    # ピリオドは空白に置換せず除去する("F.C." -> "FC" の1トークンにする。
    # 空白に置換すると "F" "C" のバラバラなトークンになり検索がヒットしなくなる)。
    cleaned = name_en.replace(".", "")
    cleaned = re.sub(r"[^A-Za-z0-9 ]+", " ", cleaned)
    tokens = [t for t in cleaned.split() if t.upper() not in _GENERIC_CLUB_TOKENS]
    return " ".join(tokens) if tokens else cleaned.strip()


def _search_queries(name_en: str) -> list[str]:
    """段階的に単純化した検索クエリ候補を順番に返す(最初にヒットしたもので確定)。"""
    queries = []
    if name_en in _MANUAL_QUERY_OVERRIDES:
        queries.append(_MANUAL_QUERY_OVERRIDES[name_en])
    primary = _sanitize_search_query(name_en)
    queries.append(primary)
    words = primary.split()
    if len(words) > 1:
        if words[0].lower() not in _UNSAFE_STANDALONE_WORDS:
            queries.append(words[0])
        if words[-1].lower() not in _UNSAFE_STANDALONE_WORDS:
            queries.append(words[-1])
    seen: set[str] = set()
    unique = []
    for q in queries:
        if q and q not in seen:
            seen.add(q)
            unique.append(q)
    return unique


def _normalize_for_match(s: str) -> str:
    tokens = [t for t in s.lower().split() if t not in _MATCH_STOPWORDS]
    return " ".join(tokens) if tokens else s.lower()


def _best_first_team(candidates: list[dict], query: str) -> dict | None:
    """candidatesは実際に検索に使ったqueryへの一致度で評価する(元の
    クラブ名全体と比較すると、'Football'/'Club'等の共通語だけで
    無関係な候補の類似度が不当に高く出てしまうため)。"""
    first_team_only = [t for t in candidates if not _NON_FIRST_TEAM_RE.search(t["name"])]
    if not first_team_only:
        return None
    target = _normalize_for_match(query)

    def ratio(t: dict) -> float:
        return difflib.SequenceMatcher(None, target, _normalize_for_match(t["name"])).ratio()

    best = max(first_team_only, key=ratio)
    return best if ratio(best) >= _MIN_MATCH_RATIO else None


def _resolve_team(name_en: str, club_ja: str, max_requests: int) -> dict | None:
    team = None
    for query in _search_queries(name_en):
        if len(query) < _MIN_QUERY_LENGTH:
            continue
        if api_client.request_count >= max_requests:
            raise _BudgetExceeded()
        try:
            candidates = api_client.search_team(query)
        except RuntimeError as exc:
            # クエリが短すぎる等、APIエラーで1件も返らなかった場合は
            # 次の(より緩い)クエリを試す。処理全体は止めない。
            print(f"    検索エラー(クエリ={query!r}): {exc}", file=sys.stderr)
            continue
        team = _best_first_team(candidates, query)
        if team is not None:
            break
    if team is None:
        return None
    country_ja = COUNTRY_JA.get(team.get("country"), team.get("country") or "")
    league_name = COUNTRY_TOP_LEAGUE_JA.get(country_ja, country_ja)
    if country_ja == "イングランド":
        # 優先順位: (1) Yahoo!スポーツの現行シーズン順位表(クオータ消費なし・
        # 最新) (2) team_id手動オーバーライド(Yahoo側で見つからない場合の
        # 保険) (3) API-Football season=2024の近似値(最後の手段)。
        division = _resolve_england_division_from_yahoo(club_ja)
        if division is None and team["id"] in ENGLAND_DIVISION_OVERRIDE_BY_TEAM_ID:
            division = ENGLAND_DIVISION_OVERRIDE_BY_TEAM_ID[team["id"]]
        if division is None:
            division = _resolve_england_division(team["id"], max_requests)
        if division is not None:
            league_name = division
    return {
        "team_id": team["id"],
        "team_name": team["name"],
        "logo": team.get("logo"),
        "country_code": (team.get("country") or "")[:3].lower(),
        "country_ja": country_ja,
        "league_name": league_name,
    }


YAHOO_DIVISIONS_PATH = DATA_DIR / "england_divisions.json"

# scrape_england_divisions.pyが取得するYahoo!スポーツ側のチーム表記は、
# 略称("・C"="City"、無印="United"省略等)がサッカーキング側の表記
# (team_name_ja)と異なる場合がある。正規化(・とスペースを除去)だけでは
# 一致しないクラブをここで個別に吸収する(2026-09-09新設)。
YAHOO_CLUB_JA_ALIASES: dict[str, str] = {
    "ハル・シティ": "ハルC",
    "コヴェントリー": "コベントリーC",
    "クイーンズ・パーク・レンジャーズ": "クイーンズパーク",
}

_yahoo_divisions_cache: dict[str, str] | None = None


def _load_yahoo_divisions() -> dict[str, str]:
    """{正規化済みチーム名: ディビジョン名}の辞書を返す(1プロセス内でキャッシュ)。"""
    global _yahoo_divisions_cache
    if _yahoo_divisions_cache is not None:
        return _yahoo_divisions_cache
    if not YAHOO_DIVISIONS_PATH.exists():
        _yahoo_divisions_cache = {}
        return _yahoo_divisions_cache
    data = json.loads(YAHOO_DIVISIONS_PATH.read_text(encoding="utf-8"))
    mapping: dict[str, str] = {}
    for name in data.get("premier_league", []):
        mapping[_normalize_club_ja(name)] = "プレミアリーグ"
    for name in data.get("championship", []):
        mapping[_normalize_club_ja(name)] = "チャンピオンシップ"
    _yahoo_divisions_cache = mapping
    return mapping


def _resolve_england_division_from_yahoo(club_ja: str) -> str | None:
    divisions = _load_yahoo_divisions()
    if not divisions:
        return None
    ja = YAHOO_CLUB_JA_ALIASES.get(club_ja, club_ja)
    norm = _normalize_club_ja(ja)
    if norm in divisions:
        return divisions[norm]
    # 表記ゆれ("リーズ"⇔"リーズ・ユナイテッド"等)を前方一致/後方一致で吸収する。
    for yahoo_norm, division in divisions.items():
        if len(yahoo_norm) < 3:
            continue
        if norm.startswith(yahoo_norm) or norm.endswith(yahoo_norm):
            return division
    return None


def _resolve_england_division(team_id: int, max_requests: int) -> str | None:
    """イングランドのクラブが実際に所属するディビジョンをAPIで確認する。

    国別トップリーグからの推定(COUNTRY_TOP_LEAGUE_JA)はイングランドでは
    常にプレミアリーグ扱いになってしまい、チャンピオンシップ以下のクラブが
    誤ってプレミアリーグ所属と表示される事故が発覚した(2026-09-09)。
    """
    if api_client.request_count >= max_requests:
        raise _BudgetExceeded()
    try:
        leagues = api_client.get_leagues_for_team(team_id, FREE_PLAN_SEASON)
    except RuntimeError as exc:
        print(f"    ディビジョン判定エラー(team_id={team_id}): {exc}", file=sys.stderr)
        return None
    for entry in leagues:
        league = entry.get("league", {})
        if league.get("type") == "League" and league.get("id") in ENGLAND_DIVISION_JA:
            return ENGLAND_DIVISION_JA[league["id"]]
    return None


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
    club_name_map: dict[str, str] = dict(scraped["club_name_map"])
    players_by_club_ja: dict[str, list[dict]] = {}
    for p in scraped["players"]:
        players_by_club_ja.setdefault(p["club_name_ja"], []).append({"name": p["name_ja"], "position": None})

    for m in _load_json(MANUAL_PLAYERS_PATH, []):
        club_name_map.setdefault(m["club_name_ja"], m["club_name_en"])
        existing = players_by_club_ja.setdefault(m["club_name_ja"], [])
        if not any(p["name"] == m["name_ja"] for p in existing):
            existing.append({"name": m["name_ja"], "position": None})

    # ゲキサカ「海外組ガイド」との突合。soccer-king側に無い選手・クラブを
    # 補完する(中黒・表記ゆれは正規化して既存クラブに寄せ、それでも
    # 一致しない場合はGEKISAKA_CLUB_EN_OVERRIDESで解決する)。
    norm_to_club_ja = {_normalize_club_ja(k): k for k in club_name_map}
    for gp in _load_json(GEKISAKA_PLAYERS_PATH, {}).get("players", []):
        gk_club_ja = gp["club_name_ja"]
        target_club_ja = norm_to_club_ja.get(_normalize_club_ja(gk_club_ja))
        if target_club_ja is None and gk_club_ja in GEKISAKA_CLUB_JA_ALIASES:
            target_club_ja = norm_to_club_ja.get(
                _normalize_club_ja(GEKISAKA_CLUB_JA_ALIASES[gk_club_ja])
            )
        if target_club_ja is None:
            name_en = GEKISAKA_CLUB_EN_OVERRIDES.get(gk_club_ja)
            if name_en is None:
                print(
                    f"  注意: ゲキサカのクラブ「{gk_club_ja}」がsoccer-king側・"
                    f"GEKISAKA_CLUB_EN_OVERRIDESのどちらにも一致しません "
                    f"({gp['name_ja']})。resolve_jp_clubs.pyにオーバーライドを追加してください。",
                    file=sys.stderr,
                )
                continue
            target_club_ja = gk_club_ja
            club_name_map.setdefault(target_club_ja, name_en)
            norm_to_club_ja[_normalize_club_ja(target_club_ja)] = target_club_ja
        existing = players_by_club_ja.setdefault(target_club_ja, [])
        if not any(p["name"] == gp["name_ja"] for p in existing):
            existing.append({"name": gp["name_ja"], "position": None})
            print(f"  ゲキサカから補完: {gp['name_ja']} ({target_club_ja})")

    cache: dict[str, dict] = _load_json(CACHE_PATH, {})

    pending = [
        (club_ja, name_en)
        for club_ja, name_en in club_name_map.items()
        if name_en not in cache
    ]

    while pending and api_client.request_count < max_requests:
        club_ja, name_en = pending[0]
        try:
            resolved = _resolve_team(name_en, club_ja, max_requests)
        except _BudgetExceeded:
            # このクラブは複数クエリを試す途中で予算に達した。
            # 未解決のまま確定させず、次回実行時に最初からやり直す。
            break
        pending.pop(0)
        if resolved is None:
            print(f"  未解決: {club_ja} ({name_en}) - 一致するトップチームが見つかりません")
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
        if not players_by_club_ja.get(club_ja):
            # サッカーキング側で「在籍クラブ」一覧には載っているが、
            # 選手一覧側には対応する選手が見つからないクラブ(サイト側の
            # 掲載タイミングのずれと思われる)。選手がいないと表示価値が
            # ないため出力から除く。
            print(f"  除外: {club_ja} ({name_en}) - 選手一覧に対応する選手が見つかりません")
            continue
        clubs.append(
            {
                "team_id": resolved["team_id"],
                "team_name": resolved["team_name"],
                "team_name_ja": club_ja,
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
