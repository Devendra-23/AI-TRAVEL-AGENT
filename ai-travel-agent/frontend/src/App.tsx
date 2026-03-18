import React, { useState, useEffect, useRef, useMemo } from "react";
import createGlobe from "cobe";
import {
  MapPin,
  Globe as GlobeIcon,
  Plane,
  Bed,
  Clock,
  ShieldCheck,
  Calendar,
  ArrowRight,
} from "lucide-react";

// --- DEPARTURE BOARD ---
function DepartureBoard() {
  const [text, setText] = useState("PLANNING");
  const phrases = [
    "ANALYSING",
    "LOCATING",
    "CURATING",
    "JFK → LHR",
    "BOM → POZ",
    "STN → ODS",
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
        <Plane size={16} className="animate-bounce" /> Agent is securing your
        route
      </div>
    </div>
  );
}

// --- GLOBE COMPONENT ---
function TravelGlobe({ lat, lng, originLat, originLng }: any) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    const nLat = parseFloat(lat) || 0;
    const nLng = parseFloat(lng) || 0;
    const nOLat = parseFloat(originLat) || 0;
    const nOLng = parseFloat(originLng) || 0;

    const markers =
      nLat !== 0 && nOLat !== 0
        ? [
            { location: [nOLat, nOLng] as [number, number], size: 0.08 },
            { location: [nLat, nLng] as [number, number], size: 0.12 },
          ]
        : [];

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
      markers: markers,
      onRender: (state) => {
        if (markers.length > 0) {
          const targetPhi = (nLng * Math.PI) / 180;
          const targetTheta = (nLat * Math.PI) / 180;
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
  const today = new Date().toISOString().split("T")[0];

  const [origin, setOrigin] = useState("");
  const [prompt, setPrompt] = useState("");
  const [startDate, setStartDate] = useState(today);
  const [endDate, setEndDate] = useState("");
  const [tripType, setTripType] = useState("round-trip");

  const [loading, setLoading] = useState(false);
  const [itinerary, setItinerary] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [bgImage, setBgImage] = useState(
    "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?q=80&w=2021&auto=format&fit=crop"
  );

  const days = useMemo(
    () => itinerary?.itinerary?.days || itinerary?.days || [],
    [itinerary]
  );
  const hotelTiers = useMemo(() => itinerary?.hotels || [], [itinerary]);

  const handlePlanTrip = async () => {
    if (!prompt || !origin) {
      setError("Please enter both origin and destination.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      // Meticulous Prompt construction for the AI agent
      const combinedMessage = `Trip from ${origin} to ${prompt}. Trip type: ${tripType}. Dates: ${startDate} to ${
        endDate || startDate
      }`;

      const res = await fetch("http://localhost:8000/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: combinedMessage,
          start_date: startDate,
          end_date: tripType === "round-trip" ? endDate : startDate,
          trip_type: tripType,
        }),
      });

      if (!res.ok) throw new Error("Server response error");

      const data = await res.json();
      setItinerary(data);
      if (data.destination) updateBackground(data.destination);
    } catch (err) {
      setError("AI agent snagged. Check backend and API connections.");
    } finally {
      setLoading(false);
    }
  };

  const updateBackground = async (query: string) => {
    const accessKey = import.meta.env.VITE_UNSPLASH_ACCESS_KEY;
    if (!accessKey) return;
    try {
      const res = await fetch(
        `https://api.unsplash.com/search/photos?query=${encodeURIComponent(
          query
        )}%20cityscape&client_id=${accessKey}`
      );
      const data = await res.json();
      if (data.results?.[0]) setBgImage(data.results[0].urls.regular);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="relative min-h-screen w-full text-white font-sans overflow-x-hidden pb-32">
      <div className="fixed inset-0 -z-50 bg-[#030712]">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#030712]/70 to-[#030712] z-10" />
        <img
          key={bgImage}
          src={bgImage}
          className="w-full h-full object-cover opacity-60 transition-all duration-1000"
          alt="Backdrop"
        />
      </div>

      {loading && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-[#030712]/95 backdrop-blur-xl">
          <DepartureBoard />
        </div>
      )}

      <div className="fixed top-1/2 right-[-10%] md:right-[0%] -translate-y-1/2 w-[600px] h-[600px] md:w-[800px] md:h-[800px] pointer-events-none -z-10 opacity-60 flex items-center justify-center">
        <TravelGlobe
          key={itinerary?.destination || "idle-globe"}
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
          <span className="text-2xl font-black tracking-tighter uppercase leading-none">
            Travel<span className="text-blue-500">Dev</span>
          </span>
        </nav>

        <div className="mb-12 max-w-2xl">
          <h1 className="text-7xl md:text-8xl font-black tracking-tighter mb-8 leading-[0.85]">
            Dream it. <br />
            <span className="text-blue-500">We find it.</span>
          </h1>
          <p className="text-slate-400 text-lg md:text-xl font-medium tracking-tight">
            Real-time GDS auditing. 3D spatial intelligence.
          </p>
        </div>

        {/* SEARCH SECTION */}
        <div className="max-w-4xl mb-16 relative group">
          <div className="flex gap-4 mb-4">
            {["round-trip", "one-way"].map((type) => (
              <button
                key={type}
                onClick={() => setTripType(type)}
                className={`px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-widest transition-all ${
                  tripType === type
                    ? "bg-blue-600 text-white"
                    : "bg-white/5 text-slate-400"
                }`}
              >
                {type.replace("-", " ")}
              </button>
            ))}
          </div>

          <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-[#39D39F] rounded-3xl blur opacity-25" />
          <div className="relative flex flex-col lg:flex-row bg-slate-900/90 backdrop-blur-3xl p-2 rounded-3xl border border-white/10 shadow-2xl lg:divide-x divide-white/10">
            <div className="flex items-center flex-1 px-4 py-3">
              <MapPin size={20} className="text-blue-400 mr-3" />
              <input
                className="w-full bg-transparent outline-none text-sm"
                placeholder="Origin city..."
                value={origin}
                onChange={(e) => setOrigin(e.target.value)}
              />
            </div>
            <div className="flex items-center flex-1 px-4 py-3">
              <GlobeIcon size={20} className="text-[#39D39F] mr-3" />
              <input
                className="w-full bg-transparent outline-none text-sm"
                placeholder="Destination..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
              />
            </div>

            <div className="flex items-center flex-1 px-4 py-3 min-w-[280px]">
              <Calendar size={20} className="text-blue-400 mr-3" />
              <div className="flex items-center gap-2">
                <input
                  type="date"
                  min={today}
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="bg-transparent text-xs font-bold outline-none cursor-pointer hover:text-blue-400 transition-colors"
                />
                {tripType === "round-trip" && (
                  <>
                    <ArrowRight size={12} className="text-slate-600" />
                    <input
                      type="date"
                      min={startDate || today}
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                      className="bg-transparent text-xs font-bold outline-none cursor-pointer hover:text-blue-400 transition-colors"
                    />
                  </>
                )}
              </div>
            </div>

            <button
              onClick={handlePlanTrip}
              className="bg-blue-600 px-8 py-4 rounded-2xl font-black hover:bg-blue-500 transition-all uppercase text-sm"
            >
              PLAN
            </button>
          </div>
          {error && (
            <p className="text-red-400 text-xs mt-4 ml-4 font-bold">{error}</p>
          )}
        </div>

        {itinerary && (
          <div className="max-w-5xl animate-in fade-in slide-in-from-bottom-4 duration-1000 relative z-20">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
              <div className="lg:col-span-2">
                <div className="p-8 rounded-[2.5rem] bg-slate-900/60 backdrop-blur-3xl border border-white/10 shadow-2xl">
                  <div className="flex justify-between items-start mb-6">
                    <div>
                      <span className="text-[10px] font-black text-blue-400 uppercase tracking-widest bg-blue-400/10 px-3 py-1 rounded-full border border-blue-400/20">
                        {itinerary.trip_type === "round-trip"
                          ? "Round Trip Verified"
                          : "One-Way Secured"}
                      </span>
                      <h4 className="text-2xl font-black text-white mt-4">
                        {itinerary.selected_flight?.airline ||
                          "Checking Carrier..."}
                      </h4>
                    </div>
                    <Plane className="text-blue-400 rotate-45" size={32} />
                  </div>
                  <div className="flex justify-between items-end">
                    <div>
                      <p className="text-sm text-slate-500 font-bold uppercase tracking-tighter">
                        Fare Total
                      </p>
                      <p className="text-5xl font-black text-white leading-none">
                        €{itinerary.selected_flight?.price_eur || "0"}
                      </p>
                    </div>
                    <p className="text-xs text-slate-500 font-mono tracking-widest">
                      {itinerary.start_date}{" "}
                      {itinerary.trip_type === "round-trip" &&
                        `→ ${itinerary.end_date}`}
                    </p>
                  </div>
                </div>
              </div>

              <div className="relative rounded-[2.5rem] overflow-hidden border border-white/10 bg-slate-900/60 backdrop-blur-3xl p-8 flex flex-col justify-between">
                <div>
                  <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                    <Bed className="text-blue-500" size={20} /> Property Tiers
                  </h3>
                  <div className="space-y-3">
                    {hotelTiers.map((hotel: any, idx: number) => (
                      <div
                        key={idx}
                        className={`p-4 rounded-2xl border transition-all ${
                          idx === 0
                            ? "bg-blue-600/20 border-blue-500/50 shadow-lg"
                            : "bg-white/5 border-white/10"
                        }`}
                      >
                        <p className="font-bold text-white text-sm line-clamp-1">
                          {hotel.name}
                        </p>
                        <div className="flex items-center justify-between mt-1">
                          <span className="text-[10px] font-black text-blue-400 uppercase tracking-tighter">
                            {hotel.label || "Option"}
                          </span>
                          <p className="font-black text-[#39D39F] text-sm">
                            €{hotel.price_per_night_eur}
                            <span className="text-[8px] font-normal text-white opacity-40">
                              /nt
                            </span>
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-[#39D39F]/10 border border-[#39D39F]/20 rounded-[3rem] p-10 mb-16 flex flex-col md:flex-row justify-between items-center gap-8 backdrop-blur-md">
              <div className="max-w-md">
                <h3 className="text-[#39D39F] font-mono text-sm uppercase tracking-[0.4em] mb-3 flex items-center gap-2">
                  <ShieldCheck size={20} /> Financial Integrity: Verified
                </h3>
                <p className="text-slate-400 text-sm leading-relaxed font-medium tracking-tight">
                  Total includes real-time data for {itinerary.destination} and
                  categorized property tiers.
                </p>
              </div>
              <div className="text-center md:text-right">
                <p className="text-7xl font-black text-white tracking-tighter mb-1">
                  €{itinerary.total_cost_eur || "0"}
                </p>
                <p className="text-blue-400 text-[10px] font-black uppercase tracking-[0.3em]">
                  Estimated Journey Total
                </p>
              </div>
            </div>

            <div className="mt-12 space-y-16">
              <h3 className="text-4xl font-black tracking-tight mb-12 border-b border-white/10 pb-8 flex items-center gap-4 italic">
                <Clock className="text-blue-500" /> Planned Route
              </h3>
              {days.map((day: any, i: number) => (
                <div
                  key={i}
                  className="border-l-4 border-blue-500/20 pl-10 relative pb-10"
                >
                  <div className="absolute -left-[10px] top-0 w-4 h-4 rounded-full bg-blue-500 shadow-[0_0_20px_rgba(59,130,246,0.5)]" />
                  <div className="mb-8">
                    <span className="text-blue-500 font-black text-[10px] uppercase tracking-[0.2em] bg-blue-500/10 px-3 py-1 rounded-lg">
                      Day {day.day}
                    </span>
                    <h4 className="text-4xl font-bold text-white mt-4 tracking-tight leading-none">
                      {day.theme}
                    </h4>
                  </div>
                  <div className="grid gap-4">
                    {day.activities.map((act: any, j: number) => (
                      <div
                        key={j}
                        className="bg-white/5 border border-white/5 p-6 rounded-[2rem] flex items-center justify-between group hover:bg-white/10 transition-all backdrop-blur-md"
                      >
                        <div className="flex items-center gap-6">
                          <div className="w-12 h-12 rounded-2xl bg-slate-800 flex items-center justify-center text-slate-500 group-hover:text-blue-400 transition-colors shadow-inner">
                            <Clock size={22} />
                          </div>
                          <div>
                            <p className="text-[10px] text-slate-500 font-mono uppercase mb-1 tracking-tighter">
                              {act.time}
                            </p>
                            <p className="font-bold text-slate-100 text-xl tracking-tight leading-none">
                              {act.name}
                            </p>
                          </div>
                        </div>
                        <span className="text-[#39D39F] font-black text-2xl tracking-tighter">
                          €{act.cost_eur || 0}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
