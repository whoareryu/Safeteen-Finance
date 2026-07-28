from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from admin.app.ports.output.pdf_summary_generator_port import PdfSummaryGeneratorPort
from core.matrix.secret_manager import secret_manager

_SUMMARY_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "당신은 업로드된 PDF 문서를 한국어로 요약하는 어시스턴트입니다. "
                   "핵심 내용을 놓치지 않으면서 간결하게 요약하세요."),
        ("human", "다음 PDF에서 추출한 텍스트를 요약해 주세요:\n\n{text}"),
    ]
)


class PdfSummaryGeneratorClient(PdfSummaryGeneratorPort):
    """LangChain + 로컬 Ollama(ChatOllama)로 PDF 텍스트를 요약하는 어댑터."""

    def __init__(self) -> None:
        base_url = secret_manager.get_secret("OLLAMA_BASE_URL", "http://localhost:11434")
        model = secret_manager.get_secret("OLLAMA_MODEL", "exaone3.5:2.4b")
        llm = ChatOllama(base_url=base_url, model=model)
        self._chain = _SUMMARY_PROMPT | llm | StrOutputParser()

    async def summarize(self, text: str) -> str:
        return await self._chain.ainvoke({"text": text})
