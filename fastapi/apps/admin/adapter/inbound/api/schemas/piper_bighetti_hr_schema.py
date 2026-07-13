from pydantic import BaseModel, Field

class BighettiHrSchema(BaseModel):

    id: int = Field(5, description="Character ID")
    name: str = Field("넬슨 비게티", description="Character's name")
    # Pied Piper HR. 빅헤드(Big Head)라는 별명. 의도치 않게 성공하는 캐릭터.

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 5,
                "name": "Nelson Bighetti",
            }
        }
    }
