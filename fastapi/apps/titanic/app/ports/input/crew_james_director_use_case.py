from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.crew_james_director_dto import JamesDirectorQuery, JamesDirectorResponse


class JamesDirectorUseCase(ABC):

    @abstractmethod
    async def upload_titanic_file(self, rows: list[dict]) -> dict:
        """CSV 파싱 결과(dict 리스트)를 받아 타이타닉 데이터베이스에 저장한다."""
        pass

    @abstractmethod
    async def introduce_myself(self, schema: JamesDirectorQuery) -> JamesDirectorResponse:
        pass
