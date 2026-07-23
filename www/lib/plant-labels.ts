/** plant_yolo.pt 진단 모델의 원시 라벨(영문, snake_case) → 한국어 표기 매핑.
 * 매핑에 없는 값은 원문 그대로 보여준다(모델 클래스가 늘어나도 깨지지 않도록). */

const SPECIES_KO: Record<string, string> = {
  // 하우스플랜트 47종 — 현재 plant_yolo.pt(품종 전용 분류기)가 내놓는 클래스.
  african_violet_saintpaulia_ionantha: "아프리칸바이올렛(African Violet)",
  aloe_vera: "알로에베라(Aloe Vera)",
  anthurium_anthurium_andraeanum: "안스리움(Anthurium)",
  areca_palm_dypsis_lutescens: "아레카야자(Areca Palm)",
  asparagus_fern_asparagus_setaceus: "아스파라거스고사리(Asparagus Fern)",
  begonia_begonia_spp: "베고니아(Begonia)",
  bird_of_paradise_strelitzia_reginae: "극락조화(Bird of Paradise)",
  birds_nest_fern_asplenium_nidus: "아스플레니움(Bird's Nest Fern)",
  boston_fern_nephrolepis_exaltata: "보스턴고사리(Boston Fern)",
  calathea: "칼라테아(Calathea)",
  cast_iron_plant_aspidistra_elatior: "엽란(Cast Iron Plant)",
  chinese_evergreen_aglaonema: "아글라오네마(Chinese Evergreen)",
  chinese_money_plant_pilea_peperomioides: "필레아(Chinese Money Plant)",
  christmas_cactus_schlumbergera_bridgesii: "크리스마스선인장(Christmas Cactus)",
  chrysanthemum: "국화(Chrysanthemum)",
  ctenanthe: "크테난테(Ctenanthe)",
  daffodils_narcissus_spp: "수선화(Daffodil)",
  dracaena: "드라세나(Dracaena)",
  dumb_cane_dieffenbachia_spp: "디펜바키아(Dumb Cane)",
  elephant_ear_alocasia_spp: "알로카시아(Elephant Ear)",
  english_ivy_hedera_helix: "아이비(English Ivy)",
  hyacinth_hyacinthus_orientalis: "히아신스(Hyacinth)",
  iron_cross_begonia_begonia_masoniana: "아이언크로스베고니아(Iron Cross Begonia)",
  jade_plant_crassula_ovata: "염좌(Jade Plant)",
  kalanchoe: "칼랑코에(Kalanchoe)",
  lilium_hemerocallis: "원추리(Daylily)",
  lily_of_the_valley_convallaria_majalis: "은방울꽃(Lily of the Valley)",
  money_tree_pachira_aquatica: "파키라(Money Tree)",
  monstera_deliciosa_monstera_deliciosa: "몬스테라(Monstera)",
  orchid: "난(Orchid)",
  parlor_palm_chamaedorea_elegans: "테이블야자(Parlor Palm)",
  peace_lily: "스파티필럼(Peace Lily)",
  poinsettia_euphorbia_pulcherrima: "포인세티아(Poinsettia)",
  polka_dot_plant_hypoestes_phyllostachya: "히포에스테스(Polka Dot Plant)",
  ponytail_palm_beaucarnea_recurvata: "포니테일야자(Ponytail Palm)",
  pothos_ivy_arum: "스킨답서스(Pothos)",
  prayer_plant_maranta_leuconeura: "마란타(Prayer Plant)",
  rattlesnake_plant_calathea_lancifolia: "칼라테아 란시폴리아(Rattlesnake Plant)",
  rubber_plant_ficus_elastica: "고무나무(Rubber Plant)",
  sago_palm_cycas_revoluta: "소철(Sago Palm)",
  schefflera: "홍콩야자(Schefflera)",
  snake_plant_sanseviera: "산세베리아(Snake Plant)",
  tradescantia: "자주달개비(Tradescantia)",
  tulip: "튤립(Tulip)",
  venus_flytrap: "파리지옥(Venus Flytrap)",
  yucca: "유카(Yucca)",
  zz_plant_zamioculcas_zamiifolia: "금전수(ZZ Plant)",
};

const SYMPTOM_KO: Record<string, string> = {
  healthy: "건강함(Healthy)",
  not_assessed: "증상 미판정",
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
