import logging
from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, Query

from apps.titanic.app.use_cases.walter_query import WalterQueryUseCase

logger = logging.getLogger(__name__)

router = APIRouter(tags=["titanic-query"])




@lru_cache
def get_walter_query_use_case() -> WalterQueryUseCase:
    return WalterQueryUseCase()


def _csv_missing(exc: FileNotFoundError) -> HTTPException:
    logger.warning("Titanic CSV 없음: %s", exc)
    return HTTPException(
        status_code=404,
        detail="Titanic CSV가 없습니다. backend/apps/titanic/app/data/Titanic-Dataset.csv 를 준비해 주세요.",
    )


@router.get("/data")
def read_titanic_data(
    use_case: WalterQueryUseCase = Depends(get_walter_query_use_case),
):
    return {"message": "CSV 조회는 비활성화되었습니다. /titanic/passengers 를 사용하세요."}


@router.get("/count")
def read_titanic_count(
    use_case: WalterQueryUseCase = Depends(get_walter_query_use_case),
):
    result = use_case.get_passenger_page(page=1, page_size=1)
    return {"count": result["total"]}


@router.get("/count/survived")
def read_titanic_count_survived(
    use_case: WalterQueryUseCase = Depends(get_walter_query_use_case),
):
    return {"message": "현재 엔드포인트는 /titanic/passengers 중심으로 동작합니다."}


@router.get("/count/dead")
def read_titanic_count_dead(
    use_case: WalterQueryUseCase = Depends(get_walter_query_use_case),
):
    return {"message": "현재 엔드포인트는 /titanic/passengers 중심으로 동작합니다."}


@router.get("/tree")
def read_titanic_tree(
    use_case: WalterQueryUseCase = Depends(get_walter_query_use_case),
):
    return {"message": "모델 조회는 별도 구현 예정입니다."}


@router.get("/model")
@router.get("/model_name")
def read_titanic_model(
    use_case: WalterQueryUseCase = Depends(get_walter_query_use_case),
):
    return {"message": "모델 조회는 별도 구현 예정입니다."}


@router.get("/accuracy")
def read_titanic_accuracy(
    use_case: WalterQueryUseCase = Depends(get_walter_query_use_case),
):
    return {"message": "모델 조회는 별도 구현 예정입니다."}


@router.get("/passengers")
def read_titanic_passengers(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=500),
    use_case: WalterQueryUseCase = Depends(get_walter_query_use_case),
):
    try:
        logger.info(
            "[Walter 경로] (1/4) Inbound adapter/inbound/api/v1/walter_router.py -> "
            "app/ports/input/walter_use_case.py | source=NeonDB table=titanic_passengers page=%d page_size=%d",
            page,
            page_size,
        )
        return use_case.get_passenger_page(page=page, page_size=page_size)
    except Exception as exc:
        logger.exception("승객 명단 조회 실패")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
