from fastapi import APIRouter

from app.api.v1.clients import router as clients_router


router = APIRouter(
    prefix="/api/v1",
)

router.include_router(clients_router)