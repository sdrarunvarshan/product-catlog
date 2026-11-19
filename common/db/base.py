import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

POSTGRES_URL = os.getenv(
    "POSTGRES_URL",
    "postgresql+psycopg2://postgres:postgres@db:5432/catalog"
)

engine = create_engine(POSTGRES_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
