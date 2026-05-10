"""
rag/vector_store.py
ChromaDB vector store with sentence-transformers embeddings.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List, Dict

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

BASE_DIR   = Path(__file__).resolve().parent.parent
KB_PATH    = BASE_DIR / "data" / "knowledge_base.json"
CHROMA_DIR = BASE_DIR / "data" / "chroma_db"
EMBED_MODEL = "all-MiniLM-L6-v2"
COLLECTION  = "rizwan_fashion_v2"   # new name forces fresh index


class VectorStore:
    def __init__(self):
        self._client     = None
        self._collection = None
        self._embedder   = None
        self._ready      = False

    def initialize(self) -> bool:
        try:
            logger.info("Loading embedding model: %s", EMBED_MODEL)
            self._embedder = SentenceTransformer(EMBED_MODEL)

            CHROMA_DIR.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(
                path=str(CHROMA_DIR),
                settings=Settings(anonymized_telemetry=False),
            )
            self._collection = self._client.get_or_create_collection(
                name=COLLECTION,
                metadata={"hnsw:space": "cosine"},
            )

            if self._collection.count() == 0:
                logger.info("Building knowledge base index…")
                self._build_index()
            else:
                logger.info("Loaded existing index (%d chunks)", self._collection.count())

            self._ready = True
            return True
        except Exception as exc:
            logger.error("VectorStore init failed: %s", exc)
            return False

    def _build_index(self) -> None:
        with open(KB_PATH, encoding="utf-8") as f:
            kb = json.load(f)

        chunks: List[Dict] = []

        for p in kb.get("products", []):
            # Rich text with repeated category keywords for better retrieval
            text = (
                f"CATEGORY: {p['category'].upper()}\n"
                f"Product name: {p['name']}\n"
                f"This is a {p['category']} product.\n"
                f"Price: {p['price']} BDT (Taka)\n"
                f"Material: {p['material']}\n"
                f"Available sizes: {', '.join(p['sizes'])}\n"
                f"Available colors: {', '.join(p['colors'])}\n"
                f"Key features: {', '.join(p['features'])}\n"
                f"Best for: {p['use_case']}\n"
                f"Target customer: {p['target_customer']}\n"
                f"Product ID: {p['id']}"
            )
            chunks.append({
                "id": p["id"],
                "text": text,
                "type": "product",
                "category": p["category"]
            })

        for i, faq in enumerate(kb.get("faq", [])):
            text = f"FAQ: {faq['question']}\nAnswer: {faq['answer']}"
            chunks.append({"id": f"FAQ{i:03d}", "text": text, "type": "faq", "category": "general"})

        rules_text = (
            "Sales rules for staff:\n" +
            "\n".join(f"- {r}" for r in kb.get("sales_rules", []))
        )
        chunks.append({"id": "RULES001", "text": rules_text, "type": "rules", "category": "general"})

        store_text = (
            f"Store: {kb['shop_name']}\n"
            f"We sell: {', '.join(kb['categories'])}"
        )
        chunks.append({"id": "STORE001", "text": store_text, "type": "store", "category": "general"})

        ids        = [c["id"]       for c in chunks]
        texts      = [c["text"]     for c in chunks]
        metadatas  = [{"type": c["type"], "category": c["category"]} for c in chunks]
        embeddings = self._embedder.encode(texts, show_progress_bar=False).tolist()

        self._collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        logger.info("Indexed %d chunks.", len(chunks))

    def retrieve(self, query: str, top_k: int = 4) -> str:
        if not self._ready:
            return ""
        try:
            query_vec = self._embedder.encode([query], show_progress_bar=False).tolist()
            results   = self._collection.query(
                query_embeddings=query_vec,
                n_results=min(top_k, self._collection.count()),
                include=["documents", "metadatas", "distances"],
            )
            docs      = results.get("documents", [[]])[0]
            distances = results.get("distances",  [[]])[0]

            # Filter out low-relevance chunks (cosine distance > 0.8)
            filtered = [d for d, dist in zip(docs, distances) if dist < 0.8]
            if not filtered:
                filtered = docs[:2]  # fallback: take top 2 anyway

            return "\n\n---\n".join(filtered)
        except Exception as exc:
            logger.error("VectorStore.retrieve failed: %s", exc)
            return ""

    @property
    def ready(self) -> bool:
        return self._ready


_store = VectorStore()

def get_store()          -> VectorStore: return _store
def initialize_store()   -> bool:        return _store.initialize()
def retrieve_context(query: str, top_k: int = 4) -> str:
    return _store.retrieve(query, top_k)
