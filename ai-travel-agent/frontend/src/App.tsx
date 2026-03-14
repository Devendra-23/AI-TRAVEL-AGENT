import React, { useState, useEffect, useRef } from "react";
import createGlobe from "cobe";
import {
  Sparkles,
  ShieldCheck,
  MapPin,
  ArrowRight,
  Coins,
  Globe as GlobeIcon,
  Plane,
  Bed,
  CheckCircle2,
  Clock,
  Ticket,
} from "lucide-react";

// --- THE BULLETPROOF GLOBE COMPONENT (Now with 2 Pins!) ---
function TravelGlobe({
  lat,
  lng,
  originLat,
  originLng,
}: {
  lat?: any;
  lng?: any;
  originLat?: any;
  originLng?: any;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    let phi = 0;
    let currentTheta = 0.3;
    if (!canvasRef.current) return;

    // DEBUG: Check if data is arriving
    console.log(
      "📍 Globe Received - Dest:",
      lat,
      lng,
      "Origin:",
      originLat,
      originLng
    );

    const numLat = parseFloat(lat);
    const numLng = parseFloat(lng);
    const numOLat = parseFloat(originLat);
    const numOLng = parseFloat(originLng);

    const hasDest = !isNaN(numLat) && !isNaN(numLng) && numLat !== 0;
    const hasOrigin = !isNaN(numOLat) && !isNaN(numOLng) && numOLat !== 0;

    // BUILD THE MARKERS ARRAY
    let dynamicMarkers = [];

    // Add Origin Pin (Slightly smaller, maybe a different color?)
    if (hasOrigin) {
      dynamicMarkers.push({
        location: [numOLat, numOLng],
        size: 0.08,
        color: [0.4, 0.7, 1], // Light Blue for Origin
      });
    }

    // Add Destination Pin (Large & Bright Green/Teal)
    if (hasDest) {
      dynamicMarkers.push({
        location: [numLat, numLng],
        size: 0.15,
        color: [0.22, 0.82, 0.62],
      });
    }

    // Default markers if no data yet
    if (dynamicMarkers.length === 0) {
      dynamicMarkers = [
        { location: [51.5072, -0.1276], size: 0.05 },
        { location: [40.7128, -74.006], size: 0.05 },
      ];
    }

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
      markers: dynamicMarkers,
      onRender: (state) => {
        if (hasDest) {
          const targetPhi = (numLng * Math.PI) / 180;
          const targetTheta = (numLat * Math.PI) / 180;
          phi += (targetPhi - phi) * 0.05;
          currentTheta += (targetTheta - currentTheta) * 0.05;
          state.phi = phi + Math.PI;
          state.theta = currentTheta;
        } else {
          state.phi = phi;
          phi += 0.005;
        }
      },
    });

    return () => globe.destroy();
  }, [lat, lng, originLat, originLng]);

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
  const [origin, setOrigin] = useState("");
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [itinerary, setItinerary] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handlePlanTrip = async () => {
    if (!prompt) return;

    setLoading(true);
    setError(null);
    setItinerary(null);

    const combinedPrompt = origin ? `From ${origin}: ${prompt}` : prompt;

    try {
      const response = await fetch("http://localhost:8000/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: combinedPrompt }),
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
    <div className="relative isolate min-h-screen w-full bg-[#030712] text-white font-sans selection:bg-blue-500/30 overflow-hidden md:overflow-auto pb-32">
      <style>{`
        @keyframes fly {
          0% { transform: translateX(-150%) translateY(10px) rotate(-15deg); opacity: 0; }
          20% { opacity: 1; transform: translateX(-50%) translateY(0px) rotate(0deg); }
          80% { opacity: 1; transform: translateX(50%) translateY(0px) rotate(0deg); }
          100% { transform: translateX(150%) translateY(-10px) rotate(15deg); opacity: 0; }
        }
        .animate-fly {
          animation: fly 2s infinite ease-in-out;
        }
      `}</style>

      {/* Background Pattern */}
      <div className="absolute inset-0 -z-20 h-full w-full bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:24px_24px] opacity-40 fixed" />

      {/* --- GLOBE POSITIONING --- */}
      <div className="absolute top-1/2 right-[-30%] md:-right-[20%] lg:-right-[15%] xl:-right-[10%] -translate-y-1/2 w-[800px] h-[800px] pointer-events-none -z-10 opacity-30 lg:opacity-100 fixed transition-all duration-1000">
        <TravelGlobe
          lat={itinerary?.destination_lat}
          lng={itinerary?.destination_lng}
          // --- NEW: Pass origin coords down to the globe! ---
          originLat={itinerary?.origin_lat}
          originLng={itinerary?.origin_lng}
        />
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

        {/* Split Search Area */}
        <div className="max-w-3xl mb-16">
          <div className="relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-[#39D39F] rounded-3xl blur opacity-30 group-hover:opacity-50 transition duration-1000"></div>

            <div className="relative flex flex-col md:flex-row bg-slate-900/80 backdrop-blur-2xl p-2 rounded-3xl border border-white/10 shadow-2xl md:divide-x divide-white/10">
              {/* Origin Input */}
              <div className="flex items-center flex-1 px-4 py-3 md:py-0">
                <MapPin size={22} className="text-blue-400 mr-3 shrink-0" />
                <input
                  className="w-full bg-transparent outline-none text-lg text-white placeholder:text-slate-500"
                  placeholder="Leaving from..."
                  value={origin}
                  onChange={(e) => setOrigin(e.target.value)}
                />
              </div>

              {/* Destination Input */}
              <div className="flex items-center flex-[1.5] px-4 py-3 md:py-0">
                <GlobeIcon size={22} className="text-[#39D39F] mr-3 shrink-0" />
                <input
                  className="w-full bg-transparent outline-none text-lg text-white placeholder:text-slate-500"
                  placeholder="e.g. 5 days in Poland under €2000"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handlePlanTrip()}
                />
              </div>

              {/* Submit Button */}
              <button
                onClick={handlePlanTrip}
                disabled={loading}
                className="bg-blue-600 text-white px-8 py-4 rounded-2xl font-black hover:bg-blue-500 transition-all flex items-center justify-center gap-2 disabled:bg-blue-800 overflow-hidden relative min-w-[160px] ml-2 mt-2 md:mt-0"
              >
                {loading ? (
                  <div className="absolute inset-0 flex items-center justify-center w-full h-full">
                    <Plane className="animate-fly text-white" size={24} />
                  </div>
                ) : (
                  <span className="flex items-center gap-2">
                    PLAN TRIP <ArrowRight size={20} />
                  </span>
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
          <div className="max-w-4xl animate-in fade-in slide-in-from-bottom-10 duration-700">
            <div className="flex items-center gap-3 mb-8">
              <Sparkles className="text-blue-400" size={28} />
              <h2 className="text-3xl md:text-5xl font-black tracking-tighter">
                Your Agent's Plan
              </h2>
            </div>

            {/* Top Cards: Flight & Hotel */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div className="p-6 rounded-[2rem] bg-slate-800/60 backdrop-blur-xl border border-white/10 shadow-xl hover:border-blue-500/50 transition-colors">
                <div className="flex justify-between items-start mb-4">
                  <div className="p-3 bg-blue-500/20 rounded-xl">
                    <Plane className="text-blue-400" size={24} />
                  </div>
                  <span className="font-black text-xl text-white">
                    ${itinerary.selected_flight?.price_usd}
                  </span>
                </div>
                <h3 className="text-xl font-bold mb-1">
                  {itinerary.selected_flight?.airline || "Flight Details"}
                </h3>
                <p className="text-slate-400 text-sm mb-4">
                  {itinerary.selected_flight?.duration_hours
                    ? `${itinerary.selected_flight.duration_hours} Hour Flight • `
                    : ""}
                  {itinerary.selected_flight?.stops !== undefined
                    ? `${itinerary.selected_flight.stops} Stop(s)`
                    : "Direct"}
                </p>
              </div>

              <div className="p-6 rounded-[2rem] bg-slate-800/60 backdrop-blur-xl border border-white/10 shadow-xl hover:border-[#39D39F]/50 transition-colors">
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
                  {itinerary.selected_hotel?.name || "Accommodation"}
                </h3>
                <p className="text-slate-400 text-sm mb-4">
                  {itinerary.selected_hotel?.location || "City Center"} •{" "}
                  {itinerary.selected_hotel?.rating || "4.0"} Stars
                </p>
              </div>
            </div>

            {/* Budget Status */}
            <div className="mb-12 p-6 rounded-[2rem] bg-slate-800/60 backdrop-blur-xl border border-white/10 shadow-xl flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-indigo-500/20 rounded-xl">
                  <Coins className="text-indigo-400" size={24} />
                </div>
                <div>
                  <h3 className="text-lg font-bold">
                    Total Budget: ${itinerary.budget_usd || "0"}
                  </h3>
                  <p className="text-slate-400 text-sm">
                    Status:{" "}
                    {itinerary.within_budget ? "Approved" : "Review Needed"}
                  </p>
                </div>
              </div>
              {itinerary.within_budget && (
                <CheckCircle2 className="text-[#39D39F]" size={32} />
              )}
            </div>

            {/* BOARDING PASS TIMELINE */}
            <div className="mt-8">
              <h3 className="text-2xl font-black tracking-tighter mb-8 flex items-center gap-2">
                <Ticket className="text-blue-500" />
                Itinerary Timeline
              </h3>

              <div className="relative border-l-2 border-dashed border-blue-500/30 ml-4 md:ml-6 space-y-12 pb-12">
                {itinerary.itinerary?.days?.map((day: any, index: number) => (
                  <div key={index} className="relative pl-8 md:pl-12">
                    <div className="absolute -left-[11px] top-2 h-5 w-5 rounded-full bg-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.6)] border-4 border-[#030712]" />

                    <div className="mb-4">
                      <span className="text-blue-400 font-bold uppercase tracking-wider text-sm">
                        Day {day.day}
                      </span>
                      <h4 className="text-2xl font-bold text-white">
                        {day.theme || "Exploration & Discovery"}
                      </h4>
                    </div>

                    <div className="space-y-4">
                      {day.activities?.map(
                        (activity: any, actIndex: number) => (
                          <div
                            key={actIndex}
                            className="bg-white/5 border border-white/10 rounded-2xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-white/10 transition-colors"
                          >
                            <div className="flex items-start gap-4">
                              <div className="mt-1 p-2 bg-slate-800 rounded-lg text-slate-400">
                                <Clock size={18} />
                              </div>
                              <div>
                                <p className="text-slate-400 font-mono text-sm mb-1">
                                  {activity.time || "Flexible"}
                                </p>
                                <p className="text-lg font-medium text-white">
                                  {activity.name || "Local Activity"}
                                </p>
                              </div>
                            </div>
                            {activity.cost_usd > 0 ? (
                              <div className="text-right">
                                <span className="bg-[#39D39F]/20 text-[#39D39F] font-bold px-3 py-1 rounded-full text-sm">
                                  ${activity.cost_usd}
                                </span>
                              </div>
                            ) : (
                              <div className="text-right">
                                <span className="bg-slate-700 text-slate-300 font-bold px-3 py-1 rounded-full text-sm">
                                  Free
                                </span>
                              </div>
                            )}
                          </div>
                        )
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
