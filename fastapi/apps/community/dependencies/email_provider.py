from __future__ import annotations

from core.infra.secret_manager import secret_manager
from community.adapter.outbound.llm.exaone_adapter import ExaoneAdapter
from community.adapter.outbound.smtp.smtp_email_gateway import SmtpEmailGateway
from community.app.use_cases.email_interactor import EmailInteractor
from ontology.dependencies.maestro_router_provider import get_maestro_use_case

# n8n 웹훅 경유는 n8n 인스턴스 상태(계정·워크플로우)에 종속적이라 불안정했다.
# 변수명은 n8n 도입 당시 그대로지만 실제 값은 Gmail SMTP 계정/앱 비밀번호라
# SmtpEmailGateway에 그대로 재사용한다.
_SMTP_USER = secret_manager.get_secret("N8N_EMAIL", "")
_SMTP_PASSWORD = secret_manager.get_secret("N8N_SMTP_PASSWORD", "")
_LLM = ExaoneAdapter(model="exaone3.5:2.4b")


def get_email_use_case() -> EmailInteractor:
    return EmailInteractor(
        llm=_LLM,
        gateway=SmtpEmailGateway(smtp_user=_SMTP_USER, smtp_password=_SMTP_PASSWORD),
        maestro=get_maestro_use_case(),
    )
