from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="EVIDENCERAG_", env_file=".env")

    database_url: str = "postgresql://evidencerag:evidencerag@localhost:5432/evidencerag"
    db_timeout_s: float = 2.0
