"""
app.py - Rizwan Fashion Store | RAG-Powered AI Assistant
"""
from __future__ import annotations
import logging
from datetime import datetime
import streamlit as st

st.set_page_config(
    page_title="Rizwan Fashion Store",
    page_icon="👕",
    layout="wide",
    initial_sidebar_state="expanded"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Hind+Siliguri:wght@400;500;600&display=swap');

:root {
    --primary:    #6C63FF;
    --primary-dk: #4B44CC;
    --accent:     #FF6584;
    --dark:       #0A0A0F;
    --card:       #12121A;
    --card2:      #1A1A28;
    --border:     #2A2A40;
    --text:       #E8E8F0;
    --muted:      #7070A0;
    --green:      #00D4AA;
    --yellow:     #FFB347;
    --red:        #FF6B6B;
    --user-bg:    #6C63FF22;
    --bot-bg:     #1A1A28;
    --radius:     16px;
}

* { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', 'Hind Siliguri', sans-serif !important;
    background: var(--dark) !important;
    color: var(--text) !important;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section.main > div { padding: 1.5rem 2rem 6rem 2rem !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--dark); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--card) !important;
    border-right: 1px solid var(--border) !important;
    padding: 0 !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--primary), var(--primary-dk)) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.2s !important;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px #6C63FF44 !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    background: var(--card2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}
[data-testid="stChatInput"] textarea {
    color: var(--text) !important;
    font-family: 'Inter', 'Hind Siliguri', sans-serif !important;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.25rem 0 !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--primary) !important; }

/* ── Alerts ── */
.stAlert { border-radius: 10px !important; }

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 0.75rem 0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state: st.session_state.messages = []

# ── Bootstrap ─────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="⚡ Booting AI Knowledge Base…")
def startup():
    res = {}
    try:
        from database.db import init_db, check_connection
        res["db"] = init_db() and check_connection()
    except Exception as e:
        res["db"] = False; res["db_err"] = str(e)
    try:
        from llm.ollama_client import check_ollama_health
        res["ai"] = check_ollama_health()
    except Exception as e:
        res["ai"] = False; res["ai_err"] = str(e)
    try:
        from rag.vector_store import initialize_store
        res["rag"] = initialize_store()
    except Exception as e:
        res["rag"] = False; res["rag_err"] = str(e)
    return res

boot   = startup()
db_ok  = boot.get("db",  False)
ai_ok  = boot.get("ai",  False)
rag_ok = boot.get("rag", False)

