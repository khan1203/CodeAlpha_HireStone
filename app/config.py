from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Job Board API"
    env: str = "development"

    secret_key: str = "dev-secret-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    database_url: str = "postgresql+psycopg2://jobboard:jobboard@db:5432/jobboard"

    upload_dir: str = "/app/uploads"
    max_resume_size_mb: int = 5

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    notify_from_email: str = "no-reply@jobboard.local"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
