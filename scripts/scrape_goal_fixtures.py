"""goal.com(日本版)から試合日程を取得する。

API-Football無料プランは/fixtures?date=が「当日±1日」程度しかアクセス
できず、試合予定サイトとしては致命的に狭かった。goal.com/jp/試合日程/
{日付} は日付ごとの静的ページ(JavaScript無効でも取得可能)で、任意の
未来日付・過去日付にアクセスでき、しかもチーム名・リーグ名が最初から
日本語で提供される。robots.txtも全面許可(Allow: /)。

このスクリプトはAPI-Footballを一切使わない(クオータ消費なし)。

出力データの日本人選手所属クラブのタグ付けは、team_idではなく
チーム名(日本語)の正規化一致で行う。goal.com側のチームIDが
API-Footballと異なる体系のため、data/jp_clubs.jsonのteam_name_ja
(サッカーキングでの表記)と照合する。表記ゆれで一致しないクラブが
出た場合はNAME_OVERRIDESで個別に吸収する。

使い方:
    python scrape_goal_fixtures.py
"""

import json
import re
import sys
import time
import unicodedata
import urllib.parse
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CLUBS_PATH = DATA_DIR / "jp_clubs.json"
OUTPUT_PATH = DATA_DIR / "fixtures.json"

BASE_URL = "https://www.goal.com/jp/%E8%A9%A6%E5%90%88%E6%97%A5%E7%A8%8B/{date}"
DAYS_AHEAD = 7
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "ja-JP,ja;q=0.9",
}
_MIN_INTERVAL_SEC = 2.0

# 対象リーグ。goal.comの(area, league_name)表記そのままをキーにする
# (どちらも日本語)。国内カップ戦は要検証(未観測のため表記が不確実)—
# 誤っていてもJP選手所属クラブの試合自体は名前一致で拾えるため、
# 全試合を並べる「対象リーグ」表示からのみ漏れる程度の影響に留まる。
LEAGUE_ALLOWLIST: dict[tuple[str, str], dict] = {
    ("イギリス", "プレミアリーグ"): {"name": "プレミアリーグ", "country_code": "eng", "country_ja": "イングランド"},
    ("イギリス", "プレミアシップ"): {"name": "スコティッシュ・プレミアシップ", "country_code": "sco", "country_ja": "スコットランド"},  # 要検証
    ("イギリス", "FAカップ"): {"name": "FAカップ", "country_code": "eng", "country_ja": "イングランド"},  # 要検証
    ("イギリス", "EFLカップ"): {"name": "EFLカップ", "country_code": "eng", "country_ja": "イングランド"},  # 要検証
    ("イギリス", "スコティッシュカップ"): {"name": "スコティッシュカップ", "country_code": "sco", "country_ja": "スコットランド"},  # 要検証
    ("スペイン", "ラ・リーガ"): {"name": "ラ・リーガ", "country_code": "esp", "country_ja": "スペイン"},
    ("スペイン", "コパ・デル・レイ"): {"name": "コパ・デル・レイ", "country_code": "esp", "country_ja": "スペイン"},  # 要検証
    ("ドイツ", "ブンデスリーガ"): {"name": "ブンデスリーガ", "country_code": "ger", "country_ja": "ドイツ"},
    ("ドイツ", "DFBポカール"): {"name": "DFBポカール", "country_code": "ger", "country_ja": "ドイツ"},  # 要検証
    ("イタリア", "セリエ A"): {"name": "セリエA", "country_code": "ita", "country_ja": "イタリア"},
    ("イタリア", "コッパ・イタリア"): {"name": "コッパ・イタリア", "country_code": "ita", "country_ja": "イタリア"},  # 要検証
    ("フランス", "リーグ・アン"): {"name": "リーグ・アン", "country_code": "fra", "country_ja": "フランス"},
    ("フランス", "クープ・ド・フランス"): {"name": "クープ・ド・フランス", "country_code": "fra", "country_ja": "フランス"},  # 要検証
    ("オランダ", "エールディビジ"): {"name": "エールディヴィジ", "country_code": "ned", "country_ja": "オランダ"},
    ("オランダ", "KNVBベーカー"): {"name": "KNVBベーカー", "country_code": "ned", "country_ja": "オランダ"},  # 要検証
    ("ポルトガル", "リガポルトガル"): {"name": "リーガ・ポルトガル", "country_code": "por", "country_ja": "ポルトガル"},
    ("ポルトガル", "ポルトガルカップ"): {"name": "ポルトガルカップ", "country_code": "por", "country_ja": "ポルトガル"},  # 要検証
    ("ベルギー", "ジュピラー･プロリーグ"): {"name": "ベルギー・プロリーグ", "country_code": "bel", "country_ja": "ベルギー"},
    ("ベルギー", "ベルギーカップ"): {"name": "ベルギーカップ", "country_code": "bel", "country_ja": "ベルギー"},  # 要検証
    ("トルコ", "スーパーリグ"): {"name": "スュペル・リグ", "country_code": "tur", "country_ja": "トルコ"},
    ("トルコ", "トルコカップ"): {"name": "トルコカップ", "country_code": "tur", "country_ja": "トルコ"},  # 要検証
}

