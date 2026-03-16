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

- **Micro-Interaction Engineering**: Replaced standard loading states with a custom CSS keyframe "Takeoff" animation (`@keyframes fly`), transforming a 5-second API wait time into an engaging visual event.
- **Dynamic 3D State Management**: Engineered a React `useEffect` hook to calculate mathematical coordinate conversions (Latitude/Longitude to Phi/Theta), allowing the `cobe` WebGL globe to autonomously rotate and drop a glowing marker exactly on the AI-generated travel destination.
- **Data Visualization UI**: Architected a "Boarding Pass" style timeline UI using Tailwind CSS to render complex nested JSON (daily arrays and activity lists) into an intuitive, visually appealing day-by-day traveler schedule.

🚀 Technical Core
Agentic Orchestration: Uses a Directed Acyclic Graph (DAG) via LangGraph to manage the trip-planning lifecycle (Input Parsing -> Research -> Planning -> Budget Audit).

3D Spatial Visualization: A custom WebGL globe rendered with cobe that dynamically responds to LLM-extracted GPS coordinates.

Contextual NLP: Implements a dual-input "Split-Input" UI that allows users to define origin and destination separately, which are then stitched for high-precision LLM intent extraction.

Financial Integrity: Includes a specialized Euro-Audit node that calculates real-time costs and verifies the feasibility of the plan against user-defined budget constraints.

March 15th: Visual & UX Foundation
3D Globe Integration: We successfully embedded the cobe WebGL globe. We engineered the useEffect hooks to translate AI-generated Latitude/Longitude into 3D coordinates, allowing the globe to rotate and mark destinations dynamically.

"Boarding Pass" Timeline: Built the front-end UI to parse the complex nested JSON from the AI into a readable, day-by-day traveler schedule.

Micro-Interaction Polish: Replaced static loading states with a custom airport-style "Departure Board" and airplane takeoff animations to manage user expectations during LLM processing.

🚀 March 16th: Dynamic Scenery & Quota Hardening
Instant Pre-fetch Logic (The "Eyes"): We implemented a regex-based "City Sniffer" in the React frontend. This scans the user's prompt (e.g., "Sweden") and immediately fetches high-resolution travel photography from the Unsplash API. This solved the "white screen" wait time by giving instant visual feedback while the AI "thought" in the background.

API Security Sync: We resolved a critical 401 Unauthorized issue by properly prefixing environment variables with VITE\_ and correctly placing .env files in separate frontend/backend directories to ensure Vite could "see" the keys.

Rate-Limit Engineering: After hitting 429 RESOURCE_EXHAUSTED errors with the Gemini 2.5 Pro model, we implemented a Hybrid Model Strategy. We switched to gemini-1.5-flash and gemini-2.5-flash-lite for development testing to take advantage of higher free-tier quotas.

Backend Resilience: Fixed several 404 NOT_FOUND crashes by correcting model-name mapping strings (e.g., adding -latest suffixes) to match the current Google GenAI SDK requirements.
