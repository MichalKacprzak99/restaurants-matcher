from fastapi import FastAPI

from starlette.middleware.cors import CORSMiddleware

from app.core.config import  get_settings
from app.db.driver import Driver
from app.routes import router

settings = get_settings()

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event('shutdown')
async def clear_config_caches():
    get_settings.cache_clear()
    Driver.close()


app.include_router(router, prefix=settings.API_PREFIX)
