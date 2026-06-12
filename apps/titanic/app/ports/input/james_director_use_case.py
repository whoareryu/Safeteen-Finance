from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from apps.titanic.adapter.inbound.api.schemas.crew_james_director_schema import JamesDirectorSchema
from titanic.app.dtos.james_director_dto import JamesDirectorResponse


class JamesDirectorUseCase(ABC):

    @abstractmethod
    async def upload_titanic_file(self, schema: list[JamesDirectorSchema]) -> JamesDirectorResponse:
        """JamesDirectorSchema 리스트를 받아서 타이타닉 데이터베이스에 저장한다."""
        pass

