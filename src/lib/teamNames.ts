/**
 * API-Footballは英語のクラブ名しか返さないため、日本語表示用の対応表を用意する。
 * 対象リーグ(config.pyのLEAGUES)の主要クラブを中心に収録。
 * 未収録のクラブは英語名のままフォールバック表示する。
 */
const TEAM_NAME_JA: Record<string, string> = {
  // プレミアリーグ
  Arsenal: "アーセナル",
  "Aston Villa": "アストン・ヴィラ",
  Bournemouth: "ボーンマス",
  Brentford: "ブレントフォード",
  Brighton: "ブライトン",
  Burnley: "バーンリー",
  Chelsea: "チェルシー",
  "Crystal Palace": "クリスタル・パレス",
  Everton: "エヴァートン",
  Fulham: "フラム",
  Liverpool: "リバプール",
  "Manchester City": "マンチェスター・シティ",
  "Manchester United": "マンチェスター・ユナイテッド",
  Newcastle: "ニューカッスル",
  "Nottingham Forest": "ノッティンガム・フォレスト",
  Sunderland: "サンダーランド",
  Tottenham: "トッテナム",
  "West Ham": "ウェストハム",
  Wolves: "ウォルバーハンプトン",

  // ラ・リーガ
  Alaves: "アラベス",
  "Athletic Club": "アスレティック・ビルバオ",
  "Atletico Madrid": "アトレティコ・マドリード",
  Barcelona: "バルセロナ",
  "Celta Vigo": "セルタ・ビーゴ",
  Elche: "エルチェ",
  Espanyol: "エスパニョール",
  Getafe: "ヘタフェ",
  Girona: "ジローナ",
  Levante: "レバンテ",
  Mallorca: "マヨルカ",
  Osasuna: "オサスナ",
  "Rayo Vallecano": "ラージョ・バジェカーノ",
  "Real Betis": "レアル・ベティス",
  "Real Madrid": "レアル・マドリード",
  "Real Oviedo": "レアル・オビエド",
  "Real Sociedad": "レアル・ソシエダ",
  Sevilla: "セビージャ",
  Valencia: "バレンシア",
  Villarreal: "ビジャレアル",

  // ブンデスリーガ
  Augsburg: "アウクスブルク",
  "Bayer Leverkusen": "バイエル・レバークーゼン",
  "Bayern Munich": "バイエルン・ミュンヘン",
  "Werder Bremen": "ヴェルダー・ブレーメン",
  "Borussia Dortmund": "ボルシア・ドルトムント",
  "Eintracht Frankfurt": "アイントラハト・フランクフルト",
  Freiburg: "フライブルク",
  Heidenheim: "ハイデンハイム",
  Hoffenheim: "ホッフェンハイム",
  "Union Berlin": "ウニオン・ベルリン",
  "RB Leipzig": "RBライプツィヒ",
  Mainz: "マインツ",
  "Borussia Monchengladbach": "ボルシア・メンヒェングラートバッハ",
  "St Pauli": "ザンクトパウリ",
  "FC Koln": "ケルン",
  "VfB Stuttgart": "シュツットガルト",
  Wolfsburg: "ヴォルフスブルク",
  "Hamburger SV": "ハンブルガーSV",

  // セリエA
  Atalanta: "アタランタ",
  Bologna: "ボローニャ",
  Cagliari: "カリアリ",
  Como: "コモ",
  Cremonese: "クレモネーゼ",
  Fiorentina: "フィオレンティーナ",
  Genoa: "ジェノア",
  "Hellas Verona": "エラス・ヴェローナ",
  Inter: "インテル",
  Juventus: "ユヴェントス",
  Lazio: "ラツィオ",
  Lecce: "レッチェ",
  "AC Milan": "ACミラン",
  Napoli: "ナポリ",
  Parma: "パルマ",
  Pisa: "ピサ",
  Roma: "ローマ",
  Sassuolo: "サッスオーロ",
  Torino: "トリノ",
  Udinese: "ウディネーゼ",

  // リーグ・アン
  Angers: "アンジェ",
  Auxerre: "オセール",
  Brest: "ブレスト",
  "Le Havre": "ル・アーヴル",
  Lens: "ランス",
  Lille: "リール",
  Lorient: "ロリアン",
  Lyon: "リヨン",
  Marseille: "マルセイユ",
  Metz: "メス",
  Monaco: "モナコ",
  Nantes: "ナント",
  Nice: "ニース",
  "Paris FC": "パリFC",
  "Paris Saint Germain": "パリ・サンジェルマン",
  Rennes: "レンヌ",
  Strasbourg: "ストラスブール",
  Toulouse: "トゥールーズ",

  // エールディヴィジ
  Ajax: "アヤックス",
  "AZ Alkmaar": "AZアルクマール",
  Feyenoord: "フェイエノールト",
  PSV: "PSVアイントホーフェン",
  "FC Twente": "FCトゥエンテ",
  "FC Utrecht": "FCユトレヒト",
  "Go Ahead Eagles": "ゴー・アヘッド・イーグルス",
  Groningen: "フローニンゲン",
  Heerenveen: "ヘーレンフェーン",
  "Fortuna Sittard": "フォルトゥナ・シッタルト",
  "NAC Breda": "NACブレダ",
  "NEC Nijmegen": "NECナイメヘン",
  "PEC Zwolle": "PECズヴォレ",
  "Sparta Rotterdam": "スパルタ・ロッテルダム",
  Volendam: "フォレンダム",

  // その他、日本人選手所属実績のあるクラブ
  Southampton: "サウサンプトン",
  "Stade Brestois 29": "ブレスト",

  // チャンピオンシップ(イングランド2部)
  "Coventry City": "コヴェントリー・シティ",
  "Stoke City": "ストーク・シティ",
  "Hull City": "ハル・シティ",
  "Blackburn Rovers": "ブラックバーン",
  "Birmingham City": "バーミンガム・シティ",
  Leeds: "リーズ・ユナイテッド",

  // スコットランド
  Rangers: "レンジャーズ",

  // ベルギー
  "Sint-Truiden": "シント＝トロイデン",
  Gent: "ゲント",
};

export function translateTeamName(name: string): string {
  return TEAM_NAME_JA[name] ?? name;
}
