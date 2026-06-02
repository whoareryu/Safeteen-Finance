from fastapi import APIRouter

andrews_blueprint_router = APIRouter(prefix="/andrews", tags=["andrews"])

@andrews_blueprint_router.get("/blueprint")
async def get_andrews_blueprint():
    return {"message": "Hello, World!"}

