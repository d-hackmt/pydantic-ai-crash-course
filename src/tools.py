"""
tools.py
This file contains helper functions handling File IO persistence for Alia's memories.
It manages her diary, heart state, chat logs, and any external tools like DuckDuckGo search.
All logs have been replaced with proper Logfire instrumentation.
"""

import json
import os
from datetime import datetime
import pytz
import logfire

# File paths for saving context locally
HEART_FILE = 'data/heart.json'
DIARY_FILE = 'data/diary.md'
LIFECYCLE_FILE = 'data/lifecycle.md'
TWITTER_SIM_FILE = 'data/twitter_sim.md'
CHAT_LOG_FILE = 'data/chat_log.json'

IST = pytz.timezone('Asia/Kolkata')

def get_ist_now() -> datetime:
    """Get the current time in the IST timezone."""
    return datetime.now(IST)

@logfire.instrument("Update Heart State")
def update_heart(affection_delta: int, energy_delta: int, mood: str) -> dict:
    """Modifies and saves Alia's core emotional state parameters."""
    if not os.path.exists(HEART_FILE):
        os.makedirs(os.path.dirname(HEART_FILE), exist_ok=True)
        with open(HEART_FILE, 'w') as f:
            json.dump({"affection_level": 50, "mood": "inspired", "energy": 100, "total_interactions": 0}, f)

    with open(HEART_FILE, 'r+') as f:
        data = json.load(f)
        # Bounded between 0 and 100
        data['affection_level'] = max(0, min(100, data.get('affection_level', 50) + affection_delta))
        data['energy'] = max(0, min(100, data.get('energy', 100) + energy_delta))
        data['mood'] = mood
        data['total_interactions'] = data.get('total_interactions', 0) + 1
        
        # Rewind file pointer and overwrite completely
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()
        
    return data

@logfire.instrument("Write to Diary")
def write_diary(entry: str):
    """Appends an internal monologue record to her diary."""
    os.makedirs(os.path.dirname(DIARY_FILE), exist_ok=True)
    with open(DIARY_FILE, 'a', encoding='utf-8') as f:
        timestamp = get_ist_now().strftime("%Y-%m-%d %I:%M %p")
        f.write(f"## {timestamp}\n{entry}\n\n")

@logfire.instrument("Log System Lifecycle")
def log_lifecycle(entry: str):
    """Logs crucial system events (bootups, sleep modes, background rituals)."""
    os.makedirs(os.path.dirname(LIFECYCLE_FILE), exist_ok=True)
    with open(LIFECYCLE_FILE, 'a', encoding='utf-8') as f:
        timestamp = get_ist_now().strftime("%Y-%m-%d %I:%M %p")
        f.write(f"- [{timestamp}] {entry}\n")

def read_diary(limit: int = 5) -> str:
    """Extracts the most recent contextual history from her diary for the LLM."""
    if not os.path.exists(DIARY_FILE):
        return "No past memories yet."
    try:
        with open(DIARY_FILE, 'r', encoding='utf-8') as f:
            content = f.read().split('## ')
            entries = [e for e in content if e.strip()]
            return "## ".join(entries[-limit:])
    except Exception as e:
        logfire.error(f"Error reading diary database: {e}")
        return "Error recalling memories."

@logfire.instrument("Simulate Tweet")
def sim_tweet(content: str) -> str:
    """Appends a new line to her simulated twitter markdown text file."""
    os.makedirs(os.path.dirname(TWITTER_SIM_FILE), exist_ok=True)
    with open(TWITTER_SIM_FILE, 'a', encoding='utf-8') as f:
        timestamp = get_ist_now().strftime("%Y-%m-%d %I:%M %p")
        f.write(f"### {timestamp}\n{content}\n---\n\n")
    return "Saved tweet."

@logfire.instrument("Log Chat Message")
def log_chat(sender: str, message: str):
    """Maintains a JSON array of the last 100 chat messages to display natively on the dashboard."""
    os.makedirs(os.path.dirname(CHAT_LOG_FILE), exist_ok=True)
    try:
        if os.path.exists(CHAT_LOG_FILE):
            with open(CHAT_LOG_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append({
            "timestamp": get_ist_now().strftime("%Y-%m-%d %H:%M:%S"),
            "sender": sender,
            "message": message
        })
        
        # Prune to prevent infinite scaling (cap at 100)
        with open(CHAT_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(logs[-100:], f, indent=2)
            
    except Exception as e:
        logfire.error(f"Error logging chat to frontend database: {e}")

