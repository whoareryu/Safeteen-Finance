from fastapi import APIRouter, Depends

from chef.adapter.inbound.api.schemas.email_schema import EmailSendRequest, EmailSendResponse
from chef.app.ports.input.email_use_case import EmailUseCase
from chef.dependencies.email_provider import get_email_use_case

"""
Chef Email Agent
AI 이메일 작성 및 Gmail SMTP 전송 라우터
"""

email_router = APIRouter(prefix="/email", tags=["chef-email"])


@email_router.get("/myself")
async def introduce_myself() -> dict:
    return {"id": 0, "name": "Chef Email Agent (ExaOne 2.4b + Gmail SMTP)"}


@email_router.post("/send", response_model=EmailSendResponse)
async def send_email(
    body: EmailSendRequest,
    use_case: EmailUseCase = Depends(get_email_use_case),
) -> EmailSendResponse:
    dto = await use_case.execute(to=body.to, prompt=body.prompt)
    return EmailSendResponse(to=dto.to, subject=dto.subject, body=dto.body)
