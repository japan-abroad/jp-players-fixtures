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
from config import COUNTRY_JA, COUNTRY_TOP_LEAGUE_JA, FREE_PLAN_SEASON

# 育成年代・リザーブ・女子チームの命名によく含まれるトークン。検索結果に
# トップチームとこれらが混在する場合、誤ってこちらを拾わないよう除外する。
_NON_FIRST_TEAM_RE = re.compile(
    r"(?:^|\s)(U1[0-9]|U2[0-3]|U9|II|III|IV|B|W|2|Youth|Yth|Reserves?|Fem\w*|Women|Ladies|Girls|Jugend|Jeugd)(?:$|\s)",
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
_UNSAFE_STANDALONE_WORDS = {
    "royal", "koninklijke", "real", "sporting", "deportivo", "atletico",
    "athletic", "club", "international", "olympic", "olympique", "united",
    "city", "town", "national", "stade", "racing", "sport",
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


def _resolve_team(name_en: str, max_requests: int) -> dict | None:
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
    return {
        "team_id": team["id"],
        "team_name": team["name"],
        "logo": team.get("logo"),
        "country_code": (team.get("country") or "")[:3].lower(),
        "country_ja": country_ja,
        "league_name": COUNTRY_TOP_LEAGUE_JA.get(country_ja, country_ja),
    }


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
    club_name_map: dict[str, str] = scraped["club_name_map"]
    players_by_club_ja: dict[str, list[dict]] = {}
    for p in scraped["players"]:
        players_by_club_ja.setdefault(p["club_name_ja"], []).append({"name": p["name_ja"], "position": None})

    cache: dict[str, dict] = _load_json(CACHE_PATH, {})

    pending = [
        (club_ja, name_en)
        for club_ja, name_en in club_name_map.items()
        if name_en not in cache
    ]

    while pending and api_client.request_count < max_requests:
        club_ja, name_en = pending[0]
        try:
            resolved = _resolve_team(name_en, max_requests)
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
