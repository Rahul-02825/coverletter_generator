import requests
import os

from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
print(api_key)
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

data = {
    "model": "mixtral-8x7b-instruct",  # Change this to a different model if needed
    "messages": [{"role": "system", "content": "You are a helpful AI assistant."},
                 {"role": "user", "content": "Hello, what can you do?"}]
}

response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=data, headers=headers)

print(response.json())
