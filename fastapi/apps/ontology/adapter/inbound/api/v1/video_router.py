import asyncio

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from ontology.adapter.inbound.api.schemas.video_classification_schema import VideoClassifyResponse
from ontology.app.dtos.video_classification_dto import VideoClassifyCommand
from ontology.app.ports.input.video_classification_use_case import VideoClassificationUseCase
from ontology.dependencies.video_classification_provider import get_video_classification_use_case

_MAX_VIDEO_BYTES = 100 * 1024 * 1024
_ALLOWED_VIDEO_CONTENT_TYPES = {"video/mp4", "video/quicktime", "video/x-msvideo"}

video_router = APIRouter(prefix="/video", tags=["video"])


@video_router.post(
    "/classify",
    response_model=VideoClassifyResponse,
    responses={400: {"description": "지원하지 않는 포맷"}, 413: {"description": "파일 크기 초과"}},
    summary="VideoMAE로 동영상 행동 분류 (전체 분류 + 슬라이딩 윈도우 구간 분류)",
)
async def classify_video(
    file: UploadFile = File(...),
    use_case: VideoClassificationUseCase = Depends(get_video_classification_use_case),
) -> VideoClassifyResponse:
    if file.content_type not in _ALLOWED_VIDEO_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail=f"지원하지 않는 Content-Type입니다: {file.content_type}")

    content = await file.read()
    if len(content) > _MAX_VIDEO_BYTES:
        raise HTTPException(status_code=413, detail="파일 크기가 100MB를 초과했습니다.")

    try:
        result = await asyncio.to_thread(
            use_case.classify,
            VideoClassifyCommand(video=content, filename=file.filename or "video.mp4"),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return VideoClassifyResponse(
        action_label=result.action_label,
        confidence=result.confidence,
        top_k_labels=[{"label": l.label, "score": l.score} for l in result.top_k_labels],
        clip_segments=[
            {
                "start_sec": s.start_sec,
                "end_sec": s.end_sec,
                "label": s.label,
                "confidence": s.confidence,
            }
            for s in result.clip_segments
        ],
    )
