from __future__ import annotations

# plant_yolo.pt 진단 모델의 원시 라벨(영문, snake_case) → 한국어 단어 매핑.
# www/lib/plant-labels.ts 와 동일한 클래스 집합을 유지한다(프론트는 표기용 영문 병기 포함,
# 백엔드는 LLM 프롬프트·일관성 검증에 쓰이므로 한글 단어만 보관한다).
# 매핑에 없는 값은 원문 그대로 반환한다(모델 클래스가 늘어나도 깨지지 않도록).

_SPECIES_KO: dict[str, str] = {
    # 하우스플랜트 47종 — 현재 plant_yolo.pt(품종 전용 분류기)가 내놓는 클래스.
    "african_violet_saintpaulia_ionantha": "아프리칸바이올렛",
    "aloe_vera": "알로에베라",
    "anthurium_anthurium_andraeanum": "안스리움",
    "areca_palm_dypsis_lutescens": "아레카야자",
    "asparagus_fern_asparagus_setaceus": "아스파라거스고사리",
    "begonia_begonia_spp": "베고니아",
    "bird_of_paradise_strelitzia_reginae": "극락조화",
    "birds_nest_fern_asplenium_nidus": "아스플레니움",
    "boston_fern_nephrolepis_exaltata": "보스턴고사리",
    "calathea": "칼라테아",
    "cast_iron_plant_aspidistra_elatior": "엽란",
    "chinese_evergreen_aglaonema": "아글라오네마",
    "chinese_money_plant_pilea_peperomioides": "필레아",
    "christmas_cactus_schlumbergera_bridgesii": "크리스마스선인장",
    "chrysanthemum": "국화",
    "ctenanthe": "크테난테",
    "daffodils_narcissus_spp": "수선화",
    "dracaena": "드라세나",
    "dumb_cane_dieffenbachia_spp": "디펜바키아",
    "elephant_ear_alocasia_spp": "알로카시아",
    "english_ivy_hedera_helix": "아이비",
    "hyacinth_hyacinthus_orientalis": "히아신스",
    "iron_cross_begonia_begonia_masoniana": "아이언크로스베고니아",
    "jade_plant_crassula_ovata": "염좌",
    "kalanchoe": "칼랑코에",
    "lilium_hemerocallis": "원추리",
    "lily_of_the_valley_convallaria_majalis": "은방울꽃",
    "money_tree_pachira_aquatica": "파키라",
    "monstera_deliciosa_monstera_deliciosa": "몬스테라",
    "orchid": "난",
    "parlor_palm_chamaedorea_elegans": "테이블야자",
    "peace_lily": "스파티필럼",
    "poinsettia_euphorbia_pulcherrima": "포인세티아",
    "polka_dot_plant_hypoestes_phyllostachya": "히포에스테스",
    "ponytail_palm_beaucarnea_recurvata": "포니테일야자",
    "pothos_ivy_arum": "스킨답서스",
    "prayer_plant_maranta_leuconeura": "마란타",
    "rattlesnake_plant_calathea_lancifolia": "칼라테아 란시폴리아",
    "rubber_plant_ficus_elastica": "고무나무",
    "sago_palm_cycas_revoluta": "소철",
    "schefflera": "홍콩야자",
    "snake_plant_sanseviera": "산세베리아",
    "tradescantia": "자주달개비",
    "tulip": "튤립",
    "venus_flytrap": "파리지옥",
    "yucca": "유카",
    "zz_plant_zamioculcas_zamiifolia": "금전수",
}

# 품종 전용(증상 라벨 없는) 분류기가 내놓는 라벨에 붙이는 sentinel.
# "healthy"로 임의 대체하면 실제로는 모르는 상태를 확신하는 것처럼 보이므로 구분한다.
SYMPTOM_NOT_ASSESSED = "not_assessed"

_SYMPTOM_KO: dict[str, str] = {
    "healthy": "건강함",
    SYMPTOM_NOT_ASSESSED: "증상 미판정",
    "rust": "녹병",
    "scab": "검은별무늬병",
    "leaf_spot": "잎반점병",
    "gray_leaf_spot": "회색잎마름병",
    "leaf_blight": "잎마름병",
    "black_rot": "흑부병",
    "early_blight": "겹무늬병",
    "late_blight": "역병",
    "powdery_mildew": "흰가루병",
    "bacterial_spot": "세균성반점병",
    "mold": "잎곰팡이병",
    "mosaic_virus": "모자이크바이러스병",
    "septoria_leaf_spot": "세프토리아잎반점병",
    "spider_mites": "점박이응애",
    "yellow_virus": "황화바이러스병",
}


def translate_species(raw: str) -> str:
    return _SPECIES_KO.get(raw, raw)


def translate_symptom(raw: str) -> str:
    return _SYMPTOM_KO.get(raw, raw)
