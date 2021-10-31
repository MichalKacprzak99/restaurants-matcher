from fastapi import APIRouter

from app.routes.person import router as person_router
from app.routes.friendship import router as friendship_router
from app.routes.cuisine import router as cuisine_router

router = APIRouter()

router.include_router(router=cuisine_router)
router.include_router(router=friendship_router)
router.include_router(router=person_router)
