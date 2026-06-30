from enum import Enum


class SpamCategory(str, Enum):
    PHISHING = "phishing"       # 피싱
    ADVERTISING = "advertising" # 광고
    FINANCIAL = "financial"     # 금융사기
    SCAM = "scam"               # 사기
    ADULT = "adult"             # 성인
    MALWARE = "malware"         # 악성코드
    HAM = "ham"                 # 정상
