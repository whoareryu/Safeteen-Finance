"""농사로 — 실내정원용 식물(garden) API."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from plant.adapter.outbound.http.http_util import http_get_text
from plant.app.dtos.knowledge_sync_dto import PlantKnowledgeFact
from plant.app.ports.output.plant_knowledge_source_port import PlantKnowledgeSourcePort
from plant.config.external_settings import get_external_settings

_BASE_URL = "http://api.nongsaro.go.kr/service/garden"
_SOURCE_API = "indoor_garden"

_DETAIL_FIELD_MAP = {
    "watercycleSprngCodeNm": "waterCycleSpring",
    "watercycleSummerCodeNm": "waterCycleSummer",
    "watercycleAutumnCodeNm": "waterCycleAutumn",
    "watercycleWinterCodeNm": "waterCycleWinter",
    "lighttdemanddoCodeNm": "lightInfo",
    "managelevelCodeNm": "manageLevel",
    "toxctyInfo": "toxicityInfo",
    "adviseInfo": "careTip",
    "hdCodeNm": "idealHumidity",
    "grwhTpCodeNm": "idealTempRange",
    "orgplceInfo": "originInfo",
}


def _text(item: ET.Element, tag: str) -> str:
    node = item.find(tag)
    return (node.text or "").strip() if node is not None and node.text else ""


def _parse_list(xml_text: str) -> list[tuple[str, str]]:
    root = ET.fromstring(xml_text)
    return [
        (_text(item, "cntntsNo"), _text(item, "cntntsSj"))
        for item in root.findall(".//item")
        if _text(item, "cntntsNo")
    ]


def _parse_detail(xml_text: str, species_name: str) -> PlantKnowledgeFact | None:
    root = ET.fromstring(xml_text)
    item = root.find(".//item")
    if item is None:
        return None
    attributes = {
        mapped_key: value
        for source_tag, mapped_key in _DETAIL_FIELD_MAP.items()
        if (value := _text(item, source_tag))
    }
    return PlantKnowledgeFact(
        species_name=species_name, source_api=_SOURCE_API, attributes=attributes
    )


class IndoorGardenPlantClient(PlantKnowledgeSourcePort):

    def __init__(self, page_size: int = 20) -> None:
        self._page_size = page_size

    def fetch_all(self) -> list[PlantKnowledgeFact]:
        settings = get_external_settings()
        if not settings.indoor_garden_configured:
            return []

        api_key = settings.plant_indoor_garden_api_key
        status, list_xml = http_get_text(
            f"{_BASE_URL}/gardenList?apiKey={api_key}&pageNo=1&numOfRows={self._page_size}"
        )
        if status != 200:
            return []

        facts: list[PlantKnowledgeFact] = []
        for cntnts_no, species_name in _parse_list(list_xml):
            detail_status, detail_xml = http_get_text(
                f"{_BASE_URL}/gardenDtl?apiKey={api_key}&cntntsNo={cntnts_no}"
            )
            if detail_status != 200:
                continue
            fact = _parse_detail(detail_xml, species_name)
            if fact is not None:
                facts.append(fact)
        return facts
