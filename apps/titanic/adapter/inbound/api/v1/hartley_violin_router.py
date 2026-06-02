from fastapi import APIRouter

hartley_violin_router = APIRouter(prefix="/hartley", tags=["hartley"])

@hartley_violin_router.get("/violin")
async def get_hartley_violin():
    return {"message": "Hello, World!"}
    
    
    