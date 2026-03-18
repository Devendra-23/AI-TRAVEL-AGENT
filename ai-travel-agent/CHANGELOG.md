CHANGELOG.md: Amazing AI Travel Agent
All notable changes to the Amazing AI Travel Agent project are documented in this file.

[[2026-03-18]] — API Hardening & GDS Integration
Added
RapidAPI booking-com18 Integration: Migrated the Hotel and Flight tools to a new high-fidelity provider to resolve "Subscription" and 403 Forbidden errors.

Base64 Location Parsing: Engineered a resilient extraction layer in hotels.py to handle the complex, encoded Destination IDs required by modern travel APIs.

Date Validation Constraints: Implemented min={today} on frontend date pickers to prevent past-date selection and ensure logical travel sequences (Return > Departure).

Fixed
JSON Navigation Crash: Resolved a 'list' object has no attribute 'get' error by implementing type-checking on API responses that fluctuated between dictionary and list structures.

The "LHR Loop" Bug: Fixed a hardcoded dependency in nodes.py that forced all flights to originate from London; the system now dynamically honors the user's specific origin city.

Flight Suffix Logic: Standardized IATA code handling to automatically switch between 3-letter codes and -sky entity IDs based on the specific API endpoint requirements.

[[2026-03-16]] — Dynamic Scenery & Environment Sync
Added
"City Sniffer" Pre-fetch: Implemented a regex-based frontend listener that detects destination intent and fetches high-resolution cityscapes from the Unsplash API before the LLM finishes processing.

Environment Architecture: Separated .env configurations for Vite and FastAPI to ensure VITE\_ prefixes are properly injected into the client-side build.

Visual Console Auditing: Added stylized debug logs (📸, ✅, ❌) to the browser and server consoles to track real-time API handshakes.

Changed
Hybrid Model Strategy: Switched from Gemini 1.5 Pro to Gemini 1.5 Flash for geocoding sub-tasks to optimize API quota usage and reduce latency.

[[2026-03-15]] — Spatial Intelligence & UX Redesign
Added
Dual-Point Geolocation: Updated the AI node to extract GPS coordinates for both origin and destination.

Multi-Marker WebGL Rendering: Enhanced the cobe globe to render a flight path between two glowing markers simultaneously.

Split-Input UI: Redesigned the search interface to separate "Leaving from" and "Destination," drastically reducing LLM "hallucination" during intent extraction.

Fixed
NaN Rendering Crash: Implemented a defensive JS layer to validate that coordinates are floats before passing them to the WebGL canvas.

[[2026-03-14]] — Interaction Polish & Boarding Pass UI
Added
Departure Board Loading State: Created a custom "Split-Flap" style display to manage user expectations during the 5-7 second LangGraph execution window.

Boarding Pass Timeline: Implemented a responsive vertical itinerary UI to parse nested JSON into a readable, day-by-day traveler schedule.

Changed
CSS Stacking Context: Implemented CSS isolate on the 3D hero container to resolve z-index anomalies where the globe would bleed into the background.

[[2026-03-11] - [2026-03-13]] — Core Infrastructure
Added
LangGraph Orchestration: Established the state-driven DAG architecture (Input -> Research -> Audit -> Plan).

FastAPI Bridge: Exposed the agentic workflow as a REST API to support the React frontend.

CORS Middleware: Enabled secure cross-origin resource sharing between the 5173 (Vite) and 8000 (FastAPI) ports.

Editable Package Install: Resolved persistent ModuleNotFoundError issues using pip install -e . for local module linking.
