from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
async def live() -> dict[str, str]:
    return {"status": "alive"}


@router.get("/ready")
async def ready() -> dict[str, str]:
    # Database and Redis probes must be wired before this endpoint is used for production routing.
    return {"status": "not_configured"}
