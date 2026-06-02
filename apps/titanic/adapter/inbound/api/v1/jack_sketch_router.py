from fastapi import APIRouter

jack_sketch_router = APIRouter(prefix="/jack", tags=["jack"])

@jack_sketch_router.get("/sketch")
async def get_jack_sketch():
    return {"message": "Hello, World!"}
    
    
    
    