from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    db_user: str
    db_password: str
    db_url: str
    db_name: str = "mercury-ai"

settings = Settings()
