/** plant_yolo.pt 진단 모델의 원시 라벨(영문, snake_case) → 한국어 표기 매핑.
 * 매핑에 없는 값은 원문 그대로 보여준다(모델 클래스가 늘어나도 깨지지 않도록). */

const SPECIES_KO: Record<string, string> = {
  apple: "사과(Apple)",
  bell_pepper: "피망(Bell Pepper)",
  blueberry: "블루베리(Blueberry)",
  cherry: "체리(Cherry)",
  corn: "옥수수(Corn)",
  grape: "포도(Grape)",
  peach: "복숭아(Peach)",
  potato: "감자(Potato)",
  raspberry: "라즈베리(Raspberry)",
  soybean: "대두(Soybean)",
  squash: "스쿼시(Squash)",
  strawberry: "딸기(Strawberry)",
  tomato: "토마토(Tomato)",
};

const SYMPTOM_KO: Record<string, string> = {
  healthy: "건강함(Healthy)",
  rust: "녹병(Rust)",
  scab: "검은별무늬병(Scab)",
  leaf_spot: "잎반점병(Leaf Spot)",
  gray_leaf_spot: "회색잎마름병(Gray Leaf Spot)",
  leaf_blight: "잎마름병(Leaf Blight)",
  black_rot: "흑부병(Black Rot)",
  early_blight: "겹무늬병(Early Blight)",
  late_blight: "역병(Late Blight)",
  powdery_mildew: "흰가루병(Powdery Mildew)",
  bacterial_spot: "세균성반점병(Bacterial Spot)",
  mold: "잎곰팡이병(Mold)",
  mosaic_virus: "모자이크바이러스병(Mosaic Virus)",
  septoria_leaf_spot: "세프토리아잎반점병(Septoria Leaf Spot)",
  spider_mites: "점박이응애(Spider Mites)",
  yellow_virus: "황화바이러스병(Yellow Virus)",
};

export function translateSpecies(raw: string): string {
  return SPECIES_KO[raw] ?? raw;
}

export function translateSymptom(raw: string): string {
  return SYMPTOM_KO[raw] ?? raw;
}
