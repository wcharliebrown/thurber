import requests
import os
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

# Your Ollama API key and endpoint
api_key = os.getenv("OLLAMA_API_KEY")
api_endpoint = "http://localhost:11434/api/chat"

messages = []

while True:
    query = input("Enter your query (type 'exit' or 'quit' to stop): ")
    if query.lower() in ['exit', 'quit']:
        print("Exiting...")
        break
    # Add the new user query to the messages
    messages.append({"role": "user", "content": query})
    payload = {
        "model": "llama3",
        "messages": messages,
        "stream": False
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    response = requests.post(api_endpoint, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"Error: {response.text}")
    else:
        resp_json = response.json()
        assistant_message = resp_json.get("message", {}).get("content", "")
        print(assistant_message)
        # Add the assistant's response to the messages
        messages.append({"role": "assistant", "content": assistant_message})
