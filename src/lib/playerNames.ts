/**
 * データ取得元(API-Football)は選手名をローマ字("K. Mitoma"のような
 * 「頭文字. 名字」形式)でしか返さないため、日本語表示用の対応表を用意する。
 * 名字(ローマ字)をキーにして日本語のフルネームを引く。
 * 未収録の名字はローマ字表記のままフォールバック表示する。
 */
const PLAYER_NAME_JA: Record<string, string> = {
  Mitoma: "三笘薫",
  Kubo: "久保建英",
  Endo: "遠藤航",
  Tomiyasu: "冨安健洋",
  Kamada: "鎌田大地",
  Doan: "堂安律",
  Minamino: "南野拓実",
  Maeda: "前田大然",
  Asano: "浅野拓磨",
  Ueda: "上田綺世",
  Taniguchi: "谷口彰悟",
  Itakura: "板倉滉",
  Hatate: "旗手怜央",
  Suzuki: "鈴木彩艶",
  Nakamura: "中村敬斗",
  Morita: "守田英正",
  Kawashima: "川島永嗣",
  Sugawara: "菅原由勢",
  Hashioka: "橋岡大樹",
  Tanaka: "田中碧",
  Sakai: "酒井宏樹",
  Ito: "伊藤洋輝",
  Kobayashi: "小林友希",
  Sakamoto: "坂元達裕",
  Takai: "高井幸大",
  Matsuki: "松木玖生",
  Ohashi: "大橋祐紀",
  Morishita: "森下龍矢",
  Iwata: "岩田智輝",
  Fujimoto: "藤本寛也",
  Yokota: "横田大祐",
  Matsuzawa: "松澤海斗",
  Hata: "畑大雅",
  Shinkawa: "新川志音",
  Araki: "荒木遼太郎",
  Osada: "長田澪",
  Yamamoto: "山本理仁",
  Goto: "後藤啓介",
  Shiogai: "塩貝健人",
  Sano: "佐野海舟",
  Kawasaki: "川﨑颯太",
  Machino: "町野修斗",
  Uno: "宇野禅斗",
  Kosugi: "小杉啓太",
  Fujita: "藤田譲瑠チマ",
  Ando: "安藤智哉",
  Hara: "原大智",
  Sekine: "関根大輝",
  Onoda: "小野田亮汰",
  Fukui: "福井太智",
  Fukuda: "福田師王",
};

export function translatePlayerName(name: string): string {
  const surname = name.includes(".") ? name.split(".").pop()!.trim() : name;
  return PLAYER_NAME_JA[surname] ?? name;
}
