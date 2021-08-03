from typing import Optional

from pydantic import BaseSettings, Field


class Env(BaseSettings):
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

    TOKEN: str = Field(env='TOKEN')

    WEBAPP_HOST: Optional[str] = Field(None, env='WEBAPP_HOST')
    WEBAPP_PORT: Optional[int] = Field(None, env='WEBAPP_PORT')
    WEBHOOK_PATH: Optional[str] = Field(None, env='WEBHOOK_PATH')
    WEBHOOK_URL: Optional[str] = Field(None, env='WEBHOOK_URL')

    DOCKER_MODE: bool = Field(False, env='DOCKER_MODE')

    DB_URL: str = Field('localhost', env='DB_URL')
    DB_NAME: str = Field(..., env='DB_NAME')
    DB_COLLECTION_NAME: str = Field(..., env='DB_COLLECTION_NAME')

    PERIOD: int = Field(5, env='PERIOD')  # how often message updates (seconds)
    TTL: int = Field(5, env='TTL')  # how long message updates (seconds)

    METRICS_DSN: Optional[str] = Field(None, env='METRICS_DSN')
    METRICS_TABLE_NAME: Optional[str] = Field(None, env='METRICS_TABLE_NAME')

    SENTRY_KEY: Optional[str] = Field(None, env='SENTRY_KEY')
    API_URL: str = Field(..., env='API_URL')
    MAPBOX_TOKEN: str = Field(..., env='MAPBOX_TOKEN')

    THROTTLE_QUANTITY: int = Field(30, env='THROTTLE_QUANTITY')
    THROTTLE_PERIOD: int = Field(3, env='THROTTLE_PERIOD')


env = Env()
