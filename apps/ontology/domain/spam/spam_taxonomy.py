from dataclasses import dataclass

from ontology.domain.spam.spam_category import SpamCategory


@dataclass(frozen=True)
class TaxonomyNode:
    category: SpamCategory
    parent: SpamCategory | None
    label: str
    description: str


TAXONOMY: dict[SpamCategory, TaxonomyNode] = {
    SpamCategory.HAM: TaxonomyNode(
        SpamCategory.HAM, None, "정상 메일",
        "스팸이 아닌 정상 이메일",
    ),
    SpamCategory.PHISHING: TaxonomyNode(
        SpamCategory.PHISHING, None, "피싱",
        "계정·개인정보 탈취를 목적으로 한 사기 이메일",
    ),
    SpamCategory.ADVERTISING: TaxonomyNode(
        SpamCategory.ADVERTISING, None, "광고",
        "상품·서비스 홍보 목적의 이메일",
    ),
    SpamCategory.FINANCIAL: TaxonomyNode(
        SpamCategory.FINANCIAL, None, "금융사기",
        "투자·대출 사기를 목적으로 한 이메일",
    ),
    SpamCategory.SCAM: TaxonomyNode(
        SpamCategory.SCAM, None, "사기",
        "당첨·경품 등 허위 혜택을 빌미로 한 이메일",
    ),
    SpamCategory.ADULT: TaxonomyNode(
        SpamCategory.ADULT, None, "성인",
        "성인 콘텐츠·만남 광고 이메일",
    ),
    SpamCategory.MALWARE: TaxonomyNode(
        SpamCategory.MALWARE, None, "악성코드",
        "첨부파일·링크 클릭 유도로 악성코드를 배포하는 이메일",
    ),
}
