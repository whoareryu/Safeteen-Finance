from pydantic import BaseModel, Field


class ImageGenerateRequest(BaseModel):

    prompt: str = Field(..., min_length=1, description="생성할 이미지를 설명하는 텍스트 프롬프트")
    negative_prompt: str | None = Field(None, description="제외하고 싶은 요소")
    num_inference_steps: int = Field(1, ge=1, le=8, description="생성 스텝 수 (Turbo: 1~4)")
    guidance_scale: float = Field(0.0, ge=0.0, le=15.0, description="프롬프트 반영 강도 (Turbo 권장: 0)")


class ImageGenerateResponse(BaseModel):

    image_url: str = Field(..., description="생성된 이미지 URL")
    seed: int = Field(..., description="재현을 위한 시드값")
    steps: int = Field(..., description="사용된 생성 스텝 수")
    model: str = Field(..., description="생성에 사용된 모델 식별자")
