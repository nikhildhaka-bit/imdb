from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "sqlite:///./marquee.db"
    jwt_secret: str
    tmdb_read_access_token: str

    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 30
    tmdb_stale_after_days: int = 30

    # Local dev runs over plain http — the Secure cookie attribute is only sent over TLS,
    # so it must be off here and switched on once the app is served over https.
    cookie_secure: bool = False

    log_level: str = "INFO"


settings = Settings()
