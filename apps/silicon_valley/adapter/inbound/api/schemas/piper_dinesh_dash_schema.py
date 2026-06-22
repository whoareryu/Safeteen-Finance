from pydantic import BaseModel, Field

class DineshDashSchema(BaseModel):

    id: int = Field(4, description="Character ID")
    name: str = Field("디네시 추그타이", description="Character's name")
    # Pied Piper 앱 개발자. 길포일과 끊임없이 경쟁하는 백엔드 엔지니어.

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 4,
                "name": "Dinesh Chugtai",
            }
        }
    }