def status_dot(ok): return f"<span style='color:{'#00D4AA' if ok else '#FF6B6B'};font-size:1rem'>{'●' if ok else '●'}</span>"
def status_txt(ok, a="Active", b="Offline"): return f"<span style='color:{'#00D4AA' if ok else '#FF6B6B'};font-weight:600'>{'✓ '+a if ok else '✗ '+b}</span>"

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand header
    st.markdown("""
<div style="background:linear-gradient(135deg,#6C63FF,#FF6584);padding:1.5rem 1.2rem;margin:-1rem -1rem 0 -1rem">
    <div style="font-size:2rem;margin-bottom:0.3rem">👕</div>
    <div style="font-size:1.1rem;font-weight:800;color:#fff;letter-spacing:0.5px">Rizwan Fashion</div>
    <div style="font-size:0.75rem;color:#ffffffcc;margin-top:2px">AI Sales Assistant</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='padding:1rem 0.5rem'>", unsafe_allow_html=True)

    # System status card
    st.markdown(f"""
<div style="background:var(--card2);border:1px solid var(--border);border-radius:12px;padding:0.9rem 1rem;margin-bottom:0.75rem">
    <div style="font-size:0.7rem;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:0.6rem">System Status</div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.35rem">
        <span style="font-size:0.82rem;color:var(--text)">🗄️ Database</span>
        {status_txt(db_ok,"Connected","Error")}
    </div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.35rem">
        <span style="font-size:0.82rem;color:var(--text)">🤖 Ollama AI</span>
        {status_txt(ai_ok,"Running","Offline")}
    </div>
    <div style="display:flex;justify-content:space-between;align-items:center">
        <span style="font-size:0.82rem;color:var(--text)">🧠 Knowledge Base</span>
        {status_txt(rag_ok,"RAG Active","Offline")}
    </div>
</div>
""", unsafe_allow_html=True)

    # Products catalog card (no prices)
    st.markdown("""
<div style="background:var(--card2);border:1px solid var(--border);border-radius:12px;padding:0.9rem 1rem;margin-bottom:0.75rem">
    <div style="font-size:0.7rem;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:0.7rem">Our Products</div>
    <div style="border-bottom:1px solid var(--border);padding-bottom:0.6rem;margin-bottom:0.6rem">
        <div style="font-size:0.75rem;font-weight:600;color:#6C63FF;margin-bottom:0.3rem">👕 T-SHIRTS</div>
        <div style="font-size:0.8rem;color:var(--text);padding:0.15rem 0">• Premium Cotton Round Neck</div>
        <div style="font-size:0.8rem;color:var(--text);padding:0.15rem 0">• Oversized Streetwear</div>
    </div>
    <div>
        <div style="font-size:0.75rem;font-weight:600;color:#FF6584;margin-bottom:0.3rem">👖 PANTS</div>
        <div style="font-size:0.8rem;color:var(--text);padding:0.15rem 0">• Slim Fit Denim Jeans</div>
        <div style="font-size:0.8rem;color:var(--text);padding:0.15rem 0">• Jogger Cargo Pant</div>
    </div>
    <div style="margin-top:0.7rem;padding-top:0.6rem;border-top:1px solid var(--border);font-size:0.72rem;color:var(--muted);text-align:center">
        💬 Ask AI for prices &amp; details
    </div>
</div>
""", unsafe_allow_html=True)

    # Store policy card
    st.markdown("""
<div style="background:var(--card2);border:1px solid var(--border);border-radius:12px;padding:0.9rem 1rem;margin-bottom:0.75rem">
    <div style="font-size:0.7rem;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:0.7rem">Store Policy</div>
    <div style="font-size:0.8rem;display:flex;flex-direction:column;gap:0.35rem">
        <div>🚚 <span style="color:var(--muted)">Dhaka:</span> <span style="color:var(--text)">1-2 days • ৳60</span></div>
        <div>📦 <span style="color:var(--muted)">Nationwide:</span> <span style="color:var(--text)">2-4 days • ৳120</span></div>
        <div>💳 <span style="color:var(--muted)">Payment:</span> <span style="color:var(--text)">bKash, Nagad, COD</span></div>
        <div>🔄 <span style="color:var(--muted)">Return:</span> <span style="color:var(--text)">7 days (unused)</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

    # Stats
    msg_count = len(st.session_state.messages)
    turns     = msg_count // 2
    st.markdown(f"""
<div style="background:var(--card2);border:1px solid var(--border);border-radius:12px;padding:0.9rem 1rem;margin-bottom:0.75rem;display:flex;justify-content:space-around;text-align:center">
    <div>
        <div style="font-size:1.4rem;font-weight:800;color:var(--primary)">{turns}</div>
        <div style="font-size:0.7rem;color:var(--muted)">Conversations</div>
    </div>
    <div style="width:1px;background:var(--border)"></div>
    <div>
        <div style="font-size:1.4rem;font-weight:800;color:var(--accent)">{msg_count}</div>
        <div style="font-size:0.7rem;color:var(--muted)">Messages</div>
    </div>
    <div style="width:1px;background:var(--border)"></div>
    <div>
        <div style="font-size:1.4rem;font-weight:800;color:var(--green)">{'ON' if ai_ok else 'OFF'}</div>
        <div style="font-size:0.7rem;color:var(--muted)">AI Status</div>
    </div>
</div>
""", unsafe_allow_html=True)

    if st.button("🗑️  Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        try:
            from database.db import delete_all_history
            delete_all_history()
        except: pass
        st.rerun()

    st.markdown("<div style='font-size:0.65rem;color:var(--muted);text-align:center;padding:0.5rem 0'>Powered by Ollama · ChromaDB · PostgreSQL</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── MAIN AREA ─────────────────────────────────────────────────────────────────

# Header
st.markdown("""
<div style="background:linear-gradient(135deg,#6C63FF15,#FF658415);border:1px solid #6C63FF33;border-radius:var(--radius);padding:1.5rem 2rem;margin-bottom:1.5rem;display:flex;align-items:center;gap:1.5rem">
    <div style="background:linear-gradient(135deg,#6C63FF,#FF6584);border-radius:14px;width:56px;height:56px;display:flex;align-items:center;justify-content:center;font-size:1.8rem;flex-shrink:0">👕</div>
    <div>
        <div style="font-size:1.6rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#FF6584);-webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1.2">Rizwan Fashion Store</div>
        <div style="color:var(--muted);font-size:0.9rem;margin-top:4px">আপনার ব্যক্তিগত ফ্যাশন সহায়ক · Your personal fashion AI assistant</div>
    </div>
    <div style="margin-left:auto;display:flex;gap:0.5rem;flex-wrap:wrap">
        <span style="background:#6C63FF22;border:1px solid #6C63FF55;color:#9D97FF;border-radius:20px;padding:4px 12px;font-size:0.72rem;font-weight:600">🧠 RAG Powered</span>
        <span style="background:#00D4AA22;border:1px solid #00D4AA55;color:#00D4AA;border-radius:20px;padding:4px 12px;font-size:0.72rem;font-weight:600">⚡ gemma:2b</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Alerts
if not ai_ok:
    st.error("⚠️ Ollama is offline. Please start Ollama and refresh the page.", icon="🔴")
if not rag_ok:
    st.warning("⚠️ Knowledge Base not loaded. Install: `pip install chromadb sentence-transformers`", icon="🟡")

# Quick questions row
if ai_ok:
    st.markdown("<div style='font-size:0.78rem;font-weight:600;color:var(--muted);margin-bottom:0.5rem;text-transform:uppercase;letter-spacing:0.5px'>💡 Quick Questions</div>", unsafe_allow_html=True)
    q_cols = st.columns(4)
    quick_qs = [
        ("👕", "T-shirt গুলো কি কি?"),
        ("👖", "Pant এর দাম কত?"),
        ("📏", "Size গাইড দিন"),
        ("🚚", "Delivery কতদিনে?"),
    ]
    for col, (icon, q) in zip(q_cols, quick_qs):
        with col:
            if st.button(f"{icon} {q}", key=f"qq_{q}", use_container_width=True):
                st.session_state["_quick"] = q
                st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)

# ── Chat area ─────────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
<div style="text-align:center;padding:4rem 2rem;background:var(--card2);border:1px dashed var(--border);border-radius:var(--radius);margin:1rem 0">
    <div style="font-size:3.5rem;margin-bottom:1rem">🛍️</div>
    <div style="font-size:1.3rem;font-weight:700;color:var(--text);margin-bottom:0.5rem">Welcome to Rizwan Fashion Store!</div>
    <div style="color:var(--muted);font-size:0.95rem;max-width:400px;margin:0 auto">
        Ask me about our T-shirts, Pants, prices, sizes, or delivery.<br>
        আমাদের পণ্য সম্পর্কে যেকোনো প্রশ্ন করুন!
    </div>
</div>
""", unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="👤" if msg["role"]=="user" else "🤖"):
            st.write(msg["content"])

# ── Input ─────────────────────────────────────────────────────────────────────
user_input = st.chat_input("পণ্য সম্পর্কে জিজ্ঞেস করুন… / Ask about our products…", disabled=not ai_ok)

if "_quick" in st.session_state:
    user_input = st.session_state.pop("_quick")

if user_input:
    user_input = user_input.strip()
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user", avatar="👤"):
        st.write(user_input)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🧠 Searching knowledge base…"):
            try:
                # RAG retrieval — search with full user query for best match
                retrieved = ""
                if rag_ok:
                    from rag.vector_store import retrieve_context
                    retrieved = retrieve_context(user_input, top_k=4)
                    logger.info("RAG retrieved %d chars for: %s", len(retrieved), user_input)

                # System prompt
                system = """You are a sales assistant for Rizwan Fashion Store in Bangladesh.
RULES:
1. Always respond in English only.
2. Answer ONLY based on the PRODUCT KNOWLEDGE provided below. Do not make up information.
3. For T-shirt questions: talk about T-shirts only.
4. For Pant questions: talk about Pants only.
5. Always mention: product name, price in BDT, available sizes and colors.
6. Be friendly and concise.
Store policy: Dhaka 1-2 days (60 BDT), Nationwide 2-4 days (120 BDT), 7-day return, bKash/Nagad/COD/Card.
If no relevant product is found in the knowledge base, say so honestly."""

                if retrieved:
                    system += f"\n\n=== PRODUCT KNOWLEDGE ===\n{retrieved}\n=== END ==="

                history = st.session_state.messages[-8:]
                api_msgs = [{"role": "system", "content": system}]
                for m in history:
                    api_msgs.append({"role": m["role"], "content": m["content"]})

                import requests as req
                r = req.post(
                    "http://localhost:11434/api/chat",
                    json={"model": "gemma:2b", "messages": api_msgs, "stream": False,
                          "options": {"temperature": 0.2, "num_predict": 300, "top_p": 0.85}},
                    timeout=120
                )
                r.raise_for_status()
                bot_response = r.json()["message"]["content"]
            except Exception as e:
                bot_response = f"⚠️ দুঃখিত, সমস্যা হয়েছে: {e}"
                logger.error("Chat error: %s", e)

        st.write(bot_response)

    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    try:
        from database.db import save_message
        save_message(user_input, bot_response)
    except Exception as e:
        logger.warning("DB save: %s", e)
