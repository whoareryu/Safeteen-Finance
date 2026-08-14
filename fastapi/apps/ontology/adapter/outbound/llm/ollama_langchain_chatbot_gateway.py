from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from ontology.app.ports.output.langchain_chatbot_gateway import LangchainChatbotGateway
from core.infra.secret_manager import secret_manager

_CHAT_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "당신은 LangChain으로 구현된 친절한 한국어 AI 어시스턴트입니다. "
                   "간결하고 정확하게 답변하세요."),
        ("human", "{message}"),
    ]
)


class OllamaLangchainChatbotGateway(LangchainChatbotGateway):
    """LangChain + 로컬 Ollama(ChatOllama)로 일상 대화(semantic routing의 gemini 버킷)에 응답하는 어댑터."""

    def __init__(self) -> None:
        base_url = secret_manager.get_secret("OLLAMA_BASE_URL", "http://localhost:11434")
        model = secret_manager.get_secret("OLLAMA_MODEL", "exaone3.5:2.4b")
        llm = ChatOllama(base_url=base_url, model=model)
        self._chain = _CHAT_PROMPT | llm | StrOutputParser()

    async def chat(self, message: str) -> str:
        return await self._chain.ainvoke({"message": message})
