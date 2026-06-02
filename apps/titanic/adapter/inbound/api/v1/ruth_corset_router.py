from fastapi import APIRouter

ruth_corset_router = APIRouter(prefix="/ruth", tags=["ruth"])

@ruth_corset_router.get("/corset")
async def get_ruth_corset():
    return {"message": "Hello, World!"}
