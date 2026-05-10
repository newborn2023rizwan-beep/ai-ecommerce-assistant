import requests

print("Sending message to Ollama...")
try:
    r = requests.post(
        'http://localhost:11434/api/chat',
        json={
            'model': 'gemma:2b',
            'messages': [
                {'role': 'system', 'content': 'You are a helpful fashion store assistant.'},
                {'role': 'user', 'content': 'hi'}
            ],
            'stream': False,
            'options': {'temperature': 0.7, 'num_predict': 400}
        },
        timeout=120
    )
    print("Status:", r.status_code)
    data = r.json()
    print("Response:", data['message']['content'][:300])
except Exception as e:
    print("ERROR:", type(e).__name__, str(e))

print()
print("Testing RAG...")
try:
    import sys
    sys.path.insert(0, '.')
    from rag.vector_store import retrieve_context
    ctx = retrieve_context('t-shirt price', top_k=2)
    print("RAG context length:", len(ctx))
    print("RAG preview:", ctx[:200])
except Exception as e:
    print("RAG ERROR:", type(e).__name__, str(e))

print()
print("All done.")
