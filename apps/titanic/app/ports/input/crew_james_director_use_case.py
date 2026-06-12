from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from titanic.app.dtos.crew_james_director_dto import JamesDirectorResponse

if TYPE_CHECKING:
    from titanic.adapter.inbound.api.schemas.crew_james_director_schema import (
        FileUploadSchema,
        JamesDirectorSchema,
    )


class JamesDirectorUseCase(ABC):

    @abstractmethod
    async def upload_titanic_file(self, schema: list[FileUploadSchema]) -> dict:
        """FileUploadSchema 리스트를 받아 타이타닉 데이터베이스에 저장한다."""
        pass

    @abstractmethod
    async def introduce_myself(self, schema: JamesDirectorSchema) -> JamesDirectorResponse:
        pass
