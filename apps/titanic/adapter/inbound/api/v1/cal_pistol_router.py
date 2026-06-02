from fastapi import APIRouter

cal_pistol_router = APIRouter(prefix="/cal_pistol", tags=["cal_pistol"])

@cal_pistol_router.get("/cal_pistol")
async def get_cal_pistol():
    return {"message": "Hello, World!"}

