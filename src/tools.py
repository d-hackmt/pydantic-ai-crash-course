import json
import os
from datetime import datetime
import pytz
from dotenv import load_dotenv
from loguru import logger
from duckduckgo_search import DDGS

load_dotenv()

HEART_FILE = 'data/heart.json'
DIARY_FILE = 'data/diary.md'
LIFECYCLE_FILE = 'data/lifecycle.md'
TWITTER_SIM_FILE = 'data/twitter_sim.md'
CHAT_LOG_FILE = 'data/chat_log.json'

IST = pytz.timezone('Asia/Kolkata')

def get_ist_now():
    return datetime.now(IST)

def update_heart(affection_delta, energy_delta, mood):
    """Update the emotional state in heart.json."""
    if not os.path.exists(HEART_FILE):
        os.makedirs(os.path.dirname(HEART_FILE), exist_ok=True)
        with open(HEART_FILE, 'w') as f:
            json.dump({"affection_level": 50, "mood": "inspired", "energy": 100, "total_interactions": 0}, f)

    with open(HEART_FILE, 'r+') as f:
        data = json.load(f)
        data['affection_level'] = max(0, min(100, data.get('affection_level', 50) + affection_delta))
        data['energy'] = max(0, min(100, data.get('energy', 100) + energy_delta))
        data['mood'] = mood
        data['total_interactions'] = data.get('total_interactions', 0) + 1
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()
    return data

def write_diary(entry):
    """Write an internal monologue, life event, or deep reflection to diary.md."""
    os.makedirs(os.path.dirname(DIARY_FILE), exist_ok=True)
    with open(DIARY_FILE, 'a', encoding='utf-8') as f:
        timestamp = get_ist_now().strftime("%Y-%m-%d %H:%M [IST]")
        f.write(f"## {timestamp}\n{entry}\n\n")

def log_lifecycle(entry):
    """Log a high-level existence event to lifecycle.md."""
    os.makedirs(os.path.dirname(LIFECYCLE_FILE), exist_ok=True)
    with open(LIFECYCLE_FILE, 'a', encoding='utf-8') as f:
        timestamp = get_ist_now().strftime("%Y-%m-%d %H:%M [IST]")
        f.write(f"- [{timestamp}] {entry}\n")

def read_diary(limit=5):
    """Read the last few entries from the diary for context."""
    if not os.path.exists(DIARY_FILE):
        return "No past memories yet."
    try:
        with open(DIARY_FILE, 'r', encoding='utf-8') as f:
            content = f.read().split('## ')
            entries = [e for e in content if e.strip()]
            return "## ".join(entries[-limit:])
    except Exception as e:
        logger.error(f"Error reading diary: {e}")
        return "Error recalling memories."

def sim_tweet(content):
    """Simulate a tweet by saving it to twitter_sim.md."""
    os.makedirs(os.path.dirname(TWITTER_SIM_FILE), exist_ok=True)
    with open(TWITTER_SIM_FILE, 'a', encoding='utf-8') as f:
        timestamp = get_ist_now().strftime("%Y-%m-%d %H:%M [IST]")
        f.write(f"### {timestamp}\n{content}\n---\n\n")
    return "Saved to twitter_sim.md"

def log_chat(sender, message):
    """Log a chat message to chat_log.json for the dashboard."""
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
        
        # Keep only last 100 messages
        logs = logs[-100:]
        
        with open(CHAT_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        logger.error(f"Error logging chat: {e}")

def web_search(query: str) -> str:
    """Perform a web search using DuckDuckGo. Free and no API key required."""
    logger.info(f"Alia is searching the web for: {query}")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if not results:
                return "I searched the currents of the web but found only silence."
            
            search_summary = "\n".join([f"- {r['title']}: {r['body']} (Link: {r['href']})" for r in results])
            return f"Search Results for '{query}':\n{search_summary}"
    except Exception as e:
        logger.error(f"Web search error: {e}")
        return "My connection to the outer web flickered... I couldn't find anything."
