from __future__ import annotations

from dataclasses import dataclass

from ontology.domain.spam.spam_category import SpamCategory


@dataclass(frozen=True)
class SpamRuleMatch:
    category: SpamCategory
    confidence: float           # 0.0–1.0
    matched_keywords: tuple[str, ...]


_KEYWORDS: dict[SpamCategory, list[str]] = {
    SpamCategory.PHISHING: [
        "계정 확인", "비밀번호 변경", "로그인 필요", "본인 확인",
        "보안 경고", "계정이 잠겼", "클릭하여 확인", "즉시 확인",
    ],
    SpamCategory.ADVERTISING: [
        "특가", "% 할인", "무료", "이벤트", "혜택",
        "지금 구매", "한정 판매", "사은품", "쿠폰",
    ],
    SpamCategory.FINANCIAL: [
        "투자", "고수익", "원금 보장", "주식", "코인",
        "가상화폐", "대출", "급전",
    ],
    SpamCategory.SCAM: [
        "당첨", "경품", "상금", "복권", "선물 증정", "무료 증정",
    ],
    SpamCategory.ADULT: [
        "성인", "19세", "만남", "소개팅", "만남 주선",
    ],
    SpamCategory.MALWARE: [
        "첨부파일 열기", "다운로드", "설치 필요", "업데이트 필요", "클릭 후 설치",
    ],
}

_CONFIDENCE_SCALE = 0.3  # 키워드 30% 매칭 시 confidence=1.0


def match(subject: str, body: str) -> SpamRuleMatch:
    """키워드 매칭으로 스팸 분류를 시도한다. 매칭 없으면 HAM/1.0 반환."""
    text = f"{subject} {body}".lower()
    scores: dict[SpamCategory, list[str]] = {}
    for category, keywords in _KEYWORDS.items():
        hits = [kw for kw in keywords if kw.lower() in text]
        if hits:
            scores[category] = hits

    if not scores:
        return SpamRuleMatch(SpamCategory.HAM, 1.0, ())

    best = max(scores, key=lambda c: len(scores[c]) / len(_KEYWORDS[c]))
    hits = scores[best]
    confidence = min(len(hits) / max(len(_KEYWORDS[best]) * _CONFIDENCE_SCALE, 1), 1.0)
    return SpamRuleMatch(best, confidence, tuple(hits))
