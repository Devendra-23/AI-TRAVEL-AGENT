# CHANGELOG: TravelDev AI Agent

All notable changes to the TravelDev AI Travel Agent project are documented in this file.

## [[2026-03-20]] — Cinematic UI & Spatial Intelligence

### Added

- **Cinematic Backdrop Engine**: Implemented a Ken Burns-style rotating slideshow that fetches 5 high-resolution destination landmarks via Unsplash API with a smooth 3-second cross-fade.
- **"Mega" GDS Flight Stack**: Redesigned the flight results card to feature expanded Outbound/Return breakdown with 240px width containers and high-contrast currency display.
- **Hard-Slicing Itinerary Logic**: Engineered a backend landmark distribution algorithm in `nodes.py` that manually partitions real-world POIs into specific days, eliminating AI landmark repetition.
- **Premium Map Access Cards**: Integrated high-fidelity Interactive Map Cards into the daily itinerary timeline, providing direct deep-links to Google Maps spatial data.
- **Triple-Point Mandate**: Reconfigured the LLM prompt architecture to strictly enforce a "Morning, Mid-day, Evening" three-activity structure per travel day.

### Changed

- **UI De-cluttering**: Removed the legacy weather capsule to prioritize real-time financial and routing data.
- **Defensive Itinerary Rendering**: Updated the frontend `useMemo` hooks to resiliently parse nested AI JSON structures, preventing UI crashes on malformed LLM responses.

## [[2026-03-18]] — API Hardening & GDS Integration

### Added

- **SerpApi Google GDS Integration**: Migrated Hotel and Flight tools to Google GDS engines to resolve legacy provider 403 Forbidden errors.
- **Regex Price Sanitization**: Implemented a robust currency cleaner in `hotels.py` to handle non-standard GDS price strings (e.g., "€140", "1.200,00").
- **Date Validation Constraints**: Implemented `min={today}` on frontend date pickers to prevent past-date selection.

### Fixed

- **JSON Navigation Crash**: Resolved a 'list' object has no attribute 'get' error via strict type-checking on API handshakes.
- **The "LHR Loop" Bug**: Fixed a hardcoded dependency in `nodes.py` that forced all flights to originate from London.
- **Flight Suffix Logic**: Standardized IATA code handling to automatically switch between 3-letter codes and entity IDs.

## [[2026-03-16]] — Dynamic Scenery & Environment Sync

### Added

- **"City Sniffer" Pre-fetch**: Implemented a regex-based frontend listener that detects destination intent and fetches cityscapes before the LLM finishes processing.
- **Environment Architecture**: Separated `.env` configurations for Vite and FastAPI to ensure proper client-side injection.
- **Visual Console Auditing**: Added stylized debug logs (📸, ✅, ❌) to track real-time agent handshakes.

### Changed

- **Hybrid Model Strategy**: Optimized geocoding sub-tasks using Gemini 1.5 Flash to reduce latency and API cost.

## [[2026-03-15]] — Spatial Intelligence & UX Redesign

### Added

- **Dual-Point Geolocation**: Updated AI nodes to extract GPS coordinates for both origin and destination for pathing logic.
- **Multi-Marker WebGL Rendering**: Enhanced the `cobe` globe to render synchronized flight paths between two glowing markers.
- **Split-Input UI**: Redesigned the search interface to separate "Leaving from" and "Destination," reducing intent extraction hallucinations.

### Fixed

- **NaN Rendering Crash**: Implemented defensive validation to ensure coordinates are valid floats before passing to the WebGL canvas.

## [[2026-03-11] - [2026-03-13]] — Core Infrastructure

### Added

- **LangGraph Orchestration**: Established state-driven DAG architecture (Input -> Research -> Audit -> Plan).
- **FastAPI Bridge**: Exposed the agentic workflow as a REST API.
- **CORS Middleware**: Enabled secure communication between Vite (5173) and FastAPI (8000).
- **Editable Package Install**: Resolved local module linking issues using `pip install -e .`.
