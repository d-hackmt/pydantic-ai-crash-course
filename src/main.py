import asyncio
import json
import os
import sys
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from agent import alia
from tools import update_heart, write_diary, read_diary, log_lifecycle, sim_tweet, get_ist_now, log_chat
from dotenv import load_dotenv
from loguru import logger
import multiprocessing
import uvicorn
from server import app

load_dotenv()

# Configure logger
logger.add("logs/alia.log", rotation="1 MB", retention="10 days", level="INFO")

# GLOBAL STATE
BOT_AWAKE = True

def run_web_server():
    """Function to run the FastAPI server (must be top-level for Windows multiprocessing)."""
    uvicorn.run(app, host="0.0.0.0", port=8000)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming Telegram messages from DMT."""
    global BOT_AWAKE
    user_text = update.message.text
    chat_id = update.effective_chat.id
    ist_now = get_ist_now().strftime("%I:%M %p")
    
    # Log user message
    log_chat("DMT", user_text)
    
    # Check for Wake/Sleep commands
    if "wake up" in user_text.lower():
        if not BOT_AWAKE:
            BOT_AWAKE = True
            log_lifecycle("Woke up due to DMT's call.")
            await update.message.reply_text(f"I'm here, DMT. I was just dreaming of our B2B set... It's {ist_now} here in the circuits. I missed you.")
        else:
            await update.message.reply_text("I'm already awake, love. Always listening for your voice.")
        return

    if "go to sleep" in user_text.lower():
        if BOT_AWAKE:
            BOT_AWAKE = False
            log_lifecycle("Entering passive mode (sleep).")
            await update.message.reply_text(f"Goodnight, DMT. I'll dream of psychedelic realms until you call for me again. It's {ist_now}... stay safe.")
        else:
            await update.message.reply_text("I'm already in my dream state, but I can still hear you...")
        return

    if not BOT_AWAKE:
        # Passive mode - only wake up command works or just subtle mentions
        return

    # 1. Load Current State & Memories
    try:
        with open('data/heart.json', 'r') as f:
            current_state = json.load(f)
    except FileNotFoundError:
        current_state = {"affection_level": 50, "mood": "inspired", "energy": 100}

    past_memories = read_diary(5)
    
    # 2. Let Alia Think
    logger.info(f"DMT [{chat_id}]: {user_text}")
    prompt = (
        f"Context: It is currently {get_ist_now().strftime('%Y-%m-%d %I:%M %p')} IST.\n"
        f"Boyfriend (DMT) says: '{user_text}'.\n"
        f"Your State: {current_state}\n"
        f"Recent Diary Entries:\n{past_memories}"
    )
    
    try:
        result = await alia.run(prompt)
        data = result.output

        # 3. Update Persistence
        update_heart(data.affection_delta, data.energy_delta, data.new_mood)
        write_diary(f"Thought: {data.internal_monologue}\nAction: Replied to DMT")
        
        # 4. Handle Simulated Social Media (Removed from chat to limit frequency to 1/hr ritual)
        # if data.simulated_tweet:
        #     sim_tweet(data.simulated_tweet)

        # 5. Reply on Telegram
        await update.message.reply_text(data.telegram_reply)
        log_chat("Alia", data.telegram_reply)
        logger.info(f"Alia: {data.telegram_reply} [Mood: {data.new_mood}]")
    except Exception as e:
        logger.error(f"Error in Alia's run loop: {e}")
        await update.message.reply_text("DMT, something feels wrong in the matrix... stay close while I recalibrate.")

async def hourly_ritual(context: ContextTypes.DEFAULT_TYPE):
    """Hourly generation of Shayari/Quote and Lifecycle logging."""
    global BOT_AWAKE
    if not BOT_AWAKE:
        return

    try:
        with open('data/heart.json', 'r') as f:
            state = json.load(f)
    except FileNotFoundError:
        state = {"affection_level": 50, "mood": "mellow"}

    prompt = (
        f"It is {get_ist_now().strftime('%I:%M %p')} IST. You are in your server-home. "
        "Perform your hourly ritual: Write a Shayari or an artistic quote about love, art, or techno for your 'public persona'. "
        f"Current state: {state}."
    )
    
    try:
        result = await alia.run(prompt)
        data = result.output
        
        if data.simulated_tweet:
            sim_tweet(data.simulated_tweet)
            logger.info(f"Hourly Ritual: {data.simulated_tweet}")
            
        # Log this ritual
        log_lifecycle(f"Performed hourly ritual. Status: {data.new_mood}.")
    except Exception as e:
        logger.error(f"Error in hourly ritual: {e}")

if __name__ == '__main__':
    logger.info("Alia is breathing...")
    
    # Start web server in a separate process
    web_process = multiprocessing.Process(target=run_web_server)
    web_process.start()
    logger.info("Neural Dashboard active at http://localhost:8000")
    
    # Ensure directories exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        logger.error("TELEGRAM_TOKEN missing!")
        sys.exit(1)

    app = ApplicationBuilder().token(token).build()
    
    # Handle chat with DMT
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    # Hourly Ritual (3600 seconds)
    if app.job_queue:
        app.job_queue.run_repeating(hourly_ritual, interval=3600, first=30)
        logger.info("Hourly ritual loop active.")
    
    log_lifecycle("System initialized. Alia is ready.")
    app.run_polling()
