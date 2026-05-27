import logging
from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException

from apps.titanic.app.use_cases.titanic_query_impl import TitanicQueryUseCase

logger = logging.getLogger(__name__)

router = APIRouter(tags=["titanic-query"])




@lru_cache
def get_titanic_query_use_case() -> TitanicQueryUseCase:
    return TitanicQueryUseCase()


def _csv_missing(exc: FileNotFoundError) -> HTTPException:
    logger.warning("Titanic CSV 없음: %s", exc)
    return HTTPException(
        status_code=404,
        detail="Titanic CSV가 없습니다. backend/apps/titanic/app/data/Titanic-Dataset.csv 를 준비해 주세요.",
    )


@router.get("/data")
def read_titanic_data(
    use_case: TitanicQueryUseCase = Depends(get_titanic_query_use_case),
):
    try:
        return use_case.get_data()
    except FileNotFoundError as e:
        raise _csv_missing(e) from e


@router.get("/count")
def read_titanic_count(
    use_case: TitanicQueryUseCase = Depends(get_titanic_query_use_case),
):
    try:
        return {"count": use_case.get_count()}
    except FileNotFoundError as e:
        raise _csv_missing(e) from e


@router.get("/count/survived")
def read_titanic_count_survived(
    use_case: TitanicQueryUseCase = Depends(get_titanic_query_use_case),
):
    try:
        return {"survived": use_case.get_count_survived()}
    except FileNotFoundError as e:
        raise _csv_missing(e) from e


@router.get("/count/dead")
def read_titanic_count_dead(
    use_case: TitanicQueryUseCase = Depends(get_titanic_query_use_case),
):
    try:
        return {"dead": use_case.get_count_dead()}
    except FileNotFoundError as e:
        raise _csv_missing(e) from e


@router.get("/tree")
def read_titanic_tree(
    use_case: TitanicQueryUseCase = Depends(get_titanic_query_use_case),
):
    return {"has_decision_tree_model": use_case.has_decision_tree_model()}


@router.get("/model")
@router.get("/model_name")
def read_titanic_model(
    use_case: TitanicQueryUseCase = Depends(get_titanic_query_use_case),
):
    return {"model_name": use_case.get_training_model_name()}


@router.get("/accuracy")
def read_titanic_accuracy(
    use_case: TitanicQueryUseCase = Depends(get_titanic_query_use_case),
):
    try:
        return {"accuracy": use_case.get_training_model_accuracy()}
    except FileNotFoundError as e:
        raise _csv_missing(e) from e
