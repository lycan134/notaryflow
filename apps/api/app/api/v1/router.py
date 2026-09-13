from fastapi import APIRouter

from app.api.v1.clients import router as clients_router
from app.api.v1.document_reviews import router as document_reviews_router
from app.api.v1.documents import router as documents_router
from app.api.v1.transactions import router as transactions_router


router = APIRouter(
    prefix="/api/v1",
)

router.include_router(clients_router)
router.include_router(transactions_router)
router.include_router(documents_router)
router.include_router(document_reviews_router)
