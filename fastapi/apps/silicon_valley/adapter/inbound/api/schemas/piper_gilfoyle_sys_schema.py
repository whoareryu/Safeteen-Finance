from pydantic import BaseModel, Field

class GilfoyleSysSchema(BaseModel):

    id: int = Field(2, description="Character ID")
    name: str = Field("버트람 길포일", description="Character's name")
    # Pied Piper 시스템 아키텍트. 사탄주의자이자 서버·보안 전문가.

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 2,
                "name": "Bertram Gilfoyle",
            }
        }
    }
