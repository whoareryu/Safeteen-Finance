from fastapi import APIRouter, Depends

from community.adapter.inbound.api.schemas.email_schema import EmailReceiveRequest, EmailReceiveResponse
from community.app.dtos.receiver_dto import ReceiverCommand
from community.app.ports.input.receiver_use_case import ReceiverUseCase
from community.dependencies.receiver_provider import get_receiver_use_case
from community.domain.exceptions import PolicyViolationError

receiver_router = APIRouter(prefix="/email", tags=["chef-email"])


@receiver_router.post("/receive", response_model=EmailReceiveResponse)
async def receive_email(
    body: EmailReceiveRequest,
    receiver: ReceiverUseCase = Depends(get_receiver_use_case),
) -> EmailReceiveResponse:
    try:
        await receiver.save(
            ReceiverCommand(
                sender=body.sender,
                recipient=body.to,
                subject=body.subject,
                preview=body.preview,
                message_id=body.message_id,
            )
        )
    except PolicyViolationError:
        return EmailReceiveResponse(status="blocked")
    return EmailReceiveResponse(status="received")
