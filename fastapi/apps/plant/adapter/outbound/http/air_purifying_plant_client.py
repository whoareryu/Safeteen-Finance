"""공공데이터포털 — 공기정화식물(NihhsFuriAirInfo) API.

주의: ``servicekey`` 승인 직후 활성화 대기 상태라 아직 실제 응답으로
검증하지 못했다. 활용가이드 문서(selectPuriAirPlantList/selectPuriAirPlantView)의
필드 스펙만으로 작성한 최선 추정 파서이므로, 키가 활성화되면 반드시 실제
응답으로 재검증해야 한다.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

from plant.adapter.outbound.http.http_util import http_get_text
from plant.app.dtos.knowledge_sync_dto import PlantKnowledgeFact
from plant.app.ports.output.plant_knowledge_source_port import PlantKnowledgeSourcePort
from plant.config.external_settings import get_external_settings

_BASE_URL = "https://apis.data.go.kr/1390804/NihhsFuriAirInfo"
_SOURCE_API = "air_purifying"

_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


def _text(item: ET.Element, tag: str) -> str:
    node = item.find(tag)
    return (node.text or "").strip() if node is not None and node.text else ""


def _strip_html(html: str) -> str:
    return _WHITESPACE_RE.sub(" ", _TAG_RE.sub(" ", html)).strip()


def _parse_list(xml_text: str) -> list[tuple[str, str]]:
    root = ET.fromstring(xml_text)
    return [
        (_text(row, "idx"), _text(row, "title"))
        for row in root.findall(".//result")
        if _text(row, "idx")
    ]


def _parse_detail(xml_text: str, species_name: str) -> PlantKnowledgeFact | None:
    root = ET.fromstring(xml_text)
    row = root.find(".//result")
    if row is None:
        return None
    html_content = _text(row, "htmlContent")
    attributes: dict[str, str] = {"airPurifying": "true"}
    if html_content:
        attributes["careTip"] = _strip_html(html_content)
    return PlantKnowledgeFact(
        species_name=species_name, source_api=_SOURCE_API, attributes=attributes
    )


class AirPurifyingPlantClient(PlantKnowledgeSourcePort):

    def __init__(self, page_size: int = 20) -> None:
        self._page_size = page_size

    def fetch_all(self) -> list[PlantKnowledgeFact]:
        settings = get_external_settings()
        if not settings.air_purifying_configured:
            return []

        api_key = settings.plant_air_purifying_api_key
        status, list_xml = http_get_text(
            f"{_BASE_URL}/selectPuriAirPlantList"
            f"?servicekey={api_key}&numOfRows={self._page_size}&pageNo=1"
        )
        if status != 200:
            return []

        facts: list[PlantKnowledgeFact] = []
        for idx, title in _parse_list(list_xml):
            detail_status, detail_xml = http_get_text(
                f"{_BASE_URL}/selectPuriAirPlantView?idx={idx}&servicekey={api_key}"
            )
            if detail_status != 200:
                continue
            fact = _parse_detail(detail_xml, title)
            if fact is not None:
                facts.append(fact)
        return facts
