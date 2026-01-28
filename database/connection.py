from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_USER = "root"
DB_PASSWORD = "ProyectoUDE2025"
DB_HOST = "127.0.0.1"
DB_NAME = "simsw"

DATABASE_URL = (
    f"mariadb+mariadbconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=0,
    echo=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()