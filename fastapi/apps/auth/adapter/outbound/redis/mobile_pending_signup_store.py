"""apps.auth.consent_flow(웹 플로우가 이미 쓰는 pending_signup:* Redis 저장소)를
그대로 위임한다 — 모바일 전용으로 새로 만들지 않는다. 신규가입 대기 상태는
플랫폼 분리 대상이 아니다(§3의 분리 대상은 세션·토큰이지 이 단계가 아니다)."""
from __future__ import annotations

from apps.auth import consent_flow
from apps.auth.app.dtos.mobile_auth_dto import PendingSignup
from apps.auth.app.ports.output.mobile_pending_signup_port import PendingSignupPort


class MobilePendingSignupStore(PendingSignupPort):

    async def create(self, *, provider: str, sub: str, email: str, name: str) -> str:
        return await consent_flow.create_pending_signup(provider=provider, sub=sub, email=email, name=name)

    async def pop(self, consent_token: str) -> PendingSignup | None:
        data = await consent_flow.pop_pending_signup(consent_token)
        if data is None:
            return None
        return PendingSignup(provider=data["provider"], sub=data["sub"], email=data["email"], name=data["name"])
