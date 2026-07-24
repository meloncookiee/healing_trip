from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL
from models import Base

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

_TEMPLE_EXTRA_COLUMNS = {
    "image_url": "VARCHAR(1000)",
    "food": "TEXT",
    "environment": "TEXT",
    "specialty": "TEXT",
    "strengths": "TEXT",
    "program_intro": "TEXT",
    "youtube_url": "VARCHAR(1000)",
    "instagram_url": "VARCHAR(1000)",
    "intro_text": "TEXT",
    "guide_text": "TEXT",
    "facility_text": "TEXT",
    "gallery_json": "TEXT",
    "reviews_json": "TEXT",
    "programs_json": "TEXT",
    "available_dates_json": "TEXT",
    "reservable": "INTEGER",
}


def _migrate_sqlite() -> None:
    if not DATABASE_URL.startswith("sqlite"):
        return
    inspector = inspect(engine)
    if "temples" not in inspector.get_table_names():
        return
    existing = {col["name"] for col in inspector.get_columns("temples")}
    with engine.begin() as conn:
        for name, col_type in _TEMPLE_EXTRA_COLUMNS.items():
            if name not in existing:
                conn.execute(text(f"ALTER TABLE temples ADD COLUMN {name} {col_type}"))


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _migrate_sqlite()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
