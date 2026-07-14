from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile

from plant.adapter.inbound.mappers.register_plant_mapper import entity_to_response, to_response
from plant.adapter.inbound.api.schemas.register_plant_schema import MyPlantResponse
from plant.app.dtos.register_plant_dto import RegisterPlantCommand
from plant.app.ports.input.register_plant_use_case import RegisterPlantUseCase
from plant.app.ports.output.plant_repository import PlantRepository
from plant.dependencies.register_plant_provider import (
    get_plant_repository,
    get_register_plant_use_case,
)

my_plants_router = APIRouter(prefix="/my-plants", tags=["plant-my-plants"])


@my_plants_router.post("", summary="마이플랜트 등록 (수기 입력 또는 사진으로 종 자동 인식)")
async def register_my_plant(
    region: str = Form(...),
    species_name: str | None = Form(None),
    owner_user_id: int | None = Form(None),
    file: UploadFile | None = File(None),
    use_case: RegisterPlantUseCase = Depends(get_register_plant_use_case),
) -> MyPlantResponse:
    photo_data = await file.read() if file is not None else None
    command = RegisterPlantCommand(
        owner_user_id=owner_user_id,
        region=region,
        species_name=species_name,
        photo_data=photo_data,
        photo_filename=file.filename if file is not None else None,
        photo_content_type=file.content_type if file is not None else None,
    )
    result = await use_case.register(command)
    return to_response(result)


@my_plants_router.get("", summary="내 반려식물 목록 조회")
async def list_my_plants(
    owner_user_id: int | None = None,
    repository: PlantRepository = Depends(get_plant_repository),
) -> list[MyPlantResponse]:
    entities = await repository.list_by_owner(owner_user_id)
    return [entity_to_response(entity) for entity in entities]


@my_plants_router.get("/{plant_id}", summary="마이플랜트 상세 조회")
async def get_my_plant(
    plant_id: int,
    repository: PlantRepository = Depends(get_plant_repository),
) -> MyPlantResponse:
    entity = await repository.get(plant_id)
    return entity_to_response(entity)
