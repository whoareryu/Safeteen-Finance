import sys
from contextlib import asynccontextmanager
from pathlib import Path

_backend_root = Path(__file__).resolve().parent
_apps_root = _backend_root / "apps"
for _path in (_backend_root, _apps_root):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

import logging

from urllib.parse import urlencode

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
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

# ── 브라우저 직접 접근 게이트: '/', '/docs', '/redoc', '/openapi.json'만 Google
#    로그인(OWNER_EMAIL)으로 막는다. /api/* 등 www 프론트엔드 호출은 대상 아님. ──
from apps.auth.browser_gate_router import GATED_PATHS, browser_gate_router  # noqa: E402
from apps.auth.owner_session import is_valid_owner_token  # noqa: E402


@app.middleware("http")
async def _google_browser_gate(request: Request, call_next):
    if request.url.path in GATED_PATHS and not is_valid_owner_token(
        request.cookies.get("wr_docs_gate")
    ):
        next_qs = urlencode({"next": request.url.path})
        return RedirectResponse(f"/auth/google/browser-login?{next_qs}")
    return await call_next(request)


from titanic.adapter.inbound.api import titanic_router  # noqa: E402
from admin.adapter.inbound.api import silicon_valley_router
from ontology.adapter.inbound.api import ontology_router
from community.adapter.inbound.api import chef_router

from ontology.adapter.inbound.api.v1.vision_router import vision_router
from ontology.adapter.inbound.api.v1.generation_router import generation_router
from ontology.adapter.inbound.api.v1.detection_router import detection_router
from ontology.adapter.inbound.api.v1.pose_router import pose_router
from ontology.adapter.inbound.api.v1.segmentation_router import segmentation_router
from ontology.adapter.inbound.api.v1.sentiment_router import sentiment_router
from ontology.adapter.inbound.api.v1.video_router import video_router
from ontology.adapter.inbound.api.v1.anomaly_router import anomaly_router
from plant.adapter.inbound.api import plant_router
from apps.auth.admin_router import admin_router
from apps.auth.auth_endpoints import auth_router
from apps.auth.consent_router import consent_router
from apps.auth.social_login_router import social_login_router

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

# ── Composition root: plant 전용 종(species) 분류기/이미지 저장소를 ontology 허브 어댑터로 주입 ──
from fastapi.staticfiles import StaticFiles

from ontology.adapter.outbound.resource_adapters.image_classifier.yolo_classifier_model_adapter import (
    YoloClassifierModelAdapter,
)
from plant.adapter.outbound.filesystem.local_image_storage_adapter import (
    LocalImageStorageAdapter,
)
from plant.adapter.outbound.resource_adapters.plant_yolo_model_adapter import (
    PlantYoloModelAdapter,
)
from plant.dependencies.diagnosis_provider import (
    register_species_classifier_factory,
    register_image_storage_factory,
)

register_species_classifier_factory(
    lambda: YoloClassifierModelAdapter(
        model_port=PlantYoloModelAdapter(
            os.getenv("PLANT_YOLO_WEIGHTS_PATH", "apps/plant/resources/plant_yolo.pt")
        )
    )
)
# PLANT_S3_BUCKET(AWS API 미발급, 보류 중)이 준비되기 전까지는 로컬 디스크에 저장한다.
# 발급 후에는 S3ImageStorageGateway(bucket=os.getenv("PLANT_S3_BUCKET", ""), ...)로 교체.
_plant_diagnosis_media_dir = _backend_root / "apps/plant/resources/diagnosis_uploads"
register_image_storage_factory(
    lambda: LocalImageStorageAdapter(
        base_dir=_plant_diagnosis_media_dir,
        public_base_url=os.getenv("BACKEND_PUBLIC_URL", "http://127.0.0.1:8000"),
        url_prefix="media/plant",
    )
)
app.mount(
    "/media/plant",
    StaticFiles(directory=str(_plant_diagnosis_media_dir), check_dir=False),
    name="plant-diagnosis-media",
)
# ─────────────────────────────────────────────────────────────────────────

# ── Composition root: 식집사 튜토리얼 Pixabay 사진 캐시 저장소(로컬 디스크) ──
from plant.dependencies.tutorial_provider import register_tutorial_image_storage_factory

_plant_tutorial_media_dir = _backend_root / "apps/plant/resources/tutorial_photos"
register_tutorial_image_storage_factory(
    lambda: LocalImageStorageAdapter(
        base_dir=_plant_tutorial_media_dir,
        public_base_url=os.getenv("BACKEND_PUBLIC_URL", "http://127.0.0.1:8000"),
        url_prefix="media/plant-tutorial",
    )
)
app.mount(
    "/media/plant-tutorial",
    StaticFiles(directory=str(_plant_tutorial_media_dir), check_dir=False),
    name="plant-tutorial-media",
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

# ── Composition root: 이미지 생성(SDXL Turbo) 결과물 정적 서빙 ────────────────
_ontology_generated_media_dir = _backend_root / "apps/ontology/resources/generated_images"
_ontology_generated_media_dir.mkdir(parents=True, exist_ok=True)
app.mount(
    "/media/generated",
    StaticFiles(directory=str(_ontology_generated_media_dir), check_dir=False),
    name="ontology-generated-media",
)
# ─────────────────────────────────────────────────────────────────────────

# ── Composition root: 시멘틱 분할(SegFormer) 오버레이 이미지 정적 서빙 ──────────
_ontology_segmentation_media_dir = _backend_root / "apps/ontology/resources/segmentation_overlays"
_ontology_segmentation_media_dir.mkdir(parents=True, exist_ok=True)
app.mount(
    "/media/segmentation",
    StaticFiles(directory=str(_ontology_segmentation_media_dir), check_dir=False),
    name="ontology-segmentation-media",
)
# ─────────────────────────────────────────────────────────────────────────

app.include_router(ontology_router, prefix="/api")
app.include_router(titanic_router, prefix="/api")
app.include_router(silicon_valley_router, prefix="/api")
app.include_router(chef_router, prefix="/api")
app.include_router(vision_router, prefix="/api")
app.include_router(generation_router, prefix="/api")
app.include_router(detection_router, prefix="/api")
app.include_router(pose_router, prefix="/api")
app.include_router(segmentation_router, prefix="/api")
app.include_router(sentiment_router, prefix="/api")
app.include_router(video_router, prefix="/api")
app.include_router(anomaly_router, prefix="/api")
app.include_router(plant_router, prefix="/api")
app.include_router(auth_router)
app.include_router(browser_gate_router)
app.include_router(social_login_router)
app.include_router(consent_router)
app.include_router(admin_router)


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
    return await DbHealthAdapter.db_time_check(db)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
