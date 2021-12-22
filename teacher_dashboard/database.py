from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.app_config import get_config

SQLALCHEMY_DATABASE_URL = get_config().DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, pool_recycle=1800
)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
