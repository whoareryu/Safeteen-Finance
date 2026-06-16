from fastapi import APIRouter
from titanic.app.dtos.crew_lowe_boat_dto import LoweBoatResponse
from titanic.app.ports.input.crew_lowe_boat_use_case import LoweBoatUseCase
import logging 
from titanic.dependencies.crew_lowe_boat_provider import get_lowe_boat_use_case
from titanic.adapter.inbound.api.schemas.crew_lowe_boat_schema import LoweBoatSchema
from fastapi import Depends
logger = logging.getLogger(__name__)


lowe_boat_router = APIRouter(prefix="/lowe", tags=["lowe"])

@lowe_boat_router.get("/myself")
async def introduce_myself(
    lowe: LoweBoatUseCase = Depends(get_lowe_boat_use_case),
) -> LoweBoatResponse:
    from titanic.adapter.inbound.api.schemas.crew_lowe_boat_schema import LoweBoatSchema
    return await lowe.introduce_myself(LoweBoatSchema())
