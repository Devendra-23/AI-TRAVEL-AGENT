# Project Development Log

## [2026-03-11] - Initial Setup

- Initialized frontend with Vite, React, and pnpm.
- Configured Tailwind CSS for styling.
- Set up Python virtual environment and installed `langchain-google-genai`.
- Integrated Google Gemini API via Google AI Studio key.

Structure: Created core backend directory tree (agent/, tools/, utils/).

Mocks: Initialized mock_data.py to allow for local testing without API costs.

State: Defined TripState schema to manage data flow between Gemini nodes.

Logic: Populated agent/graph.py with the StateGraph definition.

Routing: Implemented sequential edges for tool execution and a conditional edge for budget enforcement.

Milestone: Completed Milestone 3: Graph Architecture.

Infrastructure: Implemented an editable package installation (pip install -e .) to resolve persistent ModuleNotFoundError issues.

Connectivity: Developed server.py using FastAPI to expose the LangGraph agent as a REST API endpoint.

## [2026-03-12] - Second Setup

Security: Configured CORS middleware to allow cross-origin requests from the React/Vite frontend.

Bug Fix: Resolved TypeError in parse_input_node by implementing null-checking before type casting (float/int).

Robustness: Enhanced JSON parsing logic to provide fallback defaults for duration and budget when LLM extraction is incomplete.API

Integration: Developed server.py using FastAPI to expose the TripState as a structured JSON endpoint.

CORS Configuration: Enabled cross-origin resource sharing to allow seamless communication with the Vite/React frontend.

Refactoring: Cleaned citation markers from server.py to prevent runtime NameError exceptions.

Resolved: Fixed "Blank Screen" bug caused by Vite's default flexbox centering in index.css.

Implemented: Deployed a v4 Tailwind CSS architecture for a high-fidelity landing page.

Branding: Established "NomadAI" visual identity with a custom color palette (#2563eb Blue).

Copywriting: Refactored Hero messaging to target user pain points (confusion/worry) rather than technical "building."

UX Strategy: Transitioned tone from "Product-Centric" to "User-Centric" to increase conversion for non-technical travelers.

All notable changes to the **Amazing AI Travel Agent** project will be documented in this file.

## [Unreleased] / [2026-03-13]

### Added

- **3D Hero Integration**: Added an interactive WebGL globe (`cobe`) to the React frontend hero section to establish a strong visual hierarchy.

### Changed

- **Responsive Canvas Management**: Replaced aggressive viewport display toggles (`hidden`) with responsive opacity scaling to preserve the WebGL drawing context on mobile devices.

### Fixed

- **CSS Architecture**: Resolved complex z-index stacking context anomalies by implementing CSS `isolate` on the parent container, preventing the 3D canvas from bleeding behind the global background.

## [2026-03-14]

### Added

- **Takeoff Loading Animation**: Added a custom SVG airplane animation to the submit button to improve perceived performance during LangGraph node execution.
- **Boarding Pass Timeline UI**: Implemented a responsive vertical timeline to display the day-by-day AI generated itinerary, including conditional badges for paid vs. free activities.
- **Dynamic Globe Targeting**: Integrated GPS coordinate parsing into the Gemini `parse_input_node`. The frontend `<TravelGlobe />` now dynamically receives `lat` and `lng` props, calculating `phi` and `theta` to auto-rotate and drop a marker on the exact destination.

### Changed

- **UX Placeholder Text**: Updated the search input placeholder to implicitly train users to provide an "origin city" (e.g., "from London"), improving the accuracy of the flight-search tool.

Added
Dynamic Dual-Point Geolocation: The AI agent now extracts GPS coordinates for both the Origin and Destination cities.

Multi-Marker 3D Globe: Updated the WebGL hero section to render multiple glowing markers simultaneously, visualizing the flight path from departure to arrival.

Split-Input UX: Redesigned the search bar to include explicit "Leaving from" and "Destination" fields, significantly improving intent extraction accuracy.

GPS Safety Layer: Implemented a JavaScript defensive layer to parse AI-generated strings into valid floats, preventing WebGL "NaN" rendering crashes.

Changed
LLM Model Upgrade: Switched from gemini-2.5-flash-lite to gemini-2.5-flash to increase API rate limits and improve geographic reasoning.

State Schema Expansion: Updated the LangGraph TripState and FastAPI initial_state to support persistent storage of spatial coordinates.

Fixed
Fixed a 500 Internal Server Error caused by missing coordinate keys in the initial state dictionary.

Resolved a "NaN" crash in the 3D globe component where missing coordinates caused the WebGL canvas to go blank.

[[2026-03-16]] - Dynamic Backgrounds & Quota Hardening
Added
Instant Pre-fetch Logic: Implemented a regex-based "City Sniffer" in the frontend to detect destination intent (e.g., "in Sweden", "to Italy") before the AI backend responds.

Dynamic Scenery Backdrops: Integrated the Unsplash API to fetch high-resolution, contextually relevant landscape photography based on the identified destination.

Environment Sync: Separated .env architectures for Frontend (Vite) and Backend (FastAPI) to resolve cross-origin key injection issues.

Console Audit Logs: Added high-visibility debug logs (📸, ✅, ❌) to track API handshakes and asset loading in real-time.
