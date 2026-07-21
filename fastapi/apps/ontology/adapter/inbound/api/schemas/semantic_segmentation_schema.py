from pydantic import BaseModel, Field


class ClassAreaSchema(BaseModel):

    label: str
    ratio: float = Field(..., description="전체 픽셀 대비 해당 클래스 면적 비율 (0~1)")


class SegmentResponse(BaseModel):

    class_areas: list[ClassAreaSchema] = Field(..., description="비율 내림차순 클래스별 면적")
    overlay_image_url: str = Field(..., description="분할 마스크가 오버레이된 시각화 이미지 URL")
