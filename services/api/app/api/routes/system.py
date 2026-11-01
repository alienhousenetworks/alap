from fastapi import APIRouter

router = APIRouter()


@router.get("/system")
async def system_info() -> dict[str, str]:
    return {"name": "ALAP", "api_version": "v1", "status": "foundation"}
