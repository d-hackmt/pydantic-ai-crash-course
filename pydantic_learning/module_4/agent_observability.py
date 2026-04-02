import asyncio
from dotenv import load_dotenv

# 1. ALWAYS load environment variables BEFORE importing logfire
# This ensures it finds the LOGFIRE_API_KEY
load_dotenv()

import logfire
from pydantic_ai import Agent

# 2. Configure logfire
logfire.configure()
logfire.instrument_pydantic_ai()
logfire.info('Logfire connected successfully! Hello, {place}!', place='World')

# 3. Setup our Agent
weather_agent = Agent(
    'groq:llama-3.3-70b-versatile',
    system_prompt="You are a helpful travel assistant."
)

# 4. Setup our Tool
@weather_agent.tool_plain
def check_flight_status(flight_number: str) -> str:
    """
    Use this to check if a flight is delayed or on-time.
    """
    print(f"\n[System Alert] Checking database for flight {flight_number}...")
    if "777" in flight_number:
        return "Delayed by 2 hours due to thunderstorms."
    return "On-time."

async def main():
    print("Asking the Agent...")
    response = await weather_agent.run("Is my flight BA777 delayed?")
    
    print("\n--- Agent Response ---")
    print(response.output)
    print("\n[!] Execution finished. Check your Logfire dashboard for the waterfall trace!")

if __name__ == "__main__":
    asyncio.run(main())
