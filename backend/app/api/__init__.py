from fastapi import APIRouter
from .endpoints.admin import router as admin_router
from .endpoints.utils import router as utils_router


router = APIRouter()
router.include_router(admin_router)
router.include_router(utils_router)