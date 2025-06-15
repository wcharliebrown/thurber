import requests
import os
from dotenv import load_dotenv
import json
import threading
import time
import re

# Load environment variables from .env file
load_dotenv()

# Your Ollama API key and endpoint
api_key = os.getenv("OLLAMA_API_KEY")
api_endpoint = "http://localhost:11434/api/chat"

messages = []
persistent_goals_file = "persistent_goals.json"

# Data structure to track progress on complex problems
current_problem_file = "current_problem.json"
current_problem = {
    "question": None,
    "steps": [],
    "current_step": 0,
    "cumulative_results": []
}
# Load current_problem from file if it exists
if os.path.exists(current_problem_file):
    try:
        with open(current_problem_file, "r") as f:
            loaded_problem = json.load(f)
            # Only load if structure matches
            if all(k in loaded_problem for k in current_problem):
                current_problem = loaded_problem
    except Exception as e:
        print(f"Error loading current problem: {e}")

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
        # New question/problem: reset current_problem
        current_problem["question"] = user_input
        current_problem["steps"] = []
        current_problem["current_step"] = 0
        current_problem["cumulative_results"] = []
        # Save current_problem to file
        try:
            with open(current_problem_file, "w") as f:
                json.dump(current_problem, f)
        except Exception as e:
            print(f"Error saving current problem: {e}")
        # Ask Ollama to break the problem into steps
        step_prompt = f"Break this problem into a set of clear, sequential steps: {user_input}"
        step_messages = messages + [{"role": "user", "content": step_prompt}]
        payload = {
            "model": "llama3",
            "messages": step_messages,
            "stream": False
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        response = requests.post(api_endpoint, headers=headers, json=payload)
        if response.status_code != 200:
            print(f"Error: {response.text}")
            continue
        resp_json = response.json()
        steps_text = resp_json.get("message", {}).get("content", "")
        print("[Problem Steps]\n" + steps_text)
        # Try to parse steps as a list (if numbered or bulleted)
        steps = re.findall(r'\d+\.\s*(.*)', steps_text)
        if not steps:
            steps = [s.strip('- ').strip() for s in steps_text.split('\n') if s.strip()]
        current_problem["steps"] = steps
        if not steps:
            print("Could not parse steps. Treating the whole response as a single step.")
            current_problem["steps"] = [steps_text.strip()]
        # Save current_problem to file
        try:
            with open(current_problem_file, "w") as f:
                json.dump(current_problem, f)
        except Exception as e:
            print(f"Error saving current problem: {e}")
        # Add the new user query to the messages
        messages.append({"role": "user", "content": user_input})
        continue
    else:
        # Timeout: work on next step of current problem if any
        if current_problem["steps"] and current_problem["current_step"] < len(current_problem["steps"]):
            step_idx = current_problem["current_step"]
            step = current_problem["steps"][step_idx]
            # Build context with cumulative results
            context = "\n".join([f"Step {i+1}: {res}" for i, res in enumerate(current_problem["cumulative_results"])])
            step_prompt = f"Step {step_idx+1}: {step}\nPrevious results (if any):\n{context}"
            step_messages = messages + [{"role": "user", "content": step_prompt}]
            payload = {
                "model": "llama3",
                "messages": step_messages,
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
                print(f"[Step {step_idx+1}] {assistant_message}")
                # Store result and increment step
                current_problem["cumulative_results"].append(assistant_message)
                current_problem["current_step"] += 1
                # Save current_problem to file
                try:
                    with open(current_problem_file, "w") as f:
                        json.dump(current_problem, f)
                except Exception as e:
                    print(f"Error saving current problem: {e}")
                # Add to messages for context
                messages.append({"role": "assistant", "content": assistant_message})
            else:
                print(f"Error working on step {step_idx+1}: {response.text}")
        else:
            # Timeout: ponder persistent goals
            ponder_goals()
