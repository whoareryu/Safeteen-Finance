from fastapi import APIRouter

from chef.adapter.inbound.api.schemas.email_schema import EmailReceiveRequest, EmailReceiveResponse

receiver_router = APIRouter(prefix="/email", tags=["chef-email"])


@receiver_router.post("/receive", response_model=EmailReceiveResponse)
async def receive_email(body: EmailReceiveRequest) -> EmailReceiveResponse:
    print(f"[Gmail] from={body.sender} subject={body.subject}")
    return EmailReceiveResponse()
