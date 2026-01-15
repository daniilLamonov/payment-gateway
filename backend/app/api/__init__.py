from fastapi import APIRouter
from .endpoints.admin import router as admin_router
from .endpoints.auth import router as auth_router
from .endpoints.payment import router as payment_router


router = APIRouter()
router.include_router(admin_router)
router.include_router(auth_router)
router.include_router(payment_router)
