from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_configuration
from app.db.driver import Driver
from app.routes import router

configuration = get_configuration()

app = FastAPI(title=configuration.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=configuration.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event('shutdown')
async def clear_config_caches():
    get_configuration.cache_clear()
    Driver.close()


app.include_router(router, prefix=configuration.API_PREFIX)


@app.get("/")
def test():
    return {"status": "test"}
