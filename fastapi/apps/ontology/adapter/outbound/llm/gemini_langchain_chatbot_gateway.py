from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from ontology.app.ports.output.langchain_chatbot_gateway import LangchainChatbotGateway
from core.matrix.secret_manager import secret_manager

_CHAT_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "당신은 LangChain으로 구현된 친절한 한국어 AI 어시스턴트입니다. "
                   "간결하고 정확하게 답변하세요."),
        ("human", "{message}"),
    ]
)


class GeminiLangchainChatbotGateway(LangchainChatbotGateway):
    """LangChain + Gemini로 일상 대화(semantic routing의 gemini 버킷)에 응답하는 어댑터."""

    def __init__(self) -> None:
        api_key = secret_manager.get_secret("GEMINI_API_KEY")
        llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=api_key, temperature=0.7)
        self._chain = _CHAT_PROMPT | llm | StrOutputParser()

    async def chat(self, message: str) -> str:
        return await self._chain.ainvoke({"message": message})
