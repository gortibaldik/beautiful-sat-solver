from server.config import Config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine(
  Config.DB_CONNECTION_STRING,
  pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
base = declarative_base()

class Base(base):
    __abstract__ = True
    query = None
    query_class = None