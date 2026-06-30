from __future__ import annotations

import os

import httpx
from fastapi import APIRouter, Depends

from chef.adapter.inbound.api.schemas.telegram_schema import (
    TelegramHistoryItem,
    TelegramSchema,
)
from chef.app.dtos.telegram_dto import TelegramQuery
from chef.app.ports.input.telegram_use_case import TelegramUseCase
from chef.dependencies.telegram_provider import get_telegram_use_case

telegram_router = APIRouter(prefix="/telegram", tags=["chef-telegram"])

_N8N_WORKFLOW_ID = "AjAfsXhns8q6V689"


@telegram_router.get("/myself")
async def introduce_myself(
    use_case: TelegramUseCase = Depends(get_telegram_use_case),
) -> dict:
    result = await use_case.introduce_myself(TelegramQuery(id=1, name="Chef Telegram Bot"))
    return {"id": result.id, "name": result.name}


@telegram_router.get("/history", response_model=list[TelegramHistoryItem])
async def get_history() -> list[TelegramHistoryItem]:
    api_url = os.getenv("N8N_API_URL", "http://localhost:5678")
    api_key = os.getenv("N8N_API_KEY", "")

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"{api_url}/api/v1/executions",
            params={"workflowId": _N8N_WORKFLOW_ID, "includeData": "true", "limit": "100"},
            headers={"X-N8N-API-KEY": api_key},
        )
        resp.raise_for_status()

    items: list[TelegramHistoryItem] = []
    for execution in resp.json().get("data", []):
        run_data = (
            execution.get("data", {})
            .get("resultData", {})
            .get("runData", {})
        )
        webhook_runs = run_data.get("Webhook — Ontology Hub", [])
        if not webhook_runs:
            continue
        try:
            body = (
                webhook_runs[0]["data"]["main"][0][0]["json"]["body"]
            )
        except (KeyError, IndexError):
            continue
        if body.get("type") != "telegram":
            continue
        items.append(
            TelegramHistoryItem(
                text=body.get("text", ""),
                sent_at=execution.get("startedAt", ""),
            )
        )
    return items
