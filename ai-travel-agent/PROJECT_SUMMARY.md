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

API Development: Engineered a FastAPI backend to bridge a multi-agent AI system with a modern React frontend.

Packaging & Distribution: Utilized setuptools and editable installs to manage complex local module dependencies and ensure consistent environment behavior.

Full-Stack Integration: Designed a scalable architecture where AI state machines are served as production-ready microservices.

Resilient Data Pipelines: Designed a fault-tolerant input processing layer that handles non-deterministic LLM outputs, ensuring 100% execution stability even with partial user prompts.

Logic Hardening: Applied defensive programming patterns to synchronize LangGraph state variables with strictly typed Python functions.
