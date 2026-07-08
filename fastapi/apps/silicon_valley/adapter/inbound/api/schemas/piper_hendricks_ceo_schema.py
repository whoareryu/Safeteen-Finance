from pydantic import BaseModel, Field

class HendricksCeoSchema(BaseModel):

    id: int = Field(1, description="Character ID")
    name: str = Field("리처드 헨드릭스", description="Character's name")
    # Pied Piper CEO. 중간 아웃(Middle-Out) 압축 알고리즘 발명자.

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "Richard Hendricks",
            }
        }
    }
