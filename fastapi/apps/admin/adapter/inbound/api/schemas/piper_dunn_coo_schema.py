from pydantic import BaseModel, Field

class DunnCooSchema(BaseModel):

    id: int = Field(3, description="Character ID")
    name: str = Field("재러드 던", description="Character's name")
    # Pied Piper COO. 전 Hooli 직원. 긍정적이고 헌신적인 운영 책임자.

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 3,
                "name": "Jared Dunn",
            }
        }
    }
