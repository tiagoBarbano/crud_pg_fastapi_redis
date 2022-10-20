from pydantic import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    asyncpg_url: str
    redis_host: str
    redis_port: int
    redis_password: str
    repeat_event: int
    app_url: str
    pyctuator_endpoint_url: str
    registration_url: str
    metrics: str
    db_check: str
    host_jaeger: str
    port_jaeger: int
    
    class Config:
        env_file = ".env"

       
@lru_cache()        
def get_settings():
    return Settings()
        

