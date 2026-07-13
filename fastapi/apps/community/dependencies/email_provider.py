from __future__ import annotations

import os

from community.adapter.outbound.llm.exaone_adapter import ExaoneAdapter
from community.adapter.outbound.n8n.n8n_email_gateway import N8nEmailGateway
from community.app.use_cases.email_interactor import EmailInteractor
from ontology.dependencies.maestro_router_provider import get_maestro_use_case

_HUB_URL = os.getenv("N8N_HUB_WEBHOOK_URL", "")
_LLM = ExaoneAdapter(model="exaone3.5:2.4b")


def get_email_use_case() -> EmailInteractor:
    return EmailInteractor(
        llm=_LLM,
        gateway=N8nEmailGateway(webhook_url=_HUB_URL),
        maestro=get_maestro_use_case(),
    )
