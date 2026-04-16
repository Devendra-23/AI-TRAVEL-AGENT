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
  Sparkles,
} from "lucide-react";

// --- HELPER: UNIFORM DATE FORMATTING ---
const formatDate = (dateStr: string) => {
  if (!dateStr || dateStr === "None") return "";
  const [y, m, d] = dateStr.split("-");
  return `${d}/${m}/${y.slice(-2)}`;
};

// --- DEPARTURE BOARD LOADING ---
function DepartureBoard() {
  const [text, setText] = useState("PLANNING");
  const phrases = [
    "ANALYSING",
    "LOCATING",
    "CURATING",
    "BOM → POZ",
    "NCL → BRS",
    "LHR → ODS",
    "HEL → BZG",
    "OSLO → LIS",
    "CDG → ARN",
    "LHR → MAD",
    "HEL → CDG",
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setText(phrases[Math.floor(Math.random() * phrases.length)]);
    }, 600);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-[#030712]/95 backdrop-blur-xl px-4">
      <div className="flex flex-col items-center justify-center space-y-6 w-full max-w-md">
        <div className="bg-[#0f172a] border-2 md:border-4 border-slate-800 p-4 md:p-6 rounded-xl shadow-[0_0_50px_rgba(0,0,0,0.5)] w-full overflow-hidden">
          <div className="flex justify-center space-x-1 md:space-x-2">
            {text
              .padEnd(10, " ")
              .split("")
              .map((char, i) => (
                <div
                  key={i}
                  className="w-8 h-10 md:w-10 md:h-14 bg-slate-900 border-b-2 md:border-b-4 border-black flex items-center justify-center text-xl md:text-3xl font-mono font-bold text-blue-400 rounded-md shadow-inner"
                >
                  {char}
                </div>
              ))}
          </div>
        </div>
        <div className="flex items-center gap-3 text-blue-400/80 font-mono text-[10px] md:text-sm tracking-[0.2em] md:tracking-[0.4em] uppercase">
          <Plane size={16} className="animate-bounce" /> Securing your route
        </div>
      </div>
    </div>
  );
}

// --- GLOBE COMPONENT ---
function TravelGlobe({ lat, lng, originLat, originLng }: any) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [size, setSize] = useState(window.innerWidth < 768 ? 350 : 600);

  useEffect(() => {
    const handleResize = () => setSize(window.innerWidth < 768 ? 350 : 600);
    window.addEventListener("resize", handleResize);
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
    const globe = createGlobe(canvasRef.current, {
      devicePixelRatio: 2,
      width: size * 2,
      height: size * 2,
      phi: 0,
      theta: 0.3,
      dark: 1,
      diffuse: 1.2,
      mapSamples: 12000,
      mapBrightness: 6,
      baseColor: [0.05, 0.15, 0.3],
      markerColor: [0.22, 0.82, 0.62],
      glowColor: [0.1, 0.4, 1],
      markers: markers,
      onRender: (state) => {
        state.phi = phi;
        phi += 0.005;
      },
    });
    return () => {
      globe.destroy();
      window.removeEventListener("resize", handleResize);
    };
  }, [lat, lng, originLat, originLng, size]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        width: size,
        height: size,
        maxWidth: "100%",
        aspectRatio: "1/1",
      }}
    />
  );
}

