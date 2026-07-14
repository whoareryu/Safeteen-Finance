from __future__ import annotations

from plant.adapter.outbound.http.indoor_garden_plant_client import _parse_detail, _parse_list

_LIST_XML = """<?xml version="1.0" encoding="UTF-8"?>
<response><header><resultCode>00</resultCode><resultMsg>정상적으로 처리되었습니다.</resultMsg></header>
<body><items><item><cntntsNo><![CDATA[12938]]></cntntsNo>
<cntntsSj><![CDATA[가울테리아]]></cntntsSj></item></items></body></response>"""

_DETAIL_XML = """<?xml version="1.0" encoding="UTF-8"?>
<response><header><resultCode>00</resultCode><resultMsg>정상적으로 처리되었습니다.</resultMsg></header>
<body><item><cntntsNo><![CDATA[12938]]></cntntsNo>
<adviseInfo><![CDATA[식용, 지피, 약용, 향기,관엽, 관화, 관실]]></adviseInfo>
<toxctyInfo></toxctyInfo>
<hdCodeNm><![CDATA[40 ~ 70%]]></hdCodeNm>
<grwhTpCodeNm><![CDATA[16~20℃]]></grwhTpCodeNm>
<lighttdemanddoCodeNm><![CDATA[중간 광도(800~1,500 Lux),높은 광도(1,500~10,000 Lux)]]></lighttdemanddoCodeNm>
<managelevelCodeNm><![CDATA[경험자]]></managelevelCodeNm>
<orgplceInfo><![CDATA[아시아, 아메리카,캐나다]]></orgplceInfo>
<watercycleSprngCodeNm><![CDATA[토양 표면이 말랐을때 충분히 관수함]]></watercycleSprngCodeNm>
<watercycleSummerCodeNm><![CDATA[토양 표면이 말랐을때 충분히 관수함]]></watercycleSummerCodeNm>
<watercycleAutumnCodeNm><![CDATA[토양 표면이 말랐을때 충분히 관수함]]></watercycleAutumnCodeNm>
<watercycleWinterCodeNm><![CDATA[화분 흙 대부분 말랐을때 충분히 관수함]]></watercycleWinterCodeNm>
</item></body></response>"""


def test_parse_list_extracts_cntnts_no_and_title():
    items = _parse_list(_LIST_XML)

    assert items == [("12938", "가울테리아")]


def test_parse_detail_maps_fields_and_drops_empty_tags():
    fact = _parse_detail(_DETAIL_XML, "가울테리아")

    assert fact is not None
    assert fact.species_name == "가울테리아"
    assert fact.source_api == "indoor_garden"
    assert fact.attributes == {
        "careTip": "식용, 지피, 약용, 향기,관엽, 관화, 관실",
        "idealHumidity": "40 ~ 70%",
        "idealTempRange": "16~20℃",
        "lightInfo": "중간 광도(800~1,500 Lux),높은 광도(1,500~10,000 Lux)",
        "manageLevel": "경험자",
        "originInfo": "아시아, 아메리카,캐나다",
        "waterCycleSpring": "토양 표면이 말랐을때 충분히 관수함",
        "waterCycleSummer": "토양 표면이 말랐을때 충분히 관수함",
        "waterCycleAutumn": "토양 표면이 말랐을때 충분히 관수함",
        "waterCycleWinter": "화분 흙 대부분 말랐을때 충분히 관수함",
    }
