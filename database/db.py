"""
database/db.py
Database engine, session management, and CRUD helpers.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator, List, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session, make_transient

from config.settings import DATABASE_URL, MAX_HISTORY
from database.models import Base, ChatHistory

logger = logging.getLogger(__name__)

# ── Engine & Session factory ─────────────────────────────────────────────────
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


# ── Helpers ──────────────────────────────────────────────────────────────────

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Yield a database session and ensure it is closed afterwards."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Database error: %s", exc)
        raise
    finally:
        db.close()


def init_db() -> bool:
    """Create all tables. Returns True on success, False on failure."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialised successfully.")
        return True
    except SQLAlchemyError as exc:
        logger.error("Failed to initialise database: %s", exc)
        return False


def check_connection() -> bool:
    """Ping the database. Returns True if reachable."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        return False


def _detach(db: Session, records: list) -> list:
    """
    Expunge and make_transient so records are safely usable
    after the session closes (avoids DetachedInstanceError).
    """
    for r in records:
        _ = r.id, r.user_message, r.bot_response, r.timestamp
        db.expunge(r)
        make_transient(r)
    return records


# ── CRUD ─────────────────────────────────────────────────────────────────────

def save_message(user_message: str, bot_response: str) -> Optional[ChatHistory]:
    """Persist one conversation turn."""
    try:
        with get_db() as db:
            record = ChatHistory(
                user_message=user_message,
                bot_response=bot_response,
            )
            db.add(record)
            db.flush()
            _ = record.id, record.user_message, record.bot_response, record.timestamp
            db.expunge(record)
            make_transient(record)
            logger.debug("Saved chat record id=%s", record.id)
            return record
    except SQLAlchemyError as exc:
        logger.error("save_message failed: %s", exc)
        return None


def get_recent_history(limit: int = MAX_HISTORY) -> List[ChatHistory]:
    """Fetch the most recent *limit* turns, oldest-first."""
    try:
        with get_db() as db:
            records = (
                db.query(ChatHistory)
                .order_by(ChatHistory.timestamp.desc())
                .limit(limit)
                .all()
            )
            _detach(db, records)
            return list(reversed(records))
    except SQLAlchemyError as exc:
        logger.error("get_recent_history failed: %s", exc)
        return []


def get_all_history() -> List[ChatHistory]:
    """Return the full conversation history, oldest-first."""
    try:
        with get_db() as db:
            records = (
                db.query(ChatHistory)
                .order_by(ChatHistory.timestamp)
                .all()
            )
            _detach(db, records)
            return records
    except SQLAlchemyError as exc:
        logger.error("get_all_history failed: %s", exc)
        return []


def delete_all_history() -> bool:
    """Wipe the chat_history table. Returns True on success."""
    try:
        with get_db() as db:
            db.query(ChatHistory).delete()
        logger.info("Chat history cleared.")
        return True
    except SQLAlchemyError as exc:
        logger.error("delete_all_history failed: %s", exc)
        return False
