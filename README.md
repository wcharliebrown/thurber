# thurber
Experiments in conscious AI

## Overview

`thurber.py` is an experimental agent that interacts with the Ollama LLM API to break down complex problems into sequential steps, track progress, and pursue persistent goals over time. It is designed to simulate aspects of conscious, goal-driven reasoning.

## Features
- **Stepwise Problem Solving:** Breaks down user queries into actionable steps and works through them sequentially.
- **Persistent Goals:** Allows you to set long-term goals that the agent will periodically ponder and make progress on.
- **Progress Tracking:** Saves the state of current problems and goals to disk, so progress is not lost between runs.

## Requirements
- Python 3.8+
- [Ollama](https://ollama.com/) running locally (default API endpoint: `http://localhost:11434`)
- Python packages:
  - `requests`
  - `python-dotenv`
- An `.env` file with your Ollama API key:
  - See `.env_sample` for the required format.

## Setup
1. **Clone the repository** and enter the `thurber` directory.
2. **Install dependencies:**
   ```bash
   pip install requests python-dotenv
   ```
3. **Set up your `.env` file:**
   Copy `.env_sample` to `.env` and add your actual Ollama API key.
   ```bash
   cp .env_sample .env
   # Edit .env to insert your real OLLAMA_API_KEY
   ```
4. **Start Ollama** (see [Ollama documentation](https://ollama.com/) for setup).

## Usage
Run the agent:
```bash
python thurber.py
```
- Enter a query to have the agent break it into steps and solve it.
- Type `goal: <your goal>` to add a persistent goal.
- The agent will periodically ponder persistent goals and update their progress.
- Type `exit` or `quit` to stop.

## Data Files
- `persistent_goals.json`: Stores your long-term goals and progress.
- `current_problem.json`: Tracks the current problem and its stepwise progress.

## License
See [LICENSE](LICENSE).
