/** スタジアム名の日本語表記対応表。未収録の場合は英語名のままフォールバック。 */
const VENUE_NAME_JA: Record<string, string> = {
  // プレミアリーグ
  "Emirates Stadium": "エミレーツ・スタジアム",
  "Villa Park": "ヴィラ・パーク",
  "Vitality Stadium": "ヴァイタリティ・スタジアム",
  "Gtech Community Stadium": "ジーテック・コミュニティ・スタジアム",
  "American Express Stadium": "アメックス・スタジアム",
  "Turf Moor": "ターフ・ムーア",
  "Stamford Bridge": "スタンフォード・ブリッジ",
  "Selhurst Park": "セルハースト・パーク",
  "Goodison Park": "グディソン・パーク",
  "Hill Dickinson Stadium": "ヒル・ディキンソン・スタジアム",
  "Craven Cottage": "クレイヴン・コテージ",
  "Elland Road": "エランド・ロード",
  Anfield: "アンフィールド",
  "Etihad Stadium": "エティハド・スタジアム",
  "Old Trafford": "オールド・トラッフォード",
  "St James' Park": "セント・ジェームズ・パーク",
  "City Ground": "シティ・グラウンド",
  "Stadium of Light": "スタジアム・オブ・ライト",
  "Tottenham Hotspur Stadium": "トッテナム・ホットスパー・スタジアム",
  "London Stadium": "ロンドン・スタジアム",
  "Molineux Stadium": "モリニュー・スタジアム",
  "St Mary's Stadium": "セント・メリーズ・スタジアム",

  // ラ・リーガ
  "Santiago Bernabeu": "サンティアゴ・ベルナベウ",
  "Civitas Metropolitano": "シビタス・メトロポリターノ",
  "Reale Arena": "レアレ・アリーナ",
  "Estadio de la Ceramica": "エスタディオ・デ・ラ・セラミカ",
  "San Mames": "サン・マメス",
  "Ramon Sanchez Pizjuan": "ラモン・サンチェス・ピスファン",
  "Benito Villamarin": "ベニート・ビジャマリン",
  Mestalla: "メスタージャ",

  // ブンデスリーガ
  "Allianz Arena": "アリアンツ・アレーナ",
  "Signal Iduna Park": "ジグナル・イドゥナ・パルク",
  "Red Bull Arena": "レッドブル・アレーナ",
  BayArena: "バイアレーナ",
  "Deutsche Bank Park": "ドイチェ・バンク・パルク",
  MHPArena: "MHPアレーナ",

  // セリエA
  "San Siro": "サン・シーロ",
  "Stadio Giuseppe Meazza": "サン・シーロ",
  "Allianz Stadium": "アリアンツ・スタジアム",
  "Stadio Olimpico": "スタディオ・オリンピコ",
  "Stadio Diego Armando Maradona": "ディエゴ・アルマンド・マラドーナ・スタジアム",
  "Stadio Ennio Tardini": "エンニオ・タルディーニ・スタジアム",

  // リーグ・アン
  "Parc des Princes": "パルク・デ・プランス",
  "Stade Velodrome": "スタッド・ヴェロドローム",
  "Groupama Stadium": "グループアマ・スタジアム",
  "Stade Louis II": "スタッド・ルイ2世",

  // エールディヴィジ
  "Johan Cruyff Arena": "ヨハン・クライフ・アレナ",
  "Philips Stadion": "フィリップス・スタディオン",
  "Stadion Feijenoord": "デ・カウプ",
};

export function translateVenueName(name: string | null): string | null {
  if (!name) return name;
  return VENUE_NAME_JA[name] ?? name;
}

/** "Regular Season - 3" のような英語の節数表記を「第3節」形式に変換する。対応できない形式は原文のまま返す。 */
export function translateRound(round: string | null): string | null {
  if (!round) return round;
  const regularSeason = round.match(/^Regular Season\s*-\s*(\d+)$/i);
  if (regularSeason) return `第${regularSeason[1]}節`;

  const knockoutMap: Record<string, string> = {
    "Round of 16": "ベスト16",
    "Quarter-finals": "準々決勝",
    "Semi-finals": "準決勝",
    Final: "決勝",
  };
  return knockoutMap[round] ?? round;
}
