from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LINKS_DIR = DATA_DIR / "links"
USERS_FILE = DATA_DIR / "users.json"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    secret_key: str = "cambia-esta-clave-en-produccion-liga-2026"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    api_prefix: str = "/api"

    scse_db_user: str = ""
    scse_db_passwd: str = ""
    scse_db_ip: str = ""
    scse_db_port: int = 1521
    scse_db_database: str = ""

    @computed_field
    @property
    def db_enabled(self) -> bool:
        return bool(self.scse_db_user and self.scse_db_ip and self.scse_db_database)

    @computed_field
    @property
    def db_dsn(self) -> str:
        return f"{self.scse_db_ip}:{self.scse_db_port}/{self.scse_db_database}"


settings = Settings()
