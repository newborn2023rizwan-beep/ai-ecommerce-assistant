"""
database/models.py
SQLAlchemy ORM models.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ChatHistory(Base):
    """Stores every user ↔ bot exchange."""

    __tablename__ = "chat_history"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    timestamp    = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id":           self.id,
            "user_message": self.user_message,
            "bot_response": self.bot_response,
            "timestamp":    self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def __repr__(self) -> str:
        return f"<ChatHistory id={self.id} at={self.timestamp}>"
