from __future__ import annotations

from admin.adapter.outbound.client.langchain_chat_generator_client import (
    LangchainChatGeneratorClient,
)
from admin.app.ports.input.langchain_chat_use_case import LangchainChatUseCase
from admin.app.use_cases.langchain_chat_interactor import LangchainChatInteractor


def get_langchain_chat_use_case() -> LangchainChatUseCase:
    return LangchainChatInteractor(generator=LangchainChatGeneratorClient())
