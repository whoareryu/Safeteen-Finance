import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from apps.database import DATABASE_INIT_ERROR, get_sync_db
from apps.matrix.app.keymaker import MissingGeminiKeyError, keymaker
from apps.titanic.app.controllers.james_controller import JamesController
from apps.titanic.app.services.titanic_chat_service import (
    augment_user_message_with_context,
    build_titanic_chat_context,
)
from apps.titanic.app.services.titanic_import_service import import_titanic_csv_to_db
from apps.titanic.app.schemas.titanic_schemas import ChatMessage, ChatRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/titanic", tags=["titanic"])


@router.post("/chat")
def titanic_chat(body: ChatRequest, db: Session = Depends(get_sync_db)):
    """타이타닉 CSV·(추후) ``titanic_passengers`` 테이블 컨텍스트로 Gemini 응답."""
    if body.messages[-1].role != "user":
        raise HTTPException(
            status_code=422,
            detail="messages의 마지막 요소는 role=user 여야 합니다.",
        )
    try:
        gemini = keymaker.generative_model(body.model)
        model_used = keymaker.resolve_model_name(body.model or keymaker.gemini_model_name)
    except MissingGeminiKeyError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e

    context = build_titanic_chat_context(db)
    msgs = list(body.messages)
    last = msgs[-1]
    msgs[-1] = ChatMessage(
        role="user",
        content=augment_user_message_with_context(last.content, context),
    )
    
    # 순환 참조 방지를 위해 로컬 임포트
    from apps.main import _messages_to_gemini_contents, _gemini_error_detail
    
    contents = _messages_to_gemini_contents(msgs)
    try:
        response = gemini.generate_content(contents)
    except Exception as e:
        logger.exception("Titanic Gemini generate_content 실패")
        status, detail = _gemini_error_detail(e)
        raise HTTPException(status_code=status, detail=detail) from e

    text = (getattr(response, "text", None) or "").strip()
    if not text:
        raise HTTPException(
            status_code=502,
            detail="모델이 텍스트 응답을 반환하지 않았습니다.",
        )
    return {"text": text, "model": model_used, "context_source": "db" if "PostgreSQL" in context else "csv"}


@router.post("/upload")
def upload_titanic_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_sync_db),
):
    """Kaggle Titanic CSV → Neon ``titanic_passengers`` (기존 행 교체)."""
    if DATABASE_INIT_ERROR:
        raise HTTPException(status_code=503, detail="데이터베이스에 연결할 수 없습니다.")
    name = (file.filename or "").lower()
    if not name.endswith(".csv"):
        raise HTTPException(status_code=400, detail="CSV 파일만 업로드할 수 있습니다.")
    try:
        raw = file.file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"파일을 읽을 수 없습니다: {e}") from e
    if not raw:
        raise HTTPException(status_code=400, detail="빈 파일입니다.")
    if len(raw) > 15 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="파일이 너무 큽니다. (최대 15MB)")
    try:
        result = import_titanic_csv_to_db(db, raw)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception:
        logger.exception("[titanic] CSV 적재 실패")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="CSV를 Neon에 저장하지 못했습니다.",
        ) from None
    return {
        "ok": True,
        "message": f"{result['inserted']}건을 titanic_passengers에 저장했습니다.",
        **result,
    }


@router.get("/data")
def read_titanic_data():
    james = JamesController()
    df = james.get_data()

    return df.to_dict(orient="records")


@router.get("/count")
def read_titanic_count():
    james = JamesController()
    count = james.get_count()
    return {"count": count}


@router.get("/count_survived")
def read_titanic_count_survived():
    james = JamesController() 
    count_survived = james.get_count_survived()
    return {"count_survived": count_survived}


@router.get("/count_dead")
def read_titanic_count_dead():
    james = JamesController()
    count_dead = james.get_count_dead()
    return {"count_dead": count_dead}


@router.get("/tree")
def read_titanic_tree():
    james = JamesController()
    tree = james.has_decision_tree_model()
    return {"tree": tree}


@router.get("/model_name")
def read_titanic_model():
    james = JamesController()
    model = james.get_training_model_name()
    return {"model": model}
