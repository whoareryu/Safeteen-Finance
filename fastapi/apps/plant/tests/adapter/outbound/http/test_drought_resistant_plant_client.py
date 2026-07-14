from __future__ import annotations

from plant.adapter.outbound.http.drought_resistant_plant_client import _parse_detail, _parse_list

_LIST_XML = """<?xml version="1.0" encoding="UTF-8"?>
<response><header><resultCode>00</resultCode><resultMsg>정상적으로 처리되었습니다.</resultMsg></header>
<body><items><item><cntntsNo><![CDATA[204870]]></cntntsNo>
<cntntsSj><![CDATA[페페로미아 그라베올렌스]]></cntntsSj></item></items></body></response>"""

_DETAIL_XML = """<?xml version="1.0" encoding="UTF-8"?>
<response><header><resultCode>00</resultCode><resultMsg>정상적으로 처리되었습니다.</resultMsg></header>
<body><item><cntntsNo><![CDATA[204870]]></cntntsNo>
<waterCycleInfo><![CDATA[분 흙이 마르면 흠뻑 관수 한겨울에는 단수]]></waterCycleInfo>
<lighttInfo><![CDATA[충분한 광 필요]]></lighttInfo>
<manageLevelNm><![CDATA[어려움]]></manageLevelNm>
<dlthtsInfo></dlthtsInfo>
<tipInfo><![CDATA[직사광선 및 다습한 환경을 피함]]></tipInfo>
<pswntrTpInfo><![CDATA[10°C]]></pswntrTpInfo>
<orgplce><![CDATA[페루]]></orgplce>
</item></body></response>"""


def test_parse_list_extracts_cntnts_no_and_title():
    items = _parse_list(_LIST_XML)

    assert items == [("204870", "페페로미아 그라베올렌스")]


def test_parse_detail_maps_fields_and_drops_empty_tags():
    fact = _parse_detail(_DETAIL_XML, "페페로미아 그라베올렌스")

    assert fact is not None
    assert fact.species_name == "페페로미아 그라베올렌스"
    assert fact.source_api == "drought_resistant"
    assert fact.attributes == {
        "waterCycleInfo": "분 흙이 마르면 흠뻑 관수 한겨울에는 단수",
        "lightInfo": "충분한 광 필요",
        "manageLevel": "어려움",
        "careTip": "직사광선 및 다습한 환경을 피함",
        "minWinterTemp": "10°C",
        "originInfo": "페루",
    }
