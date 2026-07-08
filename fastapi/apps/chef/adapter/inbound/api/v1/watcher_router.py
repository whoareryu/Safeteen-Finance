from fastapi import APIRouter, Depends

from chef.adapter.inbound.api.schemas.watcher_schema import ClassifyRequest, ClassifyResponse
from chef.app.dtos.watcher_dto import ClassifyCommand, WatcherQuery
from chef.app.ports.input.watcher_use_case import WatcherUseCase
from chef.dependencies.watcher_provider import get_watcher_use_case

watcher_router = APIRouter(prefix="/watcher", tags=["chef-watcher"])


@watcher_router.get("/myself")
async def introduce_myself(
    use_case: WatcherUseCase = Depends(get_watcher_use_case),
) -> dict:
    result = await use_case.introduce_myself(WatcherQuery(id=1, name="Chef Watcher"))
    return {"id": result.id, "name": result.name}


@watcher_router.post("/classify", response_model=ClassifyResponse)
async def classify_text(
    body: ClassifyRequest,
    use_case: WatcherUseCase = Depends(get_watcher_use_case),
) -> ClassifyResponse:
    result = await use_case.classify(ClassifyCommand(text=body.text))
    return ClassifyResponse(
        violates=result.violates,
        score=result.score,
        matched=result.matched,
        categories=result.categories,
        tokens=result.tokens,
    )
