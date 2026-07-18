from __future__ import annotations

from typing import Callable

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.database import get_db
from ontology.app.ports.output.image_storage_gateway import ImageStorageGateway

from plant.adapter.outbound.http.openweather_gateway import OpenWeatherGateway
from plant.adapter.outbound.http.pixabay_gateway import PixabayGateway
from plant.adapter.outbound.pg.photo_cache_pg_repository import PhotoCachePgRepository
from plant.adapter.outbound.pg.tutorial_pg_repository import TutorialPgRepository
from plant.app.ports.input.tutorial_use_case import TutorialUseCase
from plant.app.use_cases.tutorial_interactor import TutorialInteractor

# composition root(main.py)에서 등록 — 튜토리얼 사진 캐시 저장소(diagnosis와 별도 하위 디렉터리).
_image_storage_factory: Callable[[], ImageStorageGateway] | None = None

_pixabay = PixabayGateway()
_weather_api = OpenWeatherGateway()


def register_tutorial_image_storage_factory(factory: Callable[[], ImageStorageGateway]) -> None:
    global _image_storage_factory
    _image_storage_factory = factory


def _get_image_storage_gateway() -> ImageStorageGateway:
    if _image_storage_factory is None:
        raise RuntimeError("tutorial image storage factory가 등록되지 않았습니다 (main.py composition root 확인)")
    return _image_storage_factory()


def get_tutorial_use_case(db: AsyncSession = Depends(get_db)) -> TutorialUseCase:
    return TutorialInteractor(
        tutorial_repository=TutorialPgRepository(session=db),
        photo_cache_repository=PhotoCachePgRepository(session=db),
        pixabay=_pixabay,
        storage=_get_image_storage_gateway(),
        weather_api=_weather_api,
    )
