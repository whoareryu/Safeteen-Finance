from __future__ import annotations

from ontology.app.ports.input.gemini_use_case import GeminiUseCase
from ontology.app.use_cases.gemini_interacotr import GeminiInteractor


def get_gemini_use_case() -> GeminiUseCase:
    return GeminiInteractor()
