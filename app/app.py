from typing import Any
from app import service, cache, hello_world
from fastapi_utils.tasks import repeat_every
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from app.config import get_settings
from app.database import engine as async_engine

from pyctuator.pyctuator import Pyctuator
from pyctuator.health.db_health_provider import DbHealthProvider
from pyctuator.health.redis_health_provider import RedisHealthProvider

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor, Span
from prometheus_fastapi_instrumentator import Instrumentator
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor

from sqlalchemy import create_engine


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

    pyctuator = Pyctuator(
        app,
        app.title,
        app_url=settings.app_url,
        pyctuator_endpoint_url=settings.pyctuator_endpoint_url,
        registration_url=settings.registration_url,
        app_description=app.description,
        additional_app_info=dict(serviceLinks=dict(metrics=settings.metrics))
    )

    # Provide app's build info
    pyctuator.set_build_info(
        name=app.title,
        version=app.version,
    )

    sync_engine = create_engine(settings.db_check)
    pyctuator.register_health_provider(DbHealthProvider(sync_engine))
    pyctuator.register_health_provider(RedisHealthProvider(cache.redis))

    resource = Resource.create(attributes={"service.name": "crud-pg-redis"})
    tracer = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer)
    tracer.add_span_processor(BatchSpanProcessor(JaegerExporter(
        agent_host_name=settings.host_jaeger, agent_port=settings.port_jaeger,)))

    def server_request_hook(span: Span, scope: dict):
        if span and span.is_recording():
            span.set_attribute("request", str(scope))

    def client_request_hook(span: Span, scope: dict):
        if span and span.is_recording():
            span.set_attribute("request", str(scope))

    def client_response_hook(span: Span, message: dict):
        if span and span.is_recording():
            span.set_attribute("response", str(message))

    FastAPIInstrumentor.instrument_app(
        app, tracer_provider=tracer, 
        excluded_urls="pyctuator/.*,metrics,/pyctuator", 
        client_request_hook=client_request_hook, 
        client_response_hook=client_response_hook, 
        server_request_hook=server_request_hook)
    SQLAlchemyInstrumentor().instrument(engine=async_engine.sync_engine)
    RedisInstrumentor().instrument(tracer_provider=tracer)
    Instrumentator().instrument(app).expose(app)

    app.include_router(service.router, prefix="/v1/user", tags=["Users"])
    app.include_router(hello_world.router,
                       prefix="/v1/helloworld ", tags=["HelloWorld"])
    #app.include_router(cache.router, prefix="/v1/cache", tags=["cache"])

    return app
