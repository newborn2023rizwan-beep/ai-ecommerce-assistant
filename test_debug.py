import sys
sys.path.insert(0, 'D:/Ai Engineering/PythonProject/ai-ecommerce-assistant')

print("Step 1: Testing Ollama direct call...")
import requests
try:
    r = requests.post(
        'http://localhost:11434/api/chat',
        json={
            'model': 'gemma:2b',
            'messages': [{'role': 'user', 'content': 'say hello'}],
            'stream': False
        },
        timeout=60
    )
    print("Status:", r.status_code)
    data = r.json()
    print("Response:", data['message']['content'])
except Exception as e:
    print("ERROR:", e)

print()
print("Step 2: Testing via ollama_client...")
try:
    from llm.ollama_client import generate_response
    result = generate_response('hello')
    print("Result:", repr(result))
except Exception as e:
    print("ERROR:", e)

print()
print("Step 3: Testing full pipeline...")
try:
    from chatbot.chat import process_message
    result = process_message('hello')
    print("Result:", repr(result))
except Exception as e:
    print("ERROR:", e)

print()
print("All done.")
