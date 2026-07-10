import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DB_USER = os.getenv("SCSE_DB_USER")
DB_PASSWORD = os.getenv("SCSE_DB_PASSWD")
DB_HOST = os.getenv("SCSE_DB_IP", "localhost")
DB_PORT = os.getenv("SCSE_DB_PORT", "1521")
DB_SERVICE_NAME = os.getenv("SCSE_DB_DATABASE")

DATABASE_URL = (
    f"oracle+oracledb://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}"
    f"/?service_name={DB_SERVICE_NAME}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
