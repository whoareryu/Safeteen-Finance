from __future__ import annotations

from safeteen.app.dtos.emergency_dto import (
    EmergencyGuideResult,
    EmergencyHotlineResult,
    EmergencyStepResult,
)
from safeteen.app.ports.output.emergency_guide_repository import EmergencyGuideRepository

_ACCOUNT_FREEZE_STEPS = [
    EmergencyStepResult(
        order=1,
        title="지급정지 신청",
        description="피해 계좌로 입금한 금융회사 콜센터(또는 앱)에 즉시 전화해 지급정지를 신청한다.",
    ),
    EmergencyStepResult(
        order=2,
        title="피해 사실 신고",
        description="112 또는 사이버범죄 신고시스템(ECRM)에 신고하고 사건사고사실확인원을 발급받는다.",
    ),
    EmergencyStepResult(
        order=3,
        title="확인원 제출",
        description="발급받은 사건사고사실확인원을 계좌 개설 금융회사에 제출해 지급정지를 연장·확정한다.",
    ),
]

_POLICE_REPORT_STEPS = [
    EmergencyStepResult(
        order=1,
        title="112 또는 사이버수사대 신고",
        description="가까운 경찰서 방문 또는 112, 사이버범죄 신고시스템(ECRM)으로 신고한다.",
    ),
    EmergencyStepResult(
        order=2,
        title="증거자료 확보",
        description="대화 캡처, 계좌번호, 통화 녹음, 송금 내역 등 관련 증거를 미리 정리해 둔다.",
    ),
    EmergencyStepResult(
        order=3,
        title="고소장·진술 접수",
        description="경찰서 방문 또는 온라인으로 고소장을 접수하고 담당 수사관 배정을 확인한다.",
    ),
]

_HOTLINES = [
    EmergencyHotlineResult(name="경찰청 사이버수사국", phone_number="182", description="사이버 사기·금융범죄 신고"),
    EmergencyHotlineResult(name="금융감독원", phone_number="1332", description="불법 사금융·보이스피싱 상담"),
    EmergencyHotlineResult(name="청소년 사이버 상담센터", phone_number="1388", description="청소년 대상 피해 상담"),
]


class StaticEmergencyGuideRepository(EmergencyGuideRepository):
    """Outbound 어댑터 — 정적 Mock 대응 가이드 (추후 상황별 맞춤 가이드로 확장 가능)."""

    def get_guide(self) -> EmergencyGuideResult:
        return EmergencyGuideResult(
            account_freeze_steps=list(_ACCOUNT_FREEZE_STEPS),
            police_report_steps=list(_POLICE_REPORT_STEPS),
            hotlines=list(_HOTLINES),
        )