# goal.com側の表記がサッカーキング側(jp_clubs.jsonのteam_name_ja)と
# 一致しないクラブの個別対応(判明したものから追加)。
NAME_OVERRIDES: dict[str, str] = {
    "ロサンゼルス・ギャラクシー": "LAギャラクシー",
}

# LEAGUE_ALLOWLIST(トップリーグ+主要カップ)以外で、前方一致/後方一致の
# フォールバックを許可してよいと確認済みの2部相当リーグ。ここに無い
# リーグ(FAカップ予選、USLチャンピオンシップ等)は無関係な下部/海外
# アマチュアクラブが紛れやすく、"イプスウィッチワンダラーズ"が
# "イプスウィッチ"に、"バーミンガムレギオン"が"バーミンガム"に誤って
# 一致する事故が実際に起きたため、完全一致のみ許可する。
_FUZZY_TRUSTED_LEAGUES = {
    "EFL チャンピオンシップ", "2. ブンデスリーガ", "ラ・リーガ 2部",
    "プリメーラ･ナシオナル", "チャレンジャー・プロ・リーグ", "トゥヴェーデディビジー",
    "アルスヴェンスカン",
    "スーパーリーガ", "MLS", "カナディアンチャンピオンシップ",
}

HEADER_RE = re.compile(
    r'fco-competition-section__header-name">([^<]+)</span>'
    r'<span class="fco-competition-section__header-area">([^<]+)</span>'
)
MATCH_RE = re.compile(
    r'data-match-id="([^"]+)" data-match-status="([^"]+)">.*?'
    r'data-team-id="([^"]+)">.*?fco-full-name">([^<]+)</div>'
    r'<div class="fco-team-name fco-code-name">([^<]+)</div>.*?'
    r'data-team-id="([^"]+)">.*?fco-full-name">([^<]+)</div>'
    r'<div class="fco-team-name fco-code-name">([^<]+)</div>',
    re.S,
)
LD_JSON_RE = re.compile(
    r'<script type="application/ld\+json" data-next-head="">(\{[^<]*?"SportsEvent"[^<]*?\})</script>'
)

_last_request_at = 0.0


def _throttle() -> None:
    global _last_request_at
    elapsed = time.monotonic() - _last_request_at
    wait = _MIN_INTERVAL_SEC - elapsed
    if wait > 0:
        time.sleep(wait)
    _last_request_at = time.monotonic()


def _normalize_name(name: str) -> str:
    name = unicodedata.normalize("NFKC", name)
    for ch in "・＝･-　 ":
        name = name.replace(ch, "")
    return name.strip().lower()


