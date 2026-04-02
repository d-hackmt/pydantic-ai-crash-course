# Module 3: Tools & External Intelligence

Agents are incredibly powerful, but out of the box, they are completely isolated from the real world. By giving them "Tools," we allow them to execute Python code, tap into external APIs, and browse the web synchronously.

## Core Concepts
- **Tools / Function Calling**: Native Python functions given directly to the LLM. The LLM decides *when* and *what* parameters to pass to the function.
- **Common Tools**: Pydantic native integrations for rapidly hooking into third-party services like Tavily Search.
- **LangChain Interop**: Wrapping ecosystem tools (like WikipediaAPI) into simpler Pydantic AI wrappers. 

## The Tool Execution Flow

```mermaid
flowchart LR
    Message["User: 'What is the weather in Delhi?'"] --> Agent["Pydantic AI Agent"]
    
    Agent -->|1. Identifies missing knowledge| ToolDetect{"Check available tools"}
    ToolDetect -->|Found 'check_weather()'| ToolRun["Execute Python Def"]
    
    ToolRun -->|API/Data Source| API{"External Internet / API"}
    API -->|Raw Output| Agent
    
    Agent -->|2. Integrates knowledge| Final["Final Answer: 'It is 32C in Delhi!'"]
```

## Key Methods Used
1. **`@agent.tool_plain`**: Attaches a basic, static Python function to an Agent. The agent can invoke this autonomously.
2. **`@agent.tool`**: Attaches a stateful function, allowing the python code to read from dynamic contexts (like checking an active User ID mapping).
3. **`tavily_search_tool()`**: An out-of-the-box plugin that instantly grants the agent access to the live internet safely without manual scraping logic.
