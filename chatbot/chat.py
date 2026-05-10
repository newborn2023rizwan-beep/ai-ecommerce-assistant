"""
chatbot/chat.py
Orchestrates: user input -> LLM -> database persistence -> response.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from database.db import get_recent_history, save_message
from database.models import ChatHistory
from llm.ollama_client import generate_response

logger = logging.getLogger(__name__)


@dataclass
class Message:
    role:      str
    content:   str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def from_db(cls, record: ChatHistory) -> List["Message"]:
        return [
            cls(role="user",      content=record.user_message, timestamp=record.timestamp),
            cls(role="assistant", content=record.bot_response,  timestamp=record.timestamp),
        ]


def process_message(user_message: str) -> str:
    user_message = user_message.strip()
    if not user_message:
        return "অনুগ্রহ করে একটি বার্তা লিখুন।"

    # No context injection — keeps responses clean and on-topic
    bot_response = generate_response(user_message, conversation_context="")
    save_message(user_message, bot_response)
    return bot_response


def load_chat_history() -> List[Message]:
    records  = get_recent_history()
    messages: List[Message] = []
    for rec in records:
        messages.extend(Message.from_db(rec))
    return messages


def clear_history() -> bool:
    from database.db import delete_all_history
    return delete_all_history()
