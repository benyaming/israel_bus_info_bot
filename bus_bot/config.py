from pydantic_settings import BaseSettings, SettingsConfigDict


class Env(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    TOKEN: str

    WEBAPP_HOST: str | None = None
    WEBAPP_PORT: int | None = None
    WEBHOOK_PATH: str | None = None
    WEBHOOK_URL: str | None = None

    DOCKER_MODE: bool = False

    DB_URL: str = 'localhost'
    DB_NAME: str
    DB_COLLECTION_NAME: str

    API_URL: str
    MAPBOX_TOKEN: str

    PERIOD: int = 5  # how often message updates (seconds)
    TTL: int = 5  # how long message updates (seconds)

    THROTTLE_QUANTITY: int = 30
    THROTTLE_PERIOD: int = 3

    METRICS_DSN: str | None = None
    METRICS_TABLE_NAME: str | None = None
    SENTRY_KEY: str | None = None

    MONITORING_INTERVAL: int = 30


env = Env()