export default function App() {
  const today = new Date().toISOString().split("T")[0];
  const [prompt, setPrompt] = useState("");
  const [startDate, setStartDate] = useState(today);
  const [endDate, setEndDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [itinerary, setItinerary] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const DEFAULT_BG =
    "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?q=80&w=2021&auto=format&fit=crop";
  const [bgImages, setBgImages] = useState<string[]>([DEFAULT_BG]);
  const [currentBgIdx, setCurrentBgIdx] = useState(0);

  useEffect(() => {
    if (bgImages.length <= 1) return;
    const timer = setInterval(
      () => setCurrentBgIdx((p) => (p + 1) % bgImages.length),
      7000
    );
    return () => clearInterval(timer);
  }, [bgImages]);

  const handleReset = () => {
    setItinerary(null);
    setPrompt("");
    setError(null);
    setEndDate("");
    setBgImages([DEFAULT_BG]);
    setCurrentBgIdx(0);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const days = useMemo(() => {
    if (!itinerary) return [];

    // The backend now safely wraps everything in the 'itinerary' key
    const base = itinerary.itinerary;

    if (base && Array.isArray(base.days)) {
      return base.days;
    }
    if (Array.isArray(base)) {
      return base;
    }

    return [];
  }, [itinerary]);

  const hotelTiers = useMemo(() => itinerary?.hotels || [], [itinerary]);

  // --- NEW: LOCATION INTELLIGENCE ---
  const detectLocation = () => {
    if (!navigator.geolocation) return;
    setLoading(true);
    navigator.geolocation.getCurrentPosition(async (pos) => {
      try {
        const res = await fetch(
          `https://nominatim.openstreetmap.org/reverse?format=json&lat=${pos.coords.latitude}&lon=${pos.coords.longitude}`
        );
        const data = await res.json();
        const city =
          data.address.city || data.address.town || data.address.state;
        if (city) setPrompt(`From ${city} to `);
      } catch (e) {
        setError("Could not detect location automatically.");
      } finally {
        setLoading(false);
      }
    });
  };

  const handlePlanTrip = async (isRegenerate = false) => {
    if (!prompt || prompt.length < 5) {
      setError("Please describe your journey (e.g. 'London to Dublin').");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const apiUrl =
        import.meta.env.VITE_API_URL ||
        "https://backend-red-meadow-8440.fly.dev";

      const payload = {
        prompt: isRegenerate
          ? `${prompt} (Suggest a different set of activities)`
          : prompt,
        start_date: startDate,
        end_date: endDate || startDate,
      };

      const res = await fetch(`${apiUrl}/plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data = await res.json();

      // Check for Backend-defined Intelligence Errors
      if (data.errors && data.errors.length > 0) {
        setError(data.errors[0]);
        setItinerary(null);
      } else {
        setItinerary(data);
        if (data.destination) updateBackground(data.destination);
      }
    } catch (err: any) {
      setError(`Connection failed. Error: ${err.message}`);
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
        )}%20landmark&client_id=${accessKey}&per_page=5&orientation=landscape`
      );
      const data = await res.json();
      if (data.results?.length > 0) {
        setBgImages(data.results.map((r: any) => r.urls.regular));
        setCurrentBgIdx(0);
      }
    } catch (err) {}
  };

  return (
    <div className="relative min-h-screen w-full text-white font-sans overflow-x-hidden pb-20">
      <div className="fixed inset-0 -z-50 bg-[#030712] overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#030712]/80 to-[#030712] z-10" />
        {bgImages.map((img, idx) => (
          <img
            key={img}
            src={img}
            className={`absolute inset-0 w-full h-full object-cover transition-all duration-[3000ms] ease-in-out ${
              idx === currentBgIdx
                ? "opacity-40 scale-105"
                : "opacity-0 scale-110"
            }`}
            alt="Backdrop"
          />
        ))}
      </div>

      {loading && <DepartureBoard />}

      <div className="fixed top-[60%] md:top-1/2 right-1/2 translate-x-1/2 md:translate-x-0 md:right-[-10%] lg:right-[0%] -translate-y-1/2 pointer-events-none -z-10 opacity-40 md:opacity-60 flex items-center justify-center">
        <TravelGlobe
          key={`${itinerary?.destination || "idle"}`}
          lat={itinerary?.destination_lat}
          lng={itinerary?.destination_lng}
          originLat={itinerary?.origin_lat}
          originLng={itinerary?.origin_lng}
        />
      </div>

      <div className="max-w-7xl mx-auto px-4 md:px-8 py-10 md:py-20 relative z-10">
        <nav className="mb-12 md:mb-24 flex items-center gap-4">
          <div className="relative w-10 h-10 md:w-12 md:h-12 bg-blue-600 rounded-xl flex items-center justify-center overflow-hidden">
            <img
              src="/logo.png"
              alt="TravelDev Logo"
              className="w-full h-full object-contain p-1.5"
            />
          </div>
          <span className="text-xl md:text-2xl font-black tracking-tighter uppercase leading-none">
            Travel<span className="text-blue-500">Dev</span>
          </span>
        </nav>

        <div className="mb-10 md:mb-12 text-left">
          <h1 className="text-5xl sm:text-6xl md:text-8xl font-black tracking-tighter mb-6 leading-[0.9]">
            Dream it. <br />
            <span className="text-blue-500">We find it.</span>
          </h1>
          <p className="text-lg md:text-2xl font-bold">
            Travel at the speed of thought.{" "}
            <span className="text-slate-300 font-medium italic block md:inline">
              Powered by Agentic Intelligence.
            </span>
          </p>
        </div>

        <div className="max-w-5xl mb-12 md:mb-16 relative group">
          <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-[#39D39F] rounded-2xl md:rounded-3xl blur opacity-25" />
          <div className="relative flex flex-col lg:flex-row bg-slate-900/90 backdrop-blur-3xl p-2 rounded-2xl md:rounded-3xl border border-white/10 shadow-2xl items-stretch divide-y lg:divide-y-0 lg:divide-x divide-white/10">
            <div className="flex items-center flex-1 px-4 md:px-6 py-4 md:py-5">
              <button
                onClick={detectLocation}
                title="Detect my location"
                className="hover:scale-125 transition-transform text-[#39D39F] mr-3 shrink-0"
              >
                <Sparkles size={20} />
              </button>
              <input
                className="w-full bg-transparent outline-none text-sm font-bold placeholder:text-slate-500"
                placeholder="Where to? (e.g. Ireland to Spain...)"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
              />
            </div>
            <div className="flex items-center px-4 md:px-6 py-4 md:py-5 min-w-full lg:min-w-[320px]">
              <Calendar size={20} className="text-blue-400 mr-3 shrink-0" />
              <div className="flex items-center gap-2 w-full">
                <input
                  type="date"
                  min={today}
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="bg-transparent text-[10px] md:text-sm font-black outline-none cursor-pointer hover:text-blue-400"
                />
                <ArrowRight size={12} className="text-slate-600" />
                <input
                  type="date"
                  min={startDate || today}
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="bg-transparent text-[10px] md:text-sm font-black outline-none cursor-pointer hover:text-blue-400"
                />
              </div>
            </div>
            <button
              onClick={() => handlePlanTrip(false)}
              className="bg-blue-600 px-8 lg:px-12 py-4 rounded-xl md:rounded-2xl font-black hover:bg-blue-500 transition-all uppercase text-xs m-1 md:m-2"
            >
              PLAN
            </button>
          </div>
          {error && (
            <p className="text-red-500 bg-red-500/10 border border-red-500/20 px-4 py-2 rounded-xl text-xs mt-4 font-bold animate-pulse">
              {error}
            </p>
          )}
        </div>

        {itinerary && (
          <div className="max-w-5xl animate-in fade-in slide-in-from-bottom-4 duration-1000 relative z-20">
            <div className="flex justify-between items-center mb-10 bg-slate-900/40 p-4 rounded-2xl border border-white/5 backdrop-blur-md">
              <span className="px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest bg-blue-600 text-white">
                Journey Verified
              </span>
              <button
                onClick={handleReset}
                className="text-[11px] font-black uppercase tracking-widest flex items-center gap-2 text-slate-400 hover:text-white"
              >
                Start New Journey{" "}
                <ArrowRight size={14} className="rotate-180" />
              </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
              <div className="lg:col-span-2">
                <div className="p-8 rounded-[2rem] bg-slate-900/60 backdrop-blur-3xl border border-white/10 shadow-2xl h-full flex flex-col justify-between">
                  <div className="flex flex-col sm:flex-row justify-between items-start gap-6">
                    <div>
                      <span className="text-[10px] font-black text-blue-400 uppercase tracking-widest bg-blue-400/10 px-3 py-1 rounded-full border border-blue-400/20">
                        Verified GDS Fare
                      </span>
                      <h4 className="text-2xl md:text-5xl font-black text-white mt-4 tracking-tighter uppercase">
                        {itinerary.selected_flight?.airline || "Global Carrier"}
                      </h4>
                    </div>
                    <div className="w-full sm:w-auto bg-slate-950/50 p-5 rounded-2xl border border-white/5">
                      <div className="flex justify-between gap-12 mb-4">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center">
                            <Plane
                              size={14}
                              className="text-blue-400 rotate-45"
                            />
                          </div>
                          <span className="text-[10px] font-black text-slate-500 uppercase">
                            Outbound
                          </span>
                        </div>
                        <span className="font-black text-xl">
                          €{itinerary.selected_flight?.outbound_price}
                        </span>
                      </div>
                      <div className="w-full h-[1px] bg-white/5 mb-4" />
                      <div className="flex justify-between gap-12">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center">
                            <Plane
                              size={14}
                              className="text-blue-400 rotate-[225deg]"
                            />
                          </div>
                          <span className="text-[10px] font-black text-slate-500 uppercase">
                            Return
                          </span>
                        </div>
                        <span className="font-black text-xl">
                          €{itinerary.selected_flight?.return_price}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="mt-8 flex justify-between items-end border-t border-white/5 pt-6">
                    <div>
                      <p className="text-xs text-slate-500 font-black uppercase mb-1">
                        Fare Total
                      </p>
                      <p className="text-5xl md:text-7xl font-black text-white tracking-tighter">
                        €{itinerary.selected_flight?.price_eur}
                      </p>
                    </div>
                    <p className="text-[10px] font-mono font-bold text-slate-400 bg-white/5 px-4 py-2 rounded-lg">
                      {formatDate(itinerary.start_date)} —{" "}
                      {formatDate(itinerary.end_date)}
                    </p>
                  </div>
                </div>
              </div>

              <div className="rounded-[2rem] border border-white/10 bg-slate-900/60 p-8">
                <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                  <Bed className="text-blue-500" size={18} /> Property Tier
                </h3>
                <div className="space-y-3">
                  {hotelTiers.map((hotel: any, idx: number) => (
                    <div
                      key={idx}
                      className={`p-4 rounded-xl border transition-all ${
                        idx === 0
                          ? "bg-blue-600/20 border-blue-500/50"
                          : "bg-white/5 border-white/10"
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <p className="font-bold text-xs md:text-sm line-clamp-1">
                          {hotel.name}
                        </p>
                      </div>
                      <div className="flex justify-between mt-1">
                        <span className="text-[10px] font-black text-blue-400 uppercase">
                          {hotel.label}
                        </span>
                        <p className="font-black text-[#39D39F] text-xs">
                          €{hotel.price_per_night_eur}
                          <span className="opacity-40">/nt</span>
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="bg-[#39D39F]/10 border border-[#39D39F]/20 rounded-[2rem] p-10 mb-12 flex flex-col md:flex-row justify-between items-center gap-6">
              <div className="max-w-md">
                <h3 className="text-[#39D39F] font-mono text-sm uppercase tracking-[0.4em] mb-3 flex items-center gap-2">
                  <ShieldCheck size={20} /> Integrity: Verified
                </h3>
                <p className="text-slate-400 text-sm font-medium">
                  Real-time GDS fares and property auditing for{" "}
                  {itinerary.destination}.
                </p>
              </div>
              <div className="text-right">
                <p className="text-5xl md:text-7xl font-black tracking-tighter">
                  €{itinerary.total_cost_eur}
                </p>
                <p className="text-blue-400 text-[10px] font-black uppercase tracking-[0.3em]">
                  Estimated Journey Total
                </p>
              </div>
            </div>

            <div className="mt-20 space-y-20">
              <div className="flex justify-between items-end border-b border-white/10 pb-6 mb-10">
                <h3 className="text-2xl md:text-4xl font-black tracking-tight italic uppercase flex items-center gap-3">
                  <Clock className="text-blue-500" /> AI Suggested Itinerary
                </h3>
                <button
                  onClick={() => handlePlanTrip(true)}
                  className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 text-[10px] font-black uppercase tracking-widest hover:bg-blue-600 transition-all"
                >
                  <Sparkles size={14} className="text-[#39D39F]" /> Regenerate
                </button>
              </div>
              {days.map((day: any, i: number) => (
                <div
                  key={i}
                  className="border-l-4 border-blue-500/20 pl-10 relative pb-10"
                >
                  <div className="absolute -left-[10px] top-0 w-4 h-4 rounded-full bg-blue-500 shadow-xl shadow-blue-500/50" />
                  <div className="mb-8">
                    <span className="text-blue-500 font-black text-[10px] uppercase tracking-widest bg-blue-500/10 px-4 py-2 rounded-lg">
                      Day {day.day || i + 1}
                    </span>
                    <h4 className="text-3xl md:text-5xl font-black mt-4 tracking-tighter leading-none">
                      {day.theme}
                    </h4>
                  </div>
                  <div className="relative flex flex-col items-center justify-center w-full h-32 md:h-44 bg-slate-900/80 border border-white/10 rounded-[2rem] mb-10 overflow-hidden">
                    <div className="relative z-10 flex flex-col items-center gap-3">
                      <div className="w-12 h-12 bg-blue-600 rounded-2xl flex items-center justify-center">
                        <MapPin size={24} className="text-white" />
                      </div>
                      <p className="text-[10px] font-black uppercase tracking-[0.2em] text-blue-400">
                        Spatial Intelligence
                      </p>
                      <h5 className="text-sm md:text-xl font-black tracking-tighter uppercase">
                        VIEW DAY {day.day || i + 1} ON INTERACTIVE MAP
                      </h5>
                    </div>
                  </div>
                  <div className="grid gap-6">
                    {(day.activities || []).map((act: any, j: number) => (
                      <div
                        key={j}
                        className="bg-white/5 border border-white/5 p-8 rounded-[2rem] flex flex-col sm:flex-row justify-between items-center gap-4 hover:bg-white/10 transition-all"
                      >
                        <div className="flex items-center gap-6">
                          <div className="w-12 h-12 md:w-16 md:h-16 rounded-2xl bg-slate-800 flex items-center justify-center text-slate-500">
                            <Clock size={24} />
                          </div>
                          <div>
                            <p className="text-[10px] text-blue-400/60 font-black uppercase mb-1">
                              {act.time}
                            </p>
                            <p className="font-black text-lg md:text-2xl tracking-tighter">
                              <a
                                href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
                                  act.name + " " + itinerary?.destination
                                )}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="font-black text-lg md:text-2xl tracking-tighter hover:text-blue-400 hover:underline transition-colors flex items-center gap-2 cursor-pointer"
                                title="View on Google Maps"
                              >
                                {act.name}{" "}
                                <MapPin
                                  size={18}
                                  className="inline-block text-blue-500 opacity-60"
                                />
                              </a>
                            </p>
                          </div>
                        </div>
                        <span className="text-[#39D39F] font-black text-2xl md:text-4xl tracking-tighter">
                          €{act.cost_eur}
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
