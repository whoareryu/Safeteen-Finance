"""식집사 튜토리얼 — 종 카탈로그 · 상태 판정 · 사진 검색어 조합. 프랙탈 밖 공유 VO."""

from __future__ import annotations

from dataclasses import dataclass

from plant.domain.value_objects.growth_stage import MATURE, NEW_SHOOT, SPROUT

LIGHT_SHADE = "음지"
LIGHT_PARTIAL = "반양지"
LIGHT_SUN = "양지"

STATUS_HEALTHY = "healthy"
STATUS_THIRSTY = "thirsty"
STATUS_OVERWATERED = "overwatered"
STATUS_NUTRIENT_LOW = "nutrient_low"

_THIRSTY_THRESHOLD = 30.0
_OVERWATERED_THRESHOLD = 90.0
_NUTRIENT_LOW_THRESHOLD = 30.0


@dataclass(frozen=True)
class TutorialSpeciesOption:
    name: str
    query_keyword: str


TUTORIAL_SPECIES: tuple[TutorialSpeciesOption, ...] = (
    TutorialSpeciesOption("몬스테라", "monstera plant"),
    TutorialSpeciesOption("스킨답서스", "pothos plant"),
    TutorialSpeciesOption("산세베리아", "snake plant"),
    TutorialSpeciesOption("스투키", "sansevieria stuckyi plant"),
    TutorialSpeciesOption("홍콩야자", "schefflera plant"),
    TutorialSpeciesOption("선인장", "cactus plant"),
)


def find_species(name: str) -> TutorialSpeciesOption | None:
    return next((s for s in TUTORIAL_SPECIES if s.name == name), None)


def compute_status(soil_moisture_pct: float, nutrient_pct: float) -> str:
    if soil_moisture_pct < _THIRSTY_THRESHOLD:
        return STATUS_THIRSTY
    if soil_moisture_pct > _OVERWATERED_THRESHOLD:
        return STATUS_OVERWATERED
    if nutrient_pct < _NUTRIENT_LOW_THRESHOLD:
        return STATUS_NUTRIENT_LOW
    return STATUS_HEALTHY


_STAGE_KEYWORDS = {
    SPROUT: "seedling in pot",
    NEW_SHOOT: "young potted plant",
    MATURE: "mature potted plant",
}

_STATUS_KEYWORDS = {
    STATUS_HEALTHY: "healthy",
    STATUS_THIRSTY: "wilting dry soil",
    STATUS_OVERWATERED: "overwatered soggy soil",
    STATUS_NUTRIENT_LOW: "pale leaves",
}


def build_photo_query(species_query_keyword: str, growth_stage: str, status_key: str) -> str:
    stage_kw = _STAGE_KEYWORDS.get(growth_stage, _STAGE_KEYWORDS[SPROUT])
    status_kw = _STATUS_KEYWORDS.get(status_key, _STATUS_KEYWORDS[STATUS_HEALTHY])
    return f"{species_query_keyword} {stage_kw} {status_kw}"
