from fastapi import APIRouter

router = APIRouter(tags=["vectorMgr"])

@router.get("/items/",
            description="단일 쿼리 파라미터")
async def read_items(item_id: int):
    return {"item_id": item_id}