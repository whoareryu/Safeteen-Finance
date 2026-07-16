import sys
from contextlib import asynccontextmanager
from pathlib import Path

_backend_root = Path(__file__).resolve().parent
_apps_root = _backend_root / "apps"
for _path in (_backend_root, _apps_root):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

import logging

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

load_dotenv(_backend_root / ".env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from core.db_health_adapter import DbHealthAdapter
from core.database import dispose_engine, get_db, init_db, init_engine
from core.lol.t1_mid_faker_orchestrator import T1MidFakerOrchestrator

try:
    from doro.app.doro_director import DoroDirector
except ImportError:
    DoroDirector = None  # type: ignore[misc, assignment]

try:
    from titanic.app.james_controller import JamesController
except ImportError:
    JamesController = None  # type: ignore[misc, assignment]

_faker = T1MidFakerOrchestrator()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="사용자 메시지")


class ChatResponse(BaseModel):
    reply: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_engine()
        await init_db()
    except Exception:
        logger.exception("데이터베이스 시작 초기화 실패")
    yield
    await dispose_engine()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://whoareryu.cloud",
        "https://www.whoareryu.cloud",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from titanic.adapter.inbound.api import titanic_router  # noqa: E402
from admin.adapter.inbound.api import silicon_valley_router
from ontology.adapter.inbound.api import ontology_router
from community.adapter.inbound.api import chef_router

from ontology.adapter.inbound.api.v1.vision_router import vision_router
from plant.adapter.inbound.api import plant_router
from apps.auth.auth_endpoints import auth_router, signup_router, login_router

# ── Composition root: ChefTaskDispatcher → Maestro 주입 ──────────────────
import os

from apps.auth.owner_session import is_valid_owner_token
from community.adapter.outbound.chef_task_dispatcher import ChefTaskDispatcher
from community.dependencies.email_provider import get_email_use_case
from ontology.app.ports.output.owner_gate_port import OwnerGatePort
from ontology.app.use_cases.maestro_router_interactor import MaestroInteractor
from ontology.dependencies.maestro_router_provider import (
    register_dispatch_factory,
    get_sommelier_use_case,
    get_lens_use_case,
)


class _OwnerGateAdapter(OwnerGatePort):
    def is_owner(self, owner_session: str | None) -> bool:
        return is_valid_owner_token(owner_session)


register_dispatch_factory(
    lambda: MaestroInteractor(
        sommelier=get_sommelier_use_case(),
        lens=get_lens_use_case(),
        llm=T1MidFakerOrchestrator(),
        dispatcher=ChefTaskDispatcher(
            email=get_email_use_case(),
        ),
        owner_gate=_OwnerGateAdapter(),
    )
)

# ── Composition root: plant 전용 YOLO/이미지 저장소를 ontology 허브 어댑터로 주입 ──
from ontology.adapter.outbound.s3.s3_image_storage_gateway import S3ImageStorageGateway
from ontology.app.use_cases.yolo_interactor import YoloInteractor
from plant.adapter.outbound.resource_adapters.plant_yolo_dataset_adapter import (
    PlantYoloDatasetAdapter,
)
from plant.adapter.outbound.resource_adapters.plant_yolo_model_adapter import (
    PlantYoloModelAdapter,
)
from plant.dependencies.diagnosis_provider import (
    register_species_yolo_factory,
    register_image_storage_factory,
)

register_species_yolo_factory(
    lambda: YoloInteractor(
        dataset=PlantYoloDatasetAdapter(os.getenv("PLANT_YOLO_DATASET_PATH", "apps/plant/resources/yolo_train")),
        model=PlantYoloModelAdapter(os.getenv("PLANT_YOLO_WEIGHTS_PATH", "apps/plant/resources/plant_yolo.pt")),
    )
)
register_image_storage_factory(
    lambda: S3ImageStorageGateway(
        bucket=os.getenv("PLANT_S3_BUCKET", os.getenv("S3_BUCKET", "")),
        region=os.getenv("AWS_REGION", "ap-northeast-2"),
        prefix="plant",
    )
)
# ─────────────────────────────────────────────────────────────────────────

# ── Composition root: plant 전용 pgvector(plant_knowledge)를 ontology 시맨틱
#    라우터의 exaone_rag 지식 소스로 주입 ──────────────────────────────────
from ontology.app.ports.output.plant_knowledge_search_port import PlantKnowledgeSearchPort
from ontology.dependencies.semantic_routing_provider import register_plant_knowledge_factory
from plant.adapter.outbound.llm.plant_embedding_adapter import PlantEmbeddingAdapter
from plant.adapter.outbound.pg.plant_knowledge_pg_repository import PlantKnowledgePgRepository


class _PlantKnowledgeSearchAdapter(PlantKnowledgeSearchPort):
    def __init__(self, session: AsyncSession) -> None:
        self._repository = PlantKnowledgePgRepository(session=session)
        self._embedding = PlantEmbeddingAdapter()

    async def search(self, query: str, limit: int = 3) -> list[dict]:
        vector = await self._embedding.embed(query)
        matches = await self._repository.find_similar(vector, limit=limit)
        return [{"name": m.name, "description": m.description} for m in matches]


register_plant_knowledge_factory(lambda session: _PlantKnowledgeSearchAdapter(session))
# ─────────────────────────────────────────────────────────────────────────

app.include_router(ontology_router, prefix="/api")
app.include_router(titanic_router, prefix="/api")
app.include_router(silicon_valley_router, prefix="/api")
app.include_router(chef_router, prefix="/api")
app.include_router(vision_router, prefix="/api")
app.include_router(plant_router, prefix="/api")
app.include_router(auth_router)
app.include_router(signup_router)
app.include_router(login_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "FAST API 메인 페이지", "docs": "/docs"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    """JSON 본문 `{"message": "..."}` 를 받아 ExaOne 답변 문자열을 반환합니다."""
    try:
        reply = await _faker.chat([{"role": "user", "content": req.message}])
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"ExaOne 호출 실패: {e!s}") from e
    return ChatResponse(reply=reply)


@app.get("/db-check")
async def check_db(db: AsyncSession = Depends(get_db)):
    return await DbHealthAdapter.neon_time_check(db)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
