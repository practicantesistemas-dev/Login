from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Backend CRM Mercadeo"
    api_prefix: str = "/api"

    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://160.2.1.80:3000",
        "http://160.2.1.80:5175",
    ]

    scse_db_user: str = ""
    scse_db_passwd: str = ""
    scse_db_ip: str = "localhost"
    scse_db_port: int = 1521
    scse_db_database: str = ""

    @property
    def database_url(self) -> str:
        return (
            f"oracle+oracledb://{self.scse_db_user}:{self.scse_db_passwd}"
            f"@{self.scse_db_ip}:{self.scse_db_port}/?service_name={self.scse_db_database}"
        )


settings = Settings()
