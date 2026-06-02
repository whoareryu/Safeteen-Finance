from fastapi import APIRouter

isidor_bed_router = APIRouter(prefix="/isidor", tags=["isidor"])

@isidor_bed_router.get("/bed")
async def get_isidor_bed():
    return {"message": "Hello, World!"}
    
    

