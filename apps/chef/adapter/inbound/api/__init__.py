from fastapi import APIRouter

from chef.adapter.inbound.api.v1.email_router import email_router
from chef.adapter.inbound.api.v1.telegram_router import telegram_router
from chef.adapter.inbound.api.v1.discord_router import discord_router
from chef.adapter.inbound.api.v1.address_router import address_router

chef_router = APIRouter(prefix="/chef", tags=["chef"])
chef_router.include_router(email_router)
chef_router.include_router(telegram_router)
chef_router.include_router(discord_router)
chef_router.include_router(address_router)

__all__ = ["chef_router"]
