from fastapi import APIRouter

rose_diamond_router = APIRouter(prefix="/rose", tags=["rose"])

@rose_diamond_router.get("/diamond")
async def get_rose_diamond():
    return {"message": "Hello, World!"}
