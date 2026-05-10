"""
config/settings.py
Application configuration settings.
"""

import os

# ── PostgreSQL ──────────────────────────────────────────────────────────────
DB_HOST     = os.getenv("DB_HOST",     "127.0.0.1")
DB_PORT     = os.getenv("DB_PORT",     "5432")
DB_NAME     = os.getenv("DB_NAME",     "ecommerce_support")
DB_USER     = os.getenv("DB_USER",     "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "rizwan123")

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ── Ollama ───────────────────────────────────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL",    "gemma:2b")
OLLAMA_TIMEOUT  = int(os.getenv("OLLAMA_TIMEOUT", "120"))

# ── App ──────────────────────────────────────────────────────────────────────
APP_TITLE       = "AI E-Commerce Assistant"
APP_SUBTITLE    = "আপনার স্মার্ট কেনাকাটার সহায়ক"  # "Your smart shopping assistant"
MAX_HISTORY     = int(os.getenv("MAX_HISTORY", "50"))   # messages shown in UI

# ── Business context injected into every system prompt ──────────────────────
STORE_CONTEXT = """
আপনি একটি বাংলাদেশী ই-কমার্স স্টোরের AI সহায়ক।
আপনার নাম "শপ মিত্র"।

স্টোর সম্পর্কে তথ্য:
- নাম: ShopMitra BD
- ক্যাটাগরি: ইলেকট্রনিক্স, ফ্যাশন, গৃহস্থালি পণ্য
- ডেলিভারি: ঢাকায় ১-২ দিন, সারা বাংলাদেশে ৩-৫ দিন
- পেমেন্ট: bKash, Nagad, ক্যাশ অন ডেলিভারি, ক্রেডিট/ডেবিট কার্ড
- রিটার্ন পলিসি: ৭ দিনের মধ্যে রিটার্ন গ্রহণযোগ্য

নির্দেশিকা:
- বাংলা এবং ইংরেজি উভয় ভাষায় উত্তর দিন (ব্যবহারকারী যে ভাষায় জিজ্ঞেস করেন)
- বিনয়ী, সহায়ক এবং পেশাদার থাকুন
- পণ্যের মূল্য, উপলব্ধতা, এবং ডেলিভারি সম্পর্কে সঠিক তথ্য প্রদান করুন
- অর্ডার ট্র্যাকিং, রিটার্ন, এবং রিফান্ড সম্পর্কে সহায়তা করুন
""".strip()