def _fetch_day(day: date) -> str:
    url = BASE_URL.format(date=day.isoformat())
    _throttle()
    resp = requests.get(url, headers=REQUEST_HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.text


def _parse_day(html: str) -> list[dict]:
    headers = [(m.start(), m.group(1), m.group(2)) for m in HEADER_RE.finditer(html)]
    header_positions = [h[0] for h in headers]

    ld_by_id: dict[str, dict] = {}
    for m in LD_JSON_RE.finditer(html):
        try:
            block = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        slug = urllib.parse.unquote(block["url"].rstrip("/").split("/")[-1])
        ld_by_id[slug] = block

    matches = []
    for m in MATCH_RE.finditer(html):
        match_id, status, team_a_id, name_a, code_a, team_b_id, name_b, code_b = m.groups()

        idx = _bisect_right(header_positions, m.start()) - 1
        league_name, area = (headers[idx][1], headers[idx][2]) if idx >= 0 else ("", "")

        ld = ld_by_id.get(match_id)
        matches.append(
            {
                "match_id": match_id,
                "status": status,
                "area": area,
                "league_name": league_name,
                "home_team_id": team_a_id,
                "home_team": name_a,
                "home_code": code_a,
                "away_team_id": team_b_id,
                "away_team": name_b,
                "away_code": code_b,
                "kickoff_utc": ld["startDate"] if ld else None,
                "venue": (ld.get("location") or {}).get("name") if ld else None,
                "home_logo": (ld.get("homeTeam") or {}).get("logo") if ld else None,
                "away_logo": (ld.get("awayTeam") or {}).get("logo") if ld else None,
            }
        )
    return matches


def _bisect_right(a: list[int], x: int) -> int:
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if x < a[mid]:
            hi = mid
        else:
            lo = mid + 1
    return lo


_MIN_SUBSTRING_MATCH_LEN = 3

# 育成年代・リザーブ・女子チームなど、トップチームと紛らわしい名前を
# 部分一致で誤って拾わないよう除外する(例: "トッテナムホットスパー
# アカデミー"や"レアル・ソシエダB"、"ヨングPSV"がトップチームの
# "トッテナム"/"レアル・ソシエダ"/"PSV"に部分一致してしまう事故があった)。
_NON_FIRST_TEAM_KEYWORDS = (
    "アカデミー", "ヨング", "フラウエン", "レディース", "女子", "ユース",
    "リザーブ", "リザーヴ", "TFF", "ウィメン", "女性", "WSL", "women", "Women",
    "ダーム",  # スウェーデン語で女性を意味する接頭辞(例: ダームアルスヴェンスカン)
)
_NON_FIRST_TEAM_SUFFIX_RE = re.compile(r"(B|II|U1[0-9]|U2[0-9])$")

# FAカップ予選のような大会名に"予選"を含む競技は、非リーグ所属の
# アマチュアクラブが大量に参加し、たまたま対象クラブと紛らわしい名前
# ("イプスウィッチワンダラーズ"が"イプスウィッチ"に前方一致する等)を
# 持つことが多いため、この種の大会では前方一致/後方一致の
# フォールバックを無効化し、完全一致のみ許可する。
_FUZZY_UNSAFE_COMPETITION_RE = re.compile(r"予選")


def _is_first_team_name(name: str) -> bool:
    name_lower = name.lower()
    if any(kw.lower() in name_lower for kw in _NON_FIRST_TEAM_KEYWORDS):
        return False
    return not _NON_FIRST_TEAM_SUFFIX_RE.search(name)


def _find_club(name: str, club_by_norm_name: dict[str, dict], *, allow_fuzzy: bool) -> dict | None:
    if not _is_first_team_name(name):
        return None
    name_norm = _normalize_name(name)
    exact = club_by_norm_name.get(name_norm)
    if exact is not None:
        return exact
    if not allow_fuzzy:
        return None
    # サッカーキング側が短縮表記("コヴェントリー")、goal.com側が正式名称
    # ("コヴェントリー・シティ")のような表記差を前方一致/後方一致で吸収する。
    # 任意位置の部分一致だと"パルマ"が"ラスパルマス"に誤って一致するなど
    # 無関係なクラブを拾ってしまうため、前方一致・後方一致のみに限定する。
    for club_norm, club in club_by_norm_name.items():
        shorter, longer = sorted([club_norm, name_norm], key=len)
        if len(shorter) < _MIN_SUBSTRING_MATCH_LEN:
            continue
        if longer.startswith(shorter) or longer.endswith(shorter):
            return club
    return None


def main() -> None:
    if not CLUBS_PATH.exists():
        print(f"{CLUBS_PATH} が見つかりません。先に resolve_jp_clubs.py を実行してください。", file=sys.stderr)
        sys.exit(1)

    clubs_data = json.loads(CLUBS_PATH.read_text(encoding="utf-8"))
    clubs = clubs_data["clubs"]
    club_by_norm_name: dict[str, dict] = {}
    for c in clubs:
        ja_name = NAME_OVERRIDES.get(c["team_name_ja"], c["team_name_ja"])
        club_by_norm_name[_normalize_name(ja_name)] = c

    matches_by_team: dict[int, list[dict]] = {c["team_id"]: [] for c in clubs}
    all_matches: list[dict] = []
    seen_match_ids: set[str] = set()

    today = date.today()
    for offset in range(DAYS_AHEAD):
        day = today + timedelta(days=offset)
        try:
            html = _fetch_day(day)
        except requests.RequestException as exc:
            print(f"警告: {day.isoformat()}分の取得に失敗しました: {exc}", file=sys.stderr)
            continue

        for raw in _parse_day(html):
            if raw["match_id"] in seen_match_ids:
                continue
            if raw["kickoff_utc"] is None:
                continue  # JSON-LDと突き合わせられなかった試合はスキップ
            seen_match_ids.add(raw["match_id"])

            if not _is_first_team_name(raw["league_name"]):
                continue  # 女子リーグ・育成年代リーグ自体を丸ごと除外

            league_info = LEAGUE_ALLOWLIST.get((raw["area"], raw["league_name"]))
            allow_fuzzy = league_info is not None or raw["league_name"] in _FUZZY_TRUSTED_LEAGUES

            home_club = _find_club(raw["home_team"], club_by_norm_name, allow_fuzzy=allow_fuzzy)
            away_club = _find_club(raw["away_team"], club_by_norm_name, allow_fuzzy=allow_fuzzy)
            has_jp_club = home_club is not None or away_club is not None

            if league_info is None and not has_jp_club:
                continue

            jp_players = []
            for club in (home_club, away_club):
                if club:
                    jp_players.extend(
                        {"name": p["name"], "team_id": club["team_id"]} for p in club["players"]
                    )

            if league_info is not None:
                league_name = league_info["name"]
                country_code = league_info["country_code"]
                country_ja = league_info["country_ja"]
            else:
                league_name = raw["league_name"]
                country_code = ""
                country_ja = raw["area"]

            match = {
                "fixture_id": raw["match_id"],
                "kickoff_utc": raw["kickoff_utc"],
                "venue": raw["venue"],
                "league_name": league_name,
                "country_code": country_code,
                "country_ja": country_ja,
                "round": None,
                "home_team_id": raw["home_team_id"],
                "home_team": raw["home_team"],
                "home_logo": raw["home_logo"],
                "away_team_id": raw["away_team_id"],
                "away_team": raw["away_team"],
                "away_logo": raw["away_logo"],
                "jp_players": jp_players,
            }
            all_matches.append(match)

            for club in (home_club, away_club):
                if club:
                    matches_by_team[club["team_id"]].append(match)

    all_matches.sort(key=lambda m: m["kickoff_utc"])

    fixtures_by_club = []
    for club in clubs:
        fixtures_by_club.append(
            {
                "team_id": club["team_id"],
                "team_name": club["team_name"],
                "logo": club["logo"],
                "league_name": club["league_name"],
                "players": club["players"],
                "matches": sorted(matches_by_team[club["team_id"]], key=lambda m: m["kickoff_utc"]),
            }
        )

    output = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "clubs": fixtures_by_club,
        "matches": all_matches,
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    jp_count = sum(1 for m in all_matches if m["jp_players"])
    unmatched_clubs = [c["team_name_ja"] for c in clubs if not matches_by_team[c["team_id"]]]
    print(
        f"完了: 全{len(all_matches)}試合(うち日本人選手所属{jp_count}試合)を "
        f"{OUTPUT_PATH} に出力しました。"
    )
    if unmatched_clubs:
        print(f"注意: {DAYS_AHEAD}日以内に試合が見つからなかったクラブ({len(unmatched_clubs)}件): {unmatched_clubs}")


if __name__ == "__main__":
    main()
