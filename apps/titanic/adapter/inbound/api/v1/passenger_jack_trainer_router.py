from fastapi import APIRouter
from titanic.app.dtos.passenger_jack_trainer_dto import JackTrainerResponse
from titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from titanic.dependencies.passenger_jack_trainer_provider import get_jack_trainer_use_case as get_jack_trainer_use_case
from fastapi import Depends
from titanic.adapter.inbound.api.schemas.passenger_jack_trainer_schema import JackTrainerSchema
import logging
logger = logging.getLogger(__name__)

'''
잭 도슨 (Jack Dawson)
자유로운 영혼, 예술가, 그리고 로즈를 구원하는 인물인 만큼
'그림'이나 '포커 도박'과 관련된 키워드가 잘 어울립니다.
생존 예측 모델의 핵심 인터페이스를 담당합니다.
'''

jack_train_router = APIRouter(prefix="/jack", tags=["jack"])


@jack_train_router.get("/myself")
async def introduce_myself(
    jack: JackTrainerUseCase = Depends(get_jack_trainer_use_case)
)-> JackTrainerResponse:
    return await jack.introduce_myself(
        JackTrainerSchema(
            id=9,
            name="Jack Dawson")
    )

jack_trainer_router = jack_train_router


