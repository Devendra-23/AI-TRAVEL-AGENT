import React, { useState, useEffect, useRef } from "react";
import createGlobe from "cobe";
import {
  Sparkles,
  ShieldCheck,
  MapPin,
  ArrowRight,
  Loader2,
  Coins,
  Globe as GlobeIcon,
  Plane,
  Bed,
  CalendarCheck,
  CheckCircle2,
} from "lucide-react";

// --- THE BULLETPROOF GLOBE COMPONENT ---
function TravelGlobe() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    let phi = 0;
    if (!canvasRef.current) return;

    const globe = createGlobe(canvasRef.current, {
      devicePixelRatio: 2,
      width: 1000,
      height: 1000,
      phi: 0,
      theta: 0.3,
      dark: 1,
      diffuse: 1.2,
      mapSamples: 16000,
      mapBrightness: 10,
      baseColor: [0, 0.1, 0.5],
      markerColor: [0.22, 0.82, 0.62],
      glowColor: [0, 0.4, 1],
      markers: [
        { location: [51.5072, -0.1276], size: 0.1 },
        { location: [48.8566, 2.3522], size: 0.08 },
        { location: [40.7128, -74.006], size: 0.1 },
        { location: [35.6762, 139.6503], size: 0.1 },
      ],
      onRender: (state) => {
        state.phi = phi;
        phi += 0.005;
      },
    });

    return () => globe.destroy();
  }, []);

  return (
    <div className="w-full max-w-[600px] aspect-square mx-auto opacity-100">
      <canvas
        ref={canvasRef}
        style={{ width: "100%", height: "100%", contain: "layout paint size" }}
      />
    </div>
  );
}

