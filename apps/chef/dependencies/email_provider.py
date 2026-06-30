from __future__ import annotations

import os

from chef.adapter.outbound.n8n.n8n_email_gateway import N8nEmailGateway
from chef.app.chef_orchestrator import get_chef_llm
from chef.app.use_cases.email_interactor import EmailInteractor
from ontology.dependencies.maestro_router_provider import get_maestro_use_case

_HUB_URL = os.getenv("N8N_HUB_WEBHOOK_URL", "")


def get_email_use_case() -> EmailInteractor:
    return EmailInteractor(
        llm=get_chef_llm(),
        gateway=N8nEmailGateway(webhook_url=_HUB_URL),
        maestro=get_maestro_use_case(),
    )
