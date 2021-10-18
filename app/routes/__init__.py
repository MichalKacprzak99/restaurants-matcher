from fastapi import APIRouter

from .person import router as person_router
from .friendship import router as friendship_router
router = APIRouter()

router.include_router(person_router)
router.include_router(friendship_router)
