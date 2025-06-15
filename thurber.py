import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Your Ollama API key and endpoint
api_key = os.getenv("OLLAMA_API_KEY")
api_endpoint = "http://localhost:11434/api/generate"

# Prompt the user for a query
query = input("Enter your query: ")

# Construct the API request data
payload = {
    "prompt": query,
    "stream": False,
    "model": "llama2"
}

# Set the request headers
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

# Send the API request
response = requests.post(api_endpoint, headers=headers, json=payload)

# Check for errors
if response.status_code != 200:
    print(f"Error: {response.text}")
else:
    # Print the API response
    print(response.json()["response"])
