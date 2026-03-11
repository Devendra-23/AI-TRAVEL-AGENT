# Project: Amazing AI Travel Agent

## Summary

An autonomous multi-agent system that generates complete, budget-aware travel itineraries from a single natural language prompt.

## Key Technical Highlights (CV Bullets)

- **Orchestration**: Built a stateful agentic workflow using **LangGraph** to manage multi-step planning and tool-calling sequences.
- **LLM Integration**: Leveraged **Google Gemini 1.5** for high-context reasoning and structured data extraction.
- **Tool Calling**: Integrated real-time APIs (SerpAPI, OpenWeather) to fetch live flight and weather data.
- **Constraint Logic**: Implemented a conditional "Budget Checker" node that triggers the agent to re-plan if costs exceed user limits.
- **Frontend**: Developed a responsive dashboard using **React**, **Vite**, and **Tailwind CSS**, managed with **pnpm**.

Modular Architecture: Implemented a decoupled project structure separating AI logic, external tools, and state management.

Mock-Driven Development: Engineered a mock data layer to facilitate rapid prototyping and testing of agentic flows before API integration.

Graph Orchestration: Designed a state-driven architecture using LangGraph to manage the execution order of specialized AI agents.

Non-Linear Control Flow: Implemented conditional edges to facilitate autonomous self-correction (replanning) when constraints like budget are violated.
