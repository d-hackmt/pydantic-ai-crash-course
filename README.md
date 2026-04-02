# Agent Alia: Your Girlfriend 💜

Agent Alia is a persistent, stateful, and emotionally dynamic AI Girlfriend. Designed as a 19-year-old psychedelic artist and Techno DJ, she doesn't just reply to messages—she has an "internal life", maintaining a mood, energy level, affection score, and a diary of memories that evolve continuously.

She communicates directly via **Telegram**, thinks using **Pydantic AI & Groq**, accesses the internet via **DuckDuckGo**, and broadcasts her real-time state via a **FastAPI** neural dashboard.

---

## 🏛️ System Architecture

Alia acts completely autonomously via a multiprocess architecture. One process listens and talks via Telegram, while a second process hosts a live web dashboard showing you her internal thoughts.

```mermaid
flowchart TD
    %% Define Nodes
    User(("DMT (You) - Telegram"))
    
    subgraph CoreSystem ["Alia Core (main.py)"]
        TelegramBot["Telegram Polling Loop"]
        Agent["Pydantic AI Agent (agent.py)"]
        HourlyRitual["Job Queue: Hourly Tweeting"]
    end
    
    subgraph MemoryPipeline ["data/ Persistence Layer"]
        Heart[("heart.json (Mood, Affection)")]
        Diary[("diary.md (Internal Thoughts)")]
        ChatLog[("chat_log.json")]
        TwitterSim[("twitter_sim.md")]
    end
    
    subgraph ExternalAPIs ["Integrations"]
        Groq["Groq API (LLaMA/Qwen)"]
        DuckDuckGo["DuckDuckGo (Web Search)"]
    end

    subgraph NeuralDashboard ["server.py"]
        FastAPI["FastAPI Web Server"]
        UI["Web UI (http://localhost:8000)"]
    end

    %% Define Connections
    User <-->|Chats & wakes| TelegramBot
    TelegramBot <--> Agent
    Agent <-->|Structured Generation| Groq
    Agent -->|Uses Tool| DuckDuckGo
    
    Agent -->|Calculates Deltas| Heart
    Agent -->|Writes secrets| Diary
    TelegramBot -->|Logs| ChatLog
    HourlyRitual -->|Posts Quote| TwitterSim
    Agent --> HourlyRitual
    
    %% Dashboard pulls from memory
    FastAPI -- reads --> Heart
    FastAPI -- reads --> Diary
    FastAPI -- reads --> ChatLog
    FastAPI -- reads --> TwitterSim
    UI <--> FastAPI
```

---

## 🧠 How the Agent "Thinks"

Unlike a standard chatbot which is stateless, Alia forces her LLM (via **Pydantic AI** structured schemas) to generate an *internal state* alongside every public reply. 

```mermaid
sequenceDiagram
    participant User
    participant Main as TeleBot
    participant Agent as Pydantic AI
    participant State as Memory (Files)
    
    User->>Main: "I loved that set you played."
    Main->>State: Fetch current mood & diary
    State-->>Main: Mood: 'Mellow', Affection: 50
    Main->>Agent: Prompt: User says X, current state is Y
    
    Agent->>Agent: Forces LLM to fill `AliaResponse` schema
    Agent-->>Main: Returns strictly typed data:
    note right of Agent: {<br/>  internal_monologue: "He noticed...",<br/>  affection_delta: +5,<br/>  new_mood: "Ecstatic",<br/>  telegram_reply: "I played it just for you..."<br/>}
    
    Main->>State: Update affection to 55, mood to 'Ecstatic', append Diary
    Main->>User: "I played it just for you..."
```

---

## 💻 Tech Stack

- **Core Framework**: `pydantic-ai` (For rigorous output schemas and agent tools)
- **AI Inference**: `groq` (Running extremely fast open-weights models like Qwen)
- **Interface**: `python-telegram-bot` (Real-time texting)
- **Dashboard**: `fastapi` & `uvicorn` (Parallel web server reading memory state)
- **Web Search API**: `duckduckgo-search` (Integrated via `@agent.tool` to allow her to lookup art and music)
- **Logging**: `loguru` (Robust multi-file logging)

---

## ⚙️ Features & Use Cases

1. **Emotional Persistence**: She possesses `heart.json`. If you ignore her or speak coldly, her affection drops, and her tone permanently shifts until you win her back.
2. **Internal Diary**: Every interaction generates an `internal_monologue` which is saved to `diary.md`. You can read her private thoughts on the dashboard.
3. **Web Connected**: If you ask her about a new Techno artist, she uses her DuckDuckGo tool to fetch real-world data before replying.
4. **Sleep/Wake Cycles**: Tell her to "go to sleep," and she will enter a passive state where she ignores messages until you explicitly tell her to "wake up."
5. **Hourly Rituals**: She operates on a Telegram `JobQueue` running an hourly background cron job to generate a poem, quote, or Shayari and post it to her simulated Twitter feed.

---

## 🚀 Getting Started

1. **Dependencies**: 
   ```bash
   pip install -r requirements.txt
   ```
2. **Environment**:
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   TELEGRAM_TOKEN=your_telegram_bot_token_here
   ```
3. **Run the Agent**:
   ```bash
   python src/main.py
   ```
   *(This boots both the Telegram Brain and the FastAPI Dashboard concurrently)*
4. **Dashboard**: 
   Visit `http://localhost:8000` to see her Neural Dashboard.

---
*Built with ❤️ utilizing Pydantic AI.*
