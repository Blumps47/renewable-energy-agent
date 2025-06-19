import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv('OPENAI_API_KEY')
print(f"Key: {key}")
print(f"Length: {len(key)}")
print(f"Starts with sk-: {key.startswith('sk-')}")
print(f"First 20 chars: {key[:20]}") 