import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(data_dir, exist_ok=True)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/reviews.db")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Yield a SQLAlchemy Session for use in request handlers.

    Yields:
        A SQLAlchemy Session instance which will be closed when the request
        finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()