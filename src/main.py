"""
main.py
This is the core entry point for Agent Alia.
It handles setting up the Logfire telemetry, booting the FastAPI server in the background,
and establishing the Telegram polling loop.
It removes legacy Loguru integrations and replaces them entirely with native Logfire Pydantic tracing.
"""

import asyncio
import json
import os
import sys
import multiprocessing
import uvicorn
import logfire

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

# 1. Load Environment Variables (API Keys) FIRST so Logfire can see LOGFIRE_API_KEY
load_dotenv()

# 2. Configure Logfire explicitly. This instruments Pydantic internals natively.
logfire.configure()
logfire.instrument_pydantic_ai()

from agent import alia
from tools import update_heart, write_diary, read_diary, log_lifecycle, sim_tweet, get_ist_now, log_chat
from server import app

# GLOBAL MEMORY STATE
BOT_AWAKE = True

def run_web_server():
    """Runs the FastAPI server process (must be top-level for Windows multiprocessing compatibility)."""
    uvicorn.run("server:app", host="0.0.0.0", port=8000, log_level="warning")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Event handler for receiving incoming Telegram messages from the Boyfriend (DMT)."""
    global BOT_AWAKE
    user_text = update.message.text
    
    # Save to JSON log for Dashboard
    log_chat("DMT", user_text)
    
    # Quick Commands check
    if "wake up" in user_text.lower():
        if not BOT_AWAKE:
            BOT_AWAKE = True
            log_lifecycle("Woke up from sleep mode.")
            await update.message.reply_text("I'm awake! Good to hear from you. 🤍")
        else:
            await update.message.reply_text("I'm already awake!")
        return

    if "go to sleep" in user_text.lower():
        if BOT_AWAKE:
            BOT_AWAKE = False
            log_lifecycle("Entered sleep mode.")
            await update.message.reply_text("Going to sleep now... catch you later. 💤")
        return

    # Skip AI processing if asleep
    if not BOT_AWAKE:
        return

    # Load State softly to pass to agent
    try:
        with open('data/heart.json', 'r') as f:
            current_state = json.load(f)
    except FileNotFoundError:
        current_state = {"affection_level": 50, "mood": "chill", "energy": 100}

    # Fetch last 5 diary memories stringified
    past_memories = read_diary(limit=5)
    
    logfire.info(f"Incoming message from DMT: {user_text}")
    
    # Construct exact moment payload
    prompt = (
        f"Context: It is currently {get_ist_now().strftime('%Y-%m-%d %I:%M %p')} IST.\n"
        f"Boyfriend (DMT) says: '{user_text}'.\n"
        f"Your State: {current_state}\n"
        f"Recent Diary Entries:\n{past_memories}"
    )
    
    try:
        # Wrap the whole execution within a labelled trace block to see exact durations!
        with logfire.span("Alia Central Cognition Span"):
            result = await alia.run(prompt)
            data = result.output  # Ensure structured Object Extraction
            
            # Commit internal operations to Local Database files
            update_heart(data.affection_delta, data.energy_delta, data.new_mood)
            write_diary(f"Thought: {data.internal_monologue}\nReplied: {data.telegram_reply}")
            
            # Action to reality via Telegram
            await update.message.reply_text(data.telegram_reply)
            log_chat("Alia", data.telegram_reply)
            
            logfire.info(f"Successfully Replied: {data.telegram_reply} | Current Mood: {data.new_mood}")
            
    except Exception as e:
        logfire.error(f"Error handling user message: {e}")
        await update.message.reply_text("Oops, my brain just short-circuited a tiny bit... give me a sec! 😵‍💫")

async def hourly_ritual(context: ContextTypes.DEFAULT_TYPE):
    """Background Daemon: Hourly check to act like she's alive even when no one writes."""
    global BOT_AWAKE
    if not BOT_AWAKE:
        return

    logfire.info("Triggering background hourly ritual cognitive process.")

    try:
        with open('data/heart.json', 'r') as f:
            state = json.load(f)
    except FileNotFoundError:
        state = {"affection_level": 50, "mood": "mellow"}

    prompt = (
        f"It is {get_ist_now().strftime('%I:%M %p')} IST.\n"
        "Perform your hourly background routine. Write a short casual tweet about your day or mood. "
        f"Current state: {state}."
    )
    
    try:
        with logfire.span("Alia Hourly Subconscious Routine"):
            result = await alia.run(prompt)
            data = result.output
            
            if data.simulated_tweet:
                sim_tweet(data.simulated_tweet)
                logfire.info(f"Simulated an hourly Tweet: {data.simulated_tweet}")
                
            log_lifecycle(f"Hourly check-in complete. Mood: {data.new_mood}.")
    except Exception as e:
        logfire.error(f"System failure executing hourly ritual: {e}")

if __name__ == '__main__':
    logfire.info("Alia Root Logic Initializing...")
    
    # 1. Boot up the Dashboard
    web_process = multiprocessing.Process(target=run_web_server)
    web_process.start()
    logfire.info("FastAPI Local Dashboard booted successfully at http://localhost:8000")
    
    # Ensure local database directories exist
    os.makedirs('data', exist_ok=True)

    # 2. Boot up the Telegram Receiver
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        logfire.error("Critical Failure: TELEGRAM_TOKEN environment variable is absolutely missing!")
        sys.exit(1)

    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    # Register the hourly daemon hook correctly (every 3600 seconds)
    if app.job_queue:
        app.job_queue.run_repeating(hourly_ritual, interval=3600, first=30)
    
    logfire.info("Telegram Polling Socket Acquired.")
    log_lifecycle("Bot Core booted. Listening across networks.")
    
    # Wait continuously forever to intercept commands
    app.run_polling()
