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

// --- DEPARTURE BOARD COMPONENT ---
function DepartureBoard() {
  const [text, setText] = useState("PLANNING");
  const phrases = [
    "ANALYZING",
    "LOCATING",
    "CURATING",
    "JFK → LHR",
    "BOM → DXB",
    "CDG → JFK",
    "SYD → SIN",
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setText(phrases[Math.floor(Math.random() * phrases.length)]);
    }, 600);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center space-y-6">
      <div className="bg-[#0f172a] border-4 border-slate-800 p-6 rounded-xl shadow-[0_0_50px_rgba(0,0,0,0.5)]">
        <div className="flex space-x-2">
          {text
            .padEnd(10, " ")
            .split("")
            .map((char, i) => (
              <div
                key={i}
                className="w-10 h-14 bg-slate-900 border-b-4 border-black flex items-center justify-center text-3xl font-mono font-bold text-blue-400 rounded-md shadow-inner"
              >
                {char}
              </div>
            ))}
        </div>
      </div>
      <div className="flex items-center gap-3 text-blue-400/80 font-mono text-sm tracking-[0.4em] uppercase">
        <Plane size={16} className="animate-bounce" />
        Agent is securing your route
      </div>
    </div>
  );
}

// --- GLOBE COMPONENT (Hardened) ---
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
    if (!canvasRef.current) return;

    const numLat = parseFloat(lat) || 0;
    const numLng = parseFloat(lng) || 0;
    const numOLat = parseFloat(originLat) || 0;
    const numOLng = parseFloat(originLng) || 0;

    const hasDest = numLat !== 0 || numLng !== 0;

    let phi = 0;
    let theta = 0.3;

    const globe = createGlobe(canvasRef.current, {
      devicePixelRatio: 2,
      width: 600 * 2,
      height: 600 * 2,
      phi: 0,
      theta: 0.3,
      dark: 1,
      diffuse: 1.2,
      mapSamples: 16000,
      mapBrightness: 6,
      baseColor: [0.05, 0.15, 0.3],
      markerColor: [0.22, 0.82, 0.62],
      glowColor: [0.1, 0.4, 1],
      markers: [
        { location: [numOLat, numOLng], size: 0.05 },
        { location: [numLat, numLng], size: 0.1 },
      ],
      onRender: (state) => {
        if (hasDest) {
          const targetPhi = (numLng * Math.PI) / 180;
          const targetTheta = (numLat * Math.PI) / 180;
          phi += (targetPhi - phi) * 0.05;
          theta += (targetTheta - theta) * 0.05;
          state.phi = phi + Math.PI;
          state.theta = theta;
        } else {
          state.phi = phi;
          phi += 0.005;
        }
      },
    });

    return () => globe.destroy();
  }, [lat, lng, originLat, originLng]);

  return (
    <div className="flex items-center justify-center w-[600px] h-[600px]">
      <canvas
        ref={canvasRef}
        style={{
          width: "600px",
          height: "600px",
          maxWidth: "100%",
          aspectRatio: "1/1",
        }}
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
  const [bgImage, setBgImage] = useState(
    "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?q=80&w=2021&auto=format&fit=crop"
  );

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

      if (!response.ok) throw new Error("Server Error");
      const data = await response.json();
      setItinerary(data);

      // --- THE IMAGE FETCH FIX ---
      // We check both data.destination AND data.itinerary.destination just in case
      const cityName = data.destination || data.itinerary?.destination;

      console.log("🏙️ AI identified destination as:", cityName);

      if (cityName && cityName !== "Unknown") {
        const accessKey = import.meta.env.VITE_UNSPLASH_ACCESS_KEY;

        // We add 'landscape' and 'travel' to the query to get the best results
        const imgRes = await fetch(
          `https://api.unsplash.com/search/photos?query=${encodeURIComponent(
            cityName
          )}%20scenery%20travel&orientation=landscape&client_id=${accessKey}`
        );
        const imgData = await imgRes.json();

        if (imgData.results && imgData.results.length > 0) {
          const newUrl = imgData.results[0].urls.regular;
          console.log("📸 Success! Changing background to:", newUrl);
          setBgImage(newUrl);
        } else {
          console.warn("⚠️ Unsplash found no photos for:", cityName);
        }
      }
    } catch (err) {
      console.error("❌ Plan Trip Error:", err);
      setError("AI agent snag. Check backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    // FIX: Removed bg-[#030712] here so background image is visible
    <div className="relative min-h-screen w-full text-white font-sans overflow-x-hidden pb-32">
      {/* 1. DYNAMIC BACKGROUND IMAGE (Behind everything) */}
      <div className="fixed inset-0 -z-50 bg-[#030712]">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#030712]/70 to-[#030712] z-10" />
        <img
          key={bgImage}
          src={bgImage}
          className="w-full h-full object-cover opacity-60 transition-all duration-1000 scale-105"
          alt="Backdrop"
        />
      </div>

      {/* 2. PATTERN OVERLAY */}
      <div className="fixed inset-0 -z-40 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:24px_24px] opacity-20 pointer-events-none" />

      {/* 3. LOADING OVERLAY */}
      {loading && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-[#030712]/95 backdrop-blur-xl">
          <div className="relative">
            <div className="absolute -inset-24 bg-blue-600/20 blur-[120px] rounded-full animate-pulse" />
            <DepartureBoard />
          </div>
        </div>
      )}

      {/* --- GLOBE (Nuclear Positioning Fix) --- */}
      <div className="fixed top-1/2 right-[-10%] md:right-[0%] -translate-y-1/2 w-[600px] h-[600px] md:w-[800px] md:h-[800px] pointer-events-none -z-10 opacity-80 transition-all duration-1000 flex items-center justify-center">
        <TravelGlobe
          lat={itinerary?.destination_lat}
          lng={itinerary?.destination_lng}
          originLat={itinerary?.origin_lat}
          originLng={itinerary?.origin_lng}
        />
      </div>

      <div className="max-w-6xl mx-auto px-6 py-20 relative z-10">
        <nav className="mb-24 flex items-center gap-3">
          <img
            src="/logo.png"
            alt="Logo"
            className="w-10 h-10 object-contain"
          />
          <span className="text-2xl font-black tracking-tighter uppercase">
            Travel<span className="text-blue-500">Dev</span>
          </span>
        </nav>

        <div className="mb-12 max-w-2xl">
          <h1 className="text-7xl md:text-8xl font-black tracking-tighter mb-8 leading-[0.85]">
            Dream it. <br />
            <span className="text-blue-500">We find it.</span>
          </h1>
          <p className="text-slate-400 text-lg md:text-xl max-w-lg font-medium">
            Next-gen travel intelligence. We audit budgets, find flights, and
            map your journey in 3D.
          </p>
        </div>

        {/* Search Section */}
        <div className="max-w-3xl mb-16 relative group">
          <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-[#39D39F] rounded-3xl blur opacity-25" />
          <div className="relative flex flex-col md:flex-row bg-slate-900/90 backdrop-blur-3xl p-2 rounded-3xl border border-white/10 shadow-2xl md:divide-x divide-white/10">
            <div className="flex items-center flex-1 px-4 py-3">
              <MapPin size={20} className="text-blue-400 mr-3" />
              <input
                className="w-full bg-transparent outline-none text-white placeholder:text-slate-500"
                placeholder="Leaving from..."
                value={origin}
                onChange={(e) => setOrigin(e.target.value)}
              />
            </div>
            <div className="flex items-center flex-[1.5] px-4 py-3">
              <GlobeIcon size={20} className="text-[#39D39F] mr-3" />
              <input
                className="w-full bg-transparent outline-none text-white placeholder:text-slate-500"
                placeholder="5 days in Tokyo under €2500"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handlePlanTrip()}
              />
            </div>
            <button
              onClick={handlePlanTrip}
              disabled={loading}
              className="bg-blue-600 text-white px-8 py-4 rounded-2xl font-black hover:bg-blue-500 transition-all ml-2 shadow-lg active:scale-95"
            >
              PLAN TRIP
            </button>
          </div>
          {error && (
            <div className="mt-4 text-red-400 font-medium px-4">{error}</div>
          )}
        </div>

        {/* Results Section */}
        {itinerary && (
          <div className="max-w-4xl animate-in fade-in slide-in-from-bottom-10 duration-700">
            <div className="inline-flex items-center gap-2 px-6 py-2 rounded-full bg-blue-500/20 border border-blue-500/40 text-blue-300 font-bold text-sm uppercase mb-8 shadow-xl backdrop-blur-md">
              <MapPin size={16} /> {itinerary.destination}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
              <div className="p-8 rounded-[2.5rem] bg-slate-900/60 backdrop-blur-2xl border border-white/10 shadow-2xl">
                <Plane className="text-blue-400 mb-4" size={32} />
                <h3 className="text-slate-500 uppercase text-[10px] font-black tracking-[0.2em] mb-1">
                  Inbound Flight
                </h3>
                <h4 className="font-bold text-xl mb-2 text-white">
                  {itinerary.selected_flight?.airline ||
                    "Flight Research Completed"}
                </h4>
                <p className="text-4xl font-black text-white">
                  ${itinerary.selected_flight?.price_usd || "0"}
                </p>
              </div>

              <div className="p-8 rounded-[2.5rem] bg-slate-900/60 backdrop-blur-2xl border border-white/10 shadow-2xl">
                <Bed className="text-[#39D39F] mb-4" size={32} />
                <h3 className="text-slate-500 uppercase text-[10px] font-black tracking-[0.2em] mb-1">
                  Recommended Stay
                </h3>
                <h4 className="font-bold text-xl mb-2 text-white">
                  {itinerary.selected_hotel?.name || "Curated Accommodation"}
                </h4>
                <p className="text-4xl font-black text-white">
                  ${itinerary.selected_hotel?.price_per_night_usd || "0"}
                  <span className="text-sm font-normal text-slate-500">
                    /night
                  </span>
                </p>
              </div>
            </div>

            <div className="mt-12 space-y-12">
              <h3 className="text-3xl font-black tracking-tight mb-8 border-b border-white/10 pb-4 italic">
                The Itinerary
              </h3>
              {itinerary.itinerary?.days?.map((day: any, i: number) => (
                <div
                  key={i}
                  className="border-l-4 border-blue-500/30 pl-8 relative pb-6"
                >
                  <div className="absolute -left-[10px] top-0 w-4 h-4 rounded-full bg-blue-500 shadow-[0_0_20px_rgba(59,130,246,0.8)]" />
                  <div className="mb-6">
                    <span className="text-blue-400 font-black text-xs uppercase tracking-widest">
                      Day {day.day}
                    </span>
                    <h4 className="text-3xl font-bold text-white leading-tight">
                      {day.theme}
                    </h4>
                  </div>
                  <div className="grid gap-4">
                    {day.activities.map((act: any, j: number) => (
                      <div
                        key={j}
                        className="bg-white/5 border border-white/5 p-5 rounded-3xl flex items-center justify-between hover:bg-white/10 transition-all border-l-4 border-l-transparent hover:border-l-blue-500"
                      >
                        <div className="flex items-center gap-5">
                          <div className="w-12 h-12 rounded-2xl bg-slate-800 flex items-center justify-center text-slate-500 shadow-inner">
                            <Clock size={20} />
                          </div>
                          <div>
                            <p className="text-[10px] text-slate-500 font-mono uppercase tracking-widest mb-1">
                              {act.time}
                            </p>
                            <p className="font-bold text-slate-100 text-lg">
                              {act.name}
                            </p>
                          </div>
                        </div>
                        <span className="text-[#39D39F] font-black text-xl bg-[#39D39F]/10 px-4 py-1 rounded-xl border border-[#39D39F]/20">
                          ${act.cost_usd}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Feature Cards (Initial View) */}
        {!itinerary && !loading && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl">
            <div className="p-10 rounded-[3rem] bg-white/5 backdrop-blur-xl border border-white/10 hover:bg-white/10 transition-all">
              <Coins className="text-[#39D39F] mb-6" size={32} />
              <h3 className="font-bold text-2xl mb-3">Euro Audit</h3>
              <p className="text-slate-400 leading-relaxed">
                AI performs real-time financial vetting against live exchange
                rates and local costs.
              </p>
            </div>
            <div className="p-10 rounded-[3rem] bg-white/5 backdrop-blur-xl border border-white/10 hover:bg-white/10 transition-all">
              <ShieldCheck className="text-blue-500 mb-6" size={32} />
              <h3 className="font-bold text-2xl mb-3">Verification</h3>
              <p className="text-slate-400 leading-relaxed">
                Cross-references hotel ratings and flight reliability to ensure
                premium travel standards.
              </p>
            </div>
            <div className="p-10 rounded-[3rem] bg-white/5 backdrop-blur-xl border border-white/10 hover:bg-white/10 transition-all">
              <MapPin className="text-indigo-400 mb-6" size={32} />
              <h3 className="font-bold text-2xl mb-3">Smart POIs</h3>
              <p className="text-slate-400 leading-relaxed">
                Discovers hidden gems and local landmarks using real-world
                spatial intelligence.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
