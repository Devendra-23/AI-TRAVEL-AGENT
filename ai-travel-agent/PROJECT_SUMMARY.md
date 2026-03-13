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

Backend Architecture: Scaled a local AI agent into a production-ready microservice using FastAPI and Uvicorn, supporting asynchronous state machine execution.

Full-Stack Orchestration: Managed the end-to-end data lifecycle from React frontend POST requests to LangGraph autonomous agent execution.

UI/UX Engineering: Architected a modern, responsive landing page using React and Tailwind CSS v4, focusing on performance and visual hierarchy.

Problem Solving: Diagnosed and resolved layout collapse issues stemming from clashing framework defaults and global CSS configurations.

Strategic Copywriting: Engineered a user-centric messaging framework designed to reduce "Choice Overload" and decision fatigue in the travel booking lifecycle.

Product Marketing Integration: Aligned technical AI capabilities with psychological user needs, focusing on simplifying complex data into a "1-Click" stress-free solution.

- **3D UI Engineering**: Integrated an interactive WebGL globe (`cobe`) into the React hero section, optimizing rendering performance and establishing a strong visual hierarchy.
- **Advanced CSS Architecture**: Diagnosed and resolved complex z-index stacking context anomalies by implementing CSS `isolate` to explicitly manage layout boundaries and prevent canvas bleed.
- **Responsive Canvas Management**: Engineered fluid cross-device visibility for a canvas-based animation, replacing aggressive display toggles with responsive opacity scaling to preserve the WebGL drawing context on mobile viewports.
