from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# Initilizing the database using sqlalchemy

SQLALCHEMY_DATABASE_URL = "sqlite:///./addressBook.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker( autoflush=False,bind=engine, autocommit=False )

# it is a factory function that constructs a base class for declarative class definitions.
Base = declarative_base()