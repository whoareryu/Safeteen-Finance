from fastapi import APIRouter, Depends

from ontology.adapter.inbound.api.schemas.image_generation_schema import (
    ImageGenerateRequest,
    ImageGenerateResponse,
)
from ontology.app.dtos.image_generation_dto import ImageGenerateCommand
from ontology.app.ports.input.image_generation_use_case import ImageGenerationUseCase
from ontology.dependencies.image_generation_provider import get_image_generation_use_case

generation_router = APIRouter(prefix="/generation", tags=["generation"])


@generation_router.post(
    "/generate",
    response_model=ImageGenerateResponse,
    summary="SDXL Turbo로 텍스트 프롬프트에서 이미지 생성",
)
async def generate_image(
    body: ImageGenerateRequest,
    use_case: ImageGenerationUseCase = Depends(get_image_generation_use_case),
) -> ImageGenerateResponse:
    result = await use_case.generate(
        ImageGenerateCommand(
            prompt=body.prompt,
            negative_prompt=body.negative_prompt,
            num_inference_steps=body.num_inference_steps,
            guidance_scale=body.guidance_scale,
        )
    )
    return ImageGenerateResponse(
        image_url=result.image_url,
        seed=result.seed,
        steps=result.steps,
        model=result.model,
    )
