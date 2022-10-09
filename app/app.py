from typing import Any
from app import service, cache, hello_world
from fastapi_utils.tasks import repeat_every
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from app.config import get_settings


settings = get_settings()

def create_app():
    app: Any = FastAPI(
            title="Estudo Python",
            description="FastAPI com PostGreSQL e Redis com RedisJSON",
            version="1.0.0",
            openapi_url="/openapi.json",
            docs_url="/docs",
            redoc_url="/redoc",
            default_response_class=ORJSONResponse
          )

    @app.on_event('startup')
    @repeat_every(seconds=settings.repeat_event)  
    async def startup_event():
        await cache.init_cache_user()
    
    app.include_router(service.router, prefix="/v1/user", tags=["Users"])
    app.include_router(hello_world.router, prefix="/v1/helloworld ", tags=["HelloWorld"])
    #app.include_router(cache.router, prefix="/v1/cache", tags=["cache"])

    return app
