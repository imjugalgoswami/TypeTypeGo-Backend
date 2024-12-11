from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

SQLALCHEMY_DB_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DB_URL,echo=False)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
