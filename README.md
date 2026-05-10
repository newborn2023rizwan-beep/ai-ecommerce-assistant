# 🛒 AI E-Commerce Customer Support & Sales Assistant

> **ShopMitra BD** — Bilingual (Bengali + English) AI chatbot for Bangladeshi e-commerce businesses, powered by Ollama, PostgreSQL, and Streamlit.

---

## 📁 Project Structure

```
ai-ecommerce-assistant/
│
├── app.py                  # Streamlit entry-point
├── requirements.txt
├── README.md
│
├── chatbot/
│   └── chat.py             # Business logic: orchestrate LLM + DB
│
├── llm/
│   └── ollama_client.py    # Ollama HTTP API wrapper
│
├── database/
│   ├── db.py               # Engine, session, CRUD helpers
│   └── models.py           # SQLAlchemy ORM models
│
├── config/
│   └── settings.py         # All configuration (env-aware)
│
└── utils/
    └── helpers.py          # Logging, text utilities, quick-replies
```

---

## ⚡ Quick Start

### 1. Create the PostgreSQL database

```sql
-- Connect as superuser (e.g. psql -U postgres)
CREATE DATABASE ecommerce_support;
```

The table `chat_history` is created **automatically** on first run.

### 2. Configure environment (optional)

Copy and edit the defaults if needed:

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=ecommerce_support
export DB_USER=postgres
export DB_PASSWORD=postgres

export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=phi3
```

Or create a `.env` file and load it with `python-dotenv`.

### 3. Pull the Ollama model

```bash
ollama pull phi3
```

### 4. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the app

```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## 🗄️ PostgreSQL Schema

```sql
CREATE TABLE chat_history (
    id           SERIAL PRIMARY KEY,
    user_message TEXT        NOT NULL,
    bot_response TEXT        NOT NULL,
    timestamp    TIMESTAMP   NOT NULL DEFAULT NOW()
);
```

> This is executed automatically by SQLAlchemy on startup — you do **not** need to run it manually.

---

## 🌐 Features

| Feature | Details |
|---|---|
| **Bilingual support** | Bengali (বাংলা) + English |
| **AI responses** | Ollama `phi3` via streaming HTTP API |
| **Context-aware** | Last 5 exchanges injected as conversation context |
| **Persistent history** | Every turn stored in PostgreSQL |
| **Quick replies** | One-click common questions |
| **Clear history** | Sidebar button wipes DB + UI |
| **Status indicators** | Live DB + Ollama health checks |

---

## 🔧 Configuration Reference (`config/settings.py`)

| Variable | Default | Description |
|---|---|---|
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_NAME` | `ecommerce_support` | Database name |
| `DB_USER` | `postgres` | DB username |
| `DB_PASSWORD` | `postgres` | DB password |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `phi3` | Model to use |
| `OLLAMA_TIMEOUT` | `120` | Request timeout (seconds) |
| `MAX_HISTORY` | `50` | Messages loaded per session |

---

## 🛠️ Customising the Store Context

Edit the `STORE_CONTEXT` string in `config/settings.py` to reflect your own store name, categories, delivery zones, and policies. The entire block is injected as the system prompt on every Ollama request.

---

## 📦 Compressing into a ZIP

```bash
zip -r ai-ecommerce-assistant.zip ai-ecommerce-assistant/
```

---

## 🧱 Tech Stack

- **Frontend:** Streamlit (custom CSS, Bengali-compatible font)
- **AI:** Ollama (`phi3`) — runs 100 % locally, no API key needed
- **Database:** PostgreSQL + SQLAlchemy 2.0 ORM
- **Language:** Python 3.12

---

## 📄 License

MIT — free to use, modify, and distribute.
