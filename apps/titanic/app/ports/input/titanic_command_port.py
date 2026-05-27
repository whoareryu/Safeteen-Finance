from typing import Protocol

from sqlalchemy.orm import Session

from apps.titanic.app.use_cases.titanic_schemas import ChatRequest


class TitanicCommandPort(Protocol):
    def chat(self, body: ChatRequest, db: Session) -> dict: ...
