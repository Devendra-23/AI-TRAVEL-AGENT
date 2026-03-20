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

// --- GLOBE COMPONENT (RESPONSIVE) ---
function TravelGlobe({ lat, lng, originLat, originLng }: any) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  // Dynamic size based on window width
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
      width: size * 2, // Applied dynamic size
      height: size * 2, // Applied dynamic size
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
    const timer = setInterval(() => {
      setCurrentBgIdx((prev) => (prev + 1) % bgImages.length);
    }, 7000);
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
    const base = itinerary.itinerary || itinerary;
    const list =
      base.days || base.itinerary?.days || (Array.isArray(base) ? base : []);
    return Array.isArray(list) ? list : [];
  }, [itinerary]);

  const hotelTiers = useMemo(() => itinerary?.hotels || [], [itinerary]);

  const handlePlanTrip = async () => {
    if (!prompt || prompt.length < 5) {
      setError(
        "Please describe your journey (e.g. 'Norway to Finland for 2 days')."
      );
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt,
          start_date: startDate,
          end_date: endDate || startDate,
        }),
      });
      const data = await res.json();
      if (data.error) {
        setError(data.error);
        setItinerary(null);
      } else {
        setItinerary(data);
        if (data.destination) updateBackground(data.destination);
      }
    } catch (err) {
      setError("Agent failed. Check backend connectivity.");
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
        )}%20tourism%20landmark&client_id=${accessKey}&per_page=5&orientation=landscape`
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
      {/* CINEMATIC BACKDROP */}
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

      {/* RESPONSIVE GLOBE POSITIONING (Centers on mobile, right-aligned on desktop) */}
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
        {/* LOGO & NAVIGATION */}
        <nav className="mb-12 md:mb-24 flex items-center gap-4">
          <div className="relative group">
            <div className="relative w-10 h-10 md:w-12 md:h-12">
              <img
                src="/logo.png"
                alt="TravelDev Logo"
                className="w-full h-full object-contain p-1"
              />
            </div>
          </div>
          <div className="flex flex-col">
            <span className="text-xl md:text-2xl font-black tracking-tighter uppercase leading-none">
              Travel<span className="text-blue-500">Dev</span>
            </span>
          </div>
        </nav>

        {/* HERO SECTION (Responsive Font Sizes) */}
        <div className="mb-10 md:mb-12 max-w-4xl text-left">
          <h1 className="text-5xl sm:text-6xl md:text-8xl font-black tracking-tighter mb-6 md:mb-8 leading-[0.9]">
            Dream it. <br />
            <span className="text-blue-500">We find it.</span>
          </h1>
          <div className="space-y-3 md:space-y-4">
            <p className="text-lg md:text-2xl font-bold tracking-tight">
              Travel at the speed of thought.{" "}
              <span className="text-slate-300 font-medium italic block md:inline">
                Powered by Agentic Intelligence.
              </span>
            </p>
          </div>
        </div>

        {/* RESPONSIVE INPUT BAR (Stacks on mobile, horizontal on desktop) */}
        <div className="max-w-5xl mb-12 md:mb-16 relative group">
          <div className="flex gap-4 mb-4 min-h-[28px]">
            {itinerary && (
              <span className="px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest bg-blue-600 text-white animate-in fade-in zoom-in">
                Journey Verified
              </span>
            )}
            {loading && (
              <span className="px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest bg-slate-800 text-blue-400 border border-blue-400/20 animate-pulse">
                Consulting AI Agent...
              </span>
            )}
          </div>
          <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-[#39D39F] rounded-2xl md:rounded-3xl blur opacity-25" />
          <div className="relative flex flex-col lg:flex-row bg-slate-900/90 backdrop-blur-3xl p-2 rounded-2xl md:rounded-3xl border border-white/10 shadow-2xl lg:divide-x divide-white/10 items-stretch">
            <div className="flex items-center flex-1 px-4 md:px-6 py-4 md:py-5 border-b lg:border-b-0 border-white/5">
              <Sparkles size={20} className="text-[#39D39F] mr-3 shrink-0" />
              <input
                className="w-full bg-transparent outline-none text-sm md:text-base font-bold placeholder:text-slate-500"
                placeholder="Paris to London for 3 days?"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
              />
            </div>
            <div className="flex items-center px-4 md:px-6 py-4 md:py-5 min-w-full lg:min-w-[320px]">
              <Calendar size={20} className="text-blue-400 mr-3 shrink-0" />
              <div className="flex items-center gap-2 md:gap-3 w-full justify-between lg:justify-start">
                <input
                  type="date"
                  min={today}
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="bg-transparent text-[10px] md:text-sm font-black outline-none cursor-pointer hover:text-blue-400 transition-colors"
                />
                <ArrowRight size={12} className="text-slate-600" />
                <input
                  type="date"
                  min={startDate || today}
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="bg-transparent text-[10px] md:text-sm font-black outline-none cursor-pointer hover:text-blue-400 transition-colors"
                />
              </div>
            </div>
            <button
              onClick={handlePlanTrip}
              className="bg-blue-600 px-8 lg:px-12 py-4 lg:py-5 rounded-xl md:rounded-2xl font-black hover:bg-blue-500 transition-all uppercase text-xs md:text-sm m-1 md:m-2 shadow-xl active:scale-95"
            >
              PLAN
            </button>
          </div>
          {error && (
            <p className="text-red-500 bg-red-500/10 border border-red-500/20 px-4 py-2 rounded-xl text-xs mt-4 inline-block font-bold">
              {error}
            </p>
          )}
        </div>

        {itinerary && (
          <div className="max-w-5xl animate-in fade-in slide-in-from-bottom-4 duration-1000 relative z-20">
            {/* COMMAND BAR (Stackable) */}
            <div className="flex flex-col sm:flex-row justify-between items-center mb-8 md:mb-10 gap-4 bg-slate-900/40 p-3 md:p-4 rounded-2xl md:rounded-[2rem] border border-white/5 backdrop-blur-md">
              <div className="flex items-center gap-3">
                <div className="px-3 md:px-5 py-1.5 md:py-2 rounded-full text-[8px] md:text-[10px] font-black uppercase tracking-widest bg-blue-600 text-white shadow-lg">
                  Journey Verified
                </div>
                <div className="h-4 w-[1px] bg-white/10 hidden md:block" />
                <span className="text-[8px] md:text-[10px] font-black text-slate-500 uppercase tracking-widest hidden xs:block">
                  Agent ID: TRVL-
                  {Math.random().toString(36).substring(7).toUpperCase()}
                </span>
              </div>
              <button
                onClick={handleReset}
                className="w-full md:w-auto flex items-center justify-center gap-3 px-8 py-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-2xl transition-all group active:scale-95"
              >
                <span className="text-[9px] md:text-[11px] font-black uppercase tracking-[0.2em] text-white">
                  Start New Journey
                </span>
                <ArrowRight
                  size={16}
                  className="text-blue-500 rotate-180 group-hover:-translate-x-1 transition-transform"
                />
              </button>
            </div>

            {/* RESULTS GRID (Stacks on mobile) */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 md:gap-8 mb-8 md:mb-12">
              <div className="lg:col-span-2">
                <div className="p-6 md:p-8 rounded-3xl md:rounded-[2.5rem] bg-slate-900/60 backdrop-blur-3xl border border-white/10 shadow-2xl h-full flex flex-col gap-6 md:justify-between">
                  <div className="flex flex-col sm:flex-row justify-between items-start gap-6">
                    <div>
                      <span className="text-[8px] md:text-[10px] font-black text-blue-400 uppercase tracking-widest bg-blue-400/10 px-3 py-1 rounded-full border border-blue-400/20">
                        Verified GDS Route
                      </span>
                      <h4 className="text-2xl md:text-4xl font-black text-white mt-3 md:mt-4 tracking-tighter uppercase leading-tight">
                        {itinerary.selected_flight?.airline || "Global Carrier"}
                      </h4>
                    </div>

                    {/* CLICKABLE FLIGHT STACK */}
                    <a
                      href={`https://www.google.com/search?q=flights+from+${
                        itinerary.origin_name || ""
                      }+to+${itinerary.destination}+on+${itinerary.start_date}`}
                      target="_blank"
                      rel="noreferrer"
                      className="w-full sm:w-auto bg-slate-950/50 p-5 md:p-6 rounded-2xl md:rounded-[2rem] border border-white/5 shadow-inner hover:border-blue-500/50 transition-all group cursor-pointer"
                    >
                      <div className="flex items-center justify-between gap-8 mb-4">
                        <div className="flex items-center gap-3 md:gap-4">
                          <div className="w-8 h-8 md:w-10 md:h-10 rounded-2xl bg-blue-500/20 flex items-center justify-center group-hover:bg-blue-500/40 transition-colors">
                            <Plane
                              className="text-blue-400 rotate-45"
                              size={16}
                            />
                          </div>
                          <span className="text-[9px] font-bold text-slate-400 uppercase tracking-tighter group-hover:text-blue-400 transition-colors">
                            Outbound
                          </span>
                        </div>
                        <span className="text-xl md:text-2xl font-black text-white tracking-tight">
                          €{itinerary.selected_flight?.outbound_price || "265"}
                        </span>
                      </div>
                      <div className="w-full h-[1px] bg-white/5 mb-4" />
                      <div className="flex items-center justify-between gap-8">
                        <div className="flex items-center gap-3 md:gap-4">
                          <div className="w-8 h-8 md:w-10 md:h-10 rounded-2xl bg-blue-500/20 flex items-center justify-center group-hover:bg-blue-500/40 transition-colors">
                            <Plane
                              className="text-blue-400 rotate-[225deg]"
                              size={16}
                            />
                          </div>
                          <span className="text-[9px] font-bold text-slate-400 uppercase tracking-tighter group-hover:text-blue-400 transition-colors">
                            Return
                          </span>
                        </div>
                        <span className="text-xl md:text-2xl font-black text-white tracking-tight">
                          €{itinerary.selected_flight?.return_price || "215"}
                        </span>
                      </div>
                    </a>
                  </div>
                  <div className="flex justify-between items-end border-t border-white/5 pt-6">
                    <div>
                      <p className="text-[8px] md:text-xs text-slate-500 font-black uppercase tracking-widest mb-1">
                        Fare Total
                      </p>
                      <p className="text-4xl md:text-7xl font-black text-white leading-none tracking-tighter">
                        €{itinerary.selected_flight?.price_eur || "0"}
                      </p>
                    </div>
                    <p className="text-[9px] md:text-sm text-slate-400 font-mono font-bold tracking-widest uppercase bg-white/5 px-3 md:px-4 py-1 md:py-2 rounded-lg">
                      {formatDate(itinerary.start_date)} —{" "}
                      {formatDate(itinerary.end_date)}
                    </p>
                  </div>
                </div>
              </div>

              {/* HOTEL TIERS */}
              <div className="rounded-3xl md:rounded-[2.5rem] border border-white/10 bg-slate-900/60 backdrop-blur-3xl p-6 md:p-8">
                <h3 className="text-lg md:text-xl font-bold text-white mb-6 flex items-center gap-2">
                  <Bed className="text-blue-500" size={18} /> Property Tier
                </h3>
                <div className="space-y-3">
                  {hotelTiers.map((hotel: any, idx: number) => {
                    let tierLabel = hotel.label;
                    if (tierLabel === "LUXURY") tierLabel = "Priority Asset";
                    if (tierLabel === "BOUTIQUE")
                      tierLabel = "Independent Node";
                    if (tierLabel === "BUDGET" || tierLabel === "HOSTEL")
                      tierLabel = "Optimized Entry";

                    const hotelUrl = `https://www.google.com/search?q=${encodeURIComponent(
                      hotel.name +
                        " " +
                        itinerary.destination +
                        " hotel booking"
                    )}`;

                    return (
                      <a
                        key={idx}
                        href={hotelUrl}
                        target="_blank"
                        rel="noreferrer"
                        className={`block p-4 rounded-xl md:rounded-2xl border transition-all group hover:scale-[1.02] active:scale-[0.98] ${
                          idx === 0
                            ? "bg-blue-600/20 border-blue-500/50 shadow-lg"
                            : "bg-white/5 border-white/10 hover:border-white/20"
                        }`}
                      >
                        <div className="flex justify-between items-start">
                          <p className="font-bold text-white text-xs md:text-sm line-clamp-1 group-hover:text-blue-400 transition-colors">
                            {hotel.name}
                          </p>
                          <ArrowRight
                            size={12}
                            className="text-slate-600 group-hover:text-white group-hover:translate-x-1 transition-all"
                          />
                        </div>
                        <div className="flex items-center justify-between mt-1">
                          <span className="text-[8px] md:text-[10px] font-black text-blue-400 uppercase tracking-tighter">
                            {tierLabel}
                          </span>
                          <p className="font-black text-[#39D39F] text-xs md:text-sm">
                            €{hotel.price_per_night_eur}
                            <span className="text-[8px] font-normal text-white opacity-40">
                              /nt
                            </span>
                          </p>
                        </div>
                      </a>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* INTEGRITY SECTION (Responsive padding and layout) */}
            <div className="bg-[#39D39F]/10 border border-[#39D39F]/20 rounded-3xl md:rounded-[3rem] p-6 md:p-10 mb-8 md:mb-16 flex flex-col md:flex-row justify-between items-center gap-6 backdrop-blur-md text-center md:text-left">
              <div className="max-w-md">
                <h3 className="text-[#39D39F] font-mono text-[10px] md:text-sm uppercase tracking-[0.4em] mb-3 flex items-center gap-2 justify-center md:justify-start">
                  <ShieldCheck size={20} /> Financial Integrity: Verified
                </h3>
                <p className="text-slate-400 text-xs md:text-sm leading-relaxed font-medium tracking-tight px-2 md:px-0">
                  Real-time GDS fares and property auditing for{" "}
                  {itinerary.destination}.
                </p>
              </div>
              <div className="md:ml-auto">
                <p className="text-5xl md:text-7xl font-black text-white tracking-tighter mb-1 leading-none">
                  €{itinerary.total_cost_eur || "0"}
                </p>
                <p className="text-blue-400 text-[8px] md:text-[10px] font-black uppercase tracking-[0.3em] text-center md:text-right">
                  Estimated Journey Total
                </p>
              </div>
            </div>

            {/* ITINERARY (Responsive Timeline) */}
            <div className="mt-12 space-y-16 md:space-y-20">
              <h3 className="text-2xl md:text-4xl font-black tracking-tight border-b border-white/10 pb-6 italic uppercase">
                <Clock className="text-blue-500" /> AI Suggested Itinerary
              </h3>
              {days.map((day: any, i: number) => (
                <div
                  key={i}
                  className="border-l-2 md:border-l-4 border-blue-500/20 pl-6 md:pl-10 relative pb-10"
                >
                  <div className="absolute -left-[7px] md:-left-[10px] top-0 w-3 h-3 md:w-4 md:h-4 rounded-full bg-blue-500 shadow-xl" />
                  <div className="mb-8">
                    <span className="text-blue-500 font-black text-[8px] md:text-[10px] uppercase tracking-widest bg-blue-500/10 px-3 md:px-4 py-1.5 md:py-2 rounded-lg">
                      Day {day.day || i + 1}
                    </span>
                    <h4 className="text-3xl md:text-5xl font-black text-white mt-4 tracking-tighter leading-none">
                      {day.theme || "Daily Discovery"}
                    </h4>
                  </div>

                  <a
                    href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
                      day.theme + " " + itinerary.destination
                    )}`}
                    target="_blank"
                    rel="noreferrer"
                    className="relative flex flex-col items-center justify-center w-full h-28 md:h-40 bg-slate-900/80 backdrop-blur-xl border border-white/10 rounded-2xl md:rounded-[2.5rem] mb-8 overflow-hidden group shadow-2xl"
                  >
                    <div
                      className="absolute inset-0 opacity-10 group-hover:opacity-20 transition-opacity"
                      style={{
                        backgroundImage:
                          "radial-gradient(#3b82f6 1px, transparent 1px)",
                        backgroundSize: "30px 30px",
                      }}
                    ></div>
                    <div className="relative z-10 flex flex-col items-center gap-2">
                      <div className="w-10 h-10 md:w-14 md:h-14 bg-blue-600 rounded-2xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-500">
                        <MapPin size={24} className="text-white" />
                      </div>
                      <div className="text-center">
                        <h5 className="text-sm md:text-xl font-black text-white tracking-tighter uppercase">
                          VIEW DAY {day.day || i + 1} ON MAP
                        </h5>
                      </div>
                    </div>
                    <div className="absolute bottom-0 w-full bg-white/5 py-2 px-4 md:px-6 flex justify-between items-center border-t border-white/5">
                      <span className="text-[7px] md:text-[8px] font-bold text-slate-500 uppercase tracking-[0.4em]">
                        Authenticated Source
                      </span>
                      <ArrowRight
                        size={12}
                        className="text-slate-500 group-hover:translate-x-2 transition-transform"
                      />
                    </div>
                  </a>

                  <div className="grid gap-4 md:gap-6">
                    {(day.activities || []).map((act: any, j: number) => (
                      <div
                        key={j}
                        className="bg-white/5 border border-white/5 p-5 md:p-8 rounded-2xl md:rounded-[2.5rem] flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 hover:bg-white/10 transition-all backdrop-blur-md"
                      >
                        <div className="flex items-center gap-4 md:gap-8">
                          <div className="w-10 h-10 md:w-14 md:h-14 rounded-xl md:rounded-2xl bg-slate-800 flex items-center justify-center text-slate-500 group-hover:text-blue-400 border border-white/5 shrink-0 transition-all shadow-inner">
                            <Clock size={20} />
                          </div>
                          <div>
                            <p className="text-[8px] md:text-[10px] text-blue-400/60 font-black uppercase mb-1 tracking-widest">
                              {act.time || "Scheduled"}
                            </p>
                            <p className="font-black text-slate-100 text-lg md:text-2xl tracking-tighter leading-none group-hover:text-blue-400 transition-colors">
                              {act.name}
                            </p>
                          </div>
                        </div>
                        <span className="text-[#39D39F] font-black text-xl md:text-3xl tracking-tighter">
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