export default function App() {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [itinerary, setItinerary] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handlePlanTrip = async () => {
    if (!prompt) return;

    setLoading(true);
    setError(null);
    setItinerary(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: prompt }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      setItinerary(data);
    } catch (err: any) {
      console.error("Failed to fetch itinerary:", err);
      setError(
        "Our AI agent hit a snag. Please check if the server is running."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative isolate min-h-screen w-full bg-[#030712] text-white font-sans selection:bg-blue-500/30 overflow-hidden md:overflow-auto">
      {/* Background Pattern */}
      <div className="absolute inset-0 -z-20 h-full w-full bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:24px_24px] opacity-40 fixed" />

      {/* --- GLOBE POSITIONING --- */}
      <div className="absolute top-1/2 right-[-30%] md:-right-[20%] lg:-right-[15%] xl:-right-[10%] -translate-y-1/2 w-[800px] h-[800px] pointer-events-none -z-10 opacity-30 lg:opacity-100 fixed">
        <TravelGlobe />
      </div>

      <div className="max-w-6xl mx-auto px-6 py-20 relative z-10">
        {/* Nav */}
        <nav className="flex justify-between items-center mb-24">
          <div className="flex items-center gap-3">
            <img
              src="/logo.png"
              alt="TravelDev Logo"
              className="w-10 h-10 object-contain brightness-110"
            />
            <span className="text-2xl font-black tracking-tighter uppercase">
              Travel<span className="text-blue-500">Dev</span>
            </span>
          </div>
        </nav>

        {/* Hero */}
        <div className="mb-12 max-w-2xl">
          <h1 className="text-7xl md:text-8xl font-black tracking-tighter mb-8 leading-[0.85] text-white">
            Dream it. <br />
            <span className="text-blue-500">We find it.</span> <br />
            <span className="opacity-90 text-5xl md:text-7xl">
              Just 1 click away.
            </span>
          </h1>
          <p className="text-slate-400 text-lg md:text-xl font-medium leading-relaxed">
            Stop searching. Our Agent audits your budget in{" "}
            <span className="text-white font-bold">Euros (€)</span> and builds
            your perfect itinerary instantly.
          </p>
        </div>

        {/* Search Area */}
        <div className="max-w-2xl mb-16">
          <div className="relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-[#39D39F] rounded-3xl blur opacity-30 group-hover:opacity-50 transition duration-1000"></div>
            <div className="relative flex flex-col md:flex-row gap-2 bg-slate-900/80 backdrop-blur-2xl p-3 rounded-3xl border border-white/10 shadow-2xl">
              <div className="flex items-center pl-4 text-slate-500">
                <GlobeIcon size={24} />
              </div>
              <input
                className="flex-1 px-4 py-4 bg-transparent outline-none text-xl text-white placeholder:text-slate-600"
                placeholder="e.g. 5 days in Paris under €2000"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handlePlanTrip()}
              />
              <button
                onClick={handlePlanTrip}
                disabled={loading}
                className="bg-blue-600 text-white px-10 py-5 rounded-2xl font-black hover:bg-blue-500 transition-all flex items-center justify-center gap-2 disabled:bg-blue-800"
              >
                {loading ? (
                  <Loader2 className="animate-spin" size={20} />
                ) : (
                  <>
                    PLAN TRIP <ArrowRight size={20} />
                  </>
                )}
              </button>
            </div>
          </div>
          {error && (
            <div className="mt-4 text-red-400 font-medium px-4">{error}</div>
          )}
        </div>

        {/* --- DYNAMIC CONTENT AREA --- */}
        {!itinerary && !loading && (
          /* Features (Only show when no itinerary is generated) */
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl">
            <div className="p-8 rounded-[2rem] bg-white/5 backdrop-blur-lg border border-white/10">
              <Coins className="text-[#39D39F] mb-4" size={28} />
              <h3 className="font-bold text-xl mb-2">Euro Audit</h3>
              <p className="text-slate-400 text-sm">
                Automatic financial checks ensure every activity fits your €
                budget.
              </p>
            </div>
            <div className="p-8 rounded-[2rem] bg-white/5 backdrop-blur-lg border border-white/10">
              <ShieldCheck className="text-blue-500 mb-4" size={28} />
              <h3 className="font-bold text-xl mb-2">Agent Integrity</h3>
              <p className="text-slate-400 text-sm">
                Advanced reasoning verifies hotel quality and flight
                reliability.
              </p>
            </div>
            <div className="p-8 rounded-[2rem] bg-white/5 backdrop-blur-lg border border-white/10">
              <MapPin className="text-indigo-400 mb-4" size={28} />
              <h3 className="font-bold text-xl mb-2">Smart POIs</h3>
              <p className="text-slate-400 text-sm">
                Localized discovery of hidden gems based on real-time data.
              </p>
            </div>
          </div>
        )}

        {itinerary && (
          /* Agent Results Dashboard */
          <div className="max-w-4xl animate-in fade-in slide-in-from-bottom-10 duration-700 pb-24">
            <div className="flex items-center gap-3 mb-8">
              <Sparkles className="text-blue-400" size={28} />
              <h2 className="text-3xl md:text-5xl font-black tracking-tighter">
                Your Agent's Plan
              </h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Flight Details */}
              <div className="p-6 rounded-[2rem] bg-slate-800/60 backdrop-blur-xl border border-white/10 shadow-xl">
                <div className="flex justify-between items-start mb-4">
                  <div className="p-3 bg-blue-500/20 rounded-xl">
                    <Plane className="text-blue-400" size={24} />
                  </div>
                  <span className="font-black text-xl text-white">
                    ${itinerary.selected_flight?.price_usd}
                  </span>
                </div>
                <h3 className="text-xl font-bold mb-1">
                  {itinerary.selected_flight?.airline}
                </h3>
                <p className="text-slate-400 text-sm mb-4">
                  {itinerary.selected_flight?.duration_hours} Hour Flight •{" "}
                  {itinerary.selected_flight?.stops} Stop(s)
                </p>
              </div>

              {/* Hotel Details */}
              <div className="p-6 rounded-[2rem] bg-slate-800/60 backdrop-blur-xl border border-white/10 shadow-xl">
                <div className="flex justify-between items-start mb-4">
                  <div className="p-3 bg-[#39D39F]/20 rounded-xl">
                    <Bed className="text-[#39D39F]" size={24} />
                  </div>
                  <span className="font-black text-xl text-white">
                    ${itinerary.selected_hotel?.price_per_night_usd}{" "}
                    <span className="text-sm text-slate-400 font-normal">
                      /night
                    </span>
                  </span>
                </div>
                <h3 className="text-xl font-bold mb-1">
                  {itinerary.selected_hotel?.name}
                </h3>
                <p className="text-slate-400 text-sm mb-4">
                  {itinerary.selected_hotel?.location} •{" "}
                  {itinerary.selected_hotel?.rating} Stars
                </p>
              </div>
            </div>

            {/* Budget Status */}
            <div className="mt-4 p-6 rounded-[2rem] bg-slate-800/60 backdrop-blur-xl border border-white/10 shadow-xl flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-indigo-500/20 rounded-xl">
                  <Coins className="text-indigo-400" size={24} />
                </div>
                <div>
                  <h3 className="text-lg font-bold">
                    Total Budget: ${itinerary.budget_usd}
                  </h3>
                  <p className="text-slate-400 text-sm">
                    Status:{" "}
                    {itinerary.within_budget ? "Approved" : "Over Budget"}
                  </p>
                </div>
              </div>
              {itinerary.within_budget && (
                <CheckCircle2 className="text-[#39D39F]" size={32} />
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
