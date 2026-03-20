📋 Project Summary: TravelDev AI
Autonomous Travel Intelligence & Cinematic Discovery
TravelDev is a high-performance, multi-agent autonomous system that transforms complex natural language travel intents into precise, GDS-verified itineraries. Built on a stateful LangGraph architecture, it bridges the gap between creative planning and real-world financial accuracy, all wrapped in a premium 3D WebGL interface.

🚀 Technical Core (The "How It Works")

1. Agentic Orchestration & Logic
   Stateful DAG Architecture: Engineered a Directed Acyclic Graph using LangGraph to manage the trip-planning lifecycle: Intent Parsing → GDS Flight Auditing → Tiered Hotel Vetting → POI Landmark Slicing → Contextual Itinerary Synthesis → Budget Validation.

Structured Intelligence: Leveraged Gemini 1.5 Flash with custom prompting to ensure 100% stable JSON outputs. Implemented a "Manual Construction Engine" fallback to maintain UI integrity if the LLM encounters non-deterministic data.

Dynamic Intent Extraction: Developed a regex-based "City Sniffer" to pre-fetch destination data, allowing the UI to react before the AI completes its reasoning cycle.

2. Live GDS & Spatial Intelligence
   GDS-Grade Tooling: Integrated SerpApi (Google Hotels & Flights) to perform real-time inventory auditing, replacing legacy cached data with live market pricing and high-resolution property photography.

Strict Landmark Distribution: Engineered a backend algorithm that hard-slices real-world Points of Interest (POIs) by day. This prevents AI "landmark repetition" and ensures every day of the itinerary is geographically unique.

Robust Financial Sanitization: Built a custom regex-based currency processor to normalize non-standard GDS price strings (e.g., "€1.200,50"), ensuring "Financial Integrity" badges are mathematically accurate.

3. Cinematic UI & WebGL Engineering
   Cinematic Backdrop Engine: Developed a Ken Burns-style slideshow system using the Unsplash API. It fetches 5 landmark-specific images per destination and cycles them with a smooth 3-second cross-fade and subtle zoom effect.

3D Spatial Visualization: Integrated a high-performance WebGL globe (cobe). The globe features dynamic coordinate interpolation, flying the camera to glowing markers that represent the user's flight path in real-time.

Interactive Spatial Blueprints: Replaced static maps with custom-styled "Interactive Map Cards." These provide one-click deep links to Google Maps, pre-loaded with the day's specific landmarks.

🛠️ Engineering Highlights (CV-Ready Bullets)
API Hardening: Architected a resilient backend layer in FastAPI to handle complex, nested GDS responses and Base64-encoded entity IDs.

Full-Stack State Management: Synchronized LangGraph state variables with a Vite/React frontend, maintaining a "Verified Journey" status across multi-step execution windows.

Defensive UI Architecture: Implemented resilient useMemo parsing hooks to handle fluctuating AI JSON structures, preventing frontend crashes during malformed responses.

Visual Latency Masking: Designed a "Split-Flap" style Departure Board loading state to transform high-latency AI reasoning into an engaging brand-building moment.

📅 Final Development Milestones
Phase 1: Foundation & Geocoding
Established the FastAPI / React bridge.

Engineered geocoding nodes to convert natural language into GPS-ready markers.

Phase 2: GDS Integration & Hardening
The Pricing Challenge: Solved currency symbol and comma-injection issues using robust regex sanitization.

Flight Transparency: Redesigned result cards to show stacked Outbound/Return price breakdowns for maximum user clarity.

Phase 3: Premium Polish & Launch
Cinematic Slideshows: Moved from static backdrops to dynamic destination rotation.

Itinerary Perfection: Implemented the "Triple-Point Mandate," forcing the AI to provide Morning, Mid-day, and Evening activities using real-world landmark descriptions.

Spatial Interaction: Integrated Interactive Map Cards to bridge the gap between digital planning and real-world walking routes.
