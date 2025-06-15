import requests
import os
from dotenv import load_dotenv
import json
import threading
import time

# Load environment variables from .env file
load_dotenv()

# Your Ollama API key and endpoint
api_key = os.getenv("OLLAMA_API_KEY")
api_endpoint = "http://localhost:11434/api/chat"

messages = []
persistent_goals_file = "persistent_goals.json"

# Load persistent goals from file if it exists
if os.path.exists(persistent_goals_file):
    try:
        with open(persistent_goals_file, "r") as f:
            persistent_goals = json.load(f)
    except Exception as e:
        print(f"Error loading persistent goals: {e}")
        persistent_goals = []
else:
    persistent_goals = []

user_input = None
input_event = threading.Event()

def get_input():
    global user_input
    while True:
        user_input = input("Enter your query (type 'exit' or 'quit' to stop, 'goal: <goal>' to add a persistent goal): ")
        input_event.set()
        if user_input.lower() in ['exit', 'quit']:
            break

def ponder_goals():
    if persistent_goals:
        ponder_message = "Please ponder the following persistent goals: " + ", ".join(persistent_goals)
        messages.append({"role": "user", "content": ponder_message})
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
        if response.status_code == 200:
            resp_json = response.json()
            assistant_message = resp_json.get("message", {}).get("content", "")
            print("[Pondering Goals]", assistant_message)
            messages.append({"role": "assistant", "content": assistant_message})
        else:
            print(f"Error pondering goals: {response.text}")
    else:
        print("[No persistent goals to ponder]")

input_thread = threading.Thread(target=get_input, daemon=True)
input_thread.start()

while True:
    input_event.clear()
    # Wait for input or timeout
    if input_event.wait(timeout=15):
        if user_input.lower() in ['exit', 'quit']:
            print("Exiting...")
            break
        elif user_input.lower().startswith('goal:'):
            goal = user_input[5:].strip()
            if goal:
                persistent_goals.append(goal)
                print(f"Added persistent goal: {goal}")
                # Save persistent goals to file
                try:
                    with open(persistent_goals_file, "w") as f:
                        json.dump(persistent_goals, f)
                except Exception as e:
                    print(f"Error saving persistent goals: {e}")
            else:
                print("No goal provided.")
            continue
        # Add the new user query to the messages
        messages.append({"role": "user", "content": user_input})
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
    else:
        # Timeout: ponder persistent goals
        ponder_goals()
