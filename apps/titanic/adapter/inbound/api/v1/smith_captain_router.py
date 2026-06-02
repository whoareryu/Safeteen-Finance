from fastapi import APIRouter

smith_captain_router = APIRouter(prefix="/smith", tags=["smith"])

@smith_captain_router.get("/captain")
async def get_smith_captain():
    return {"message": "Hello, World!"}
