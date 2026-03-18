import React from "react";
import { Plane, Ticket, Clock } from "lucide-react";

export function FlightTicket({
  flight,
  origin,
  destination,
  destinationCode,
}: any) {
  // Fallback for codes if they aren't parsed yet
  const displayOrigin = origin ? origin.substring(0, 3).toUpperCase() : "ORG";
  const displayDest =
    destinationCode ||
    (destination ? destination.substring(0, 3).toUpperCase() : "DST");

  return (
    <div className="relative w-full bg-slate-900/40 border border-white/10 rounded-[2rem] overflow-hidden backdrop-blur-3xl shadow-2xl group transition-all hover:border-blue-500/30">
      {/* Top Header Strip */}
      <div className="bg-blue-600/90 px-6 py-3 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Ticket size={14} className="text-white" />
          <span className="text-[10px] font-black uppercase tracking-[0.2em] text-white">
            Priority Boarding Pass
          </span>
        </div>
        <div className="h-2 w-2 rounded-full bg-white animate-pulse" />
      </div>

      <div className="p-8">
        <div className="flex justify-between items-center mb-8">
          {/* Origin */}
          <div className="flex flex-col">
            <span className="text-slate-500 text-[10px] font-bold uppercase tracking-widest mb-1">
              From
            </span>
            <h2 className="text-5xl font-black tracking-tighter text-white">
              {displayOrigin}
            </h2>
            <p className="text-slate-400 text-xs font-medium truncate max-w-[100px]">
              {origin || "Origin City"}
            </p>
          </div>

          {/* Path Illustration */}
          <div className="flex-1 flex flex-col items-center px-6">
            <div className="w-full flex items-center gap-2">
              <div className="h-[2px] flex-1 bg-gradient-to-r from-blue-500/0 via-blue-500/50 to-blue-500" />
              <Plane
                size={20}
                className="text-blue-500 rotate-90 group-hover:translate-x-2 transition-transform duration-700"
              />
              <div className="h-[2px] flex-1 bg-gradient-to-r from-blue-500 via-blue-500/50 to-blue-500/0" />
            </div>
            <p className="text-[9px] font-mono text-slate-500 uppercase mt-3 tracking-[0.3em]">
              {flight?.airline || "Global Carrier"}
            </p>
          </div>

          {/* Destination */}
          <div className="flex flex-col text-right">
            <span className="text-slate-500 text-[10px] font-bold uppercase tracking-widest mb-1">
              To
            </span>
            <h2 className="text-5xl font-black tracking-tighter text-white">
              {displayDest}
            </h2>
            <p className="text-slate-400 text-xs font-medium truncate max-w-[100px]">
              {destination || "Destination"}
            </p>
          </div>
        </div>

        {/* Footer Section: Price and Barcode */}
        <div className="flex justify-between items-end pt-6 border-t border-white/5 border-dashed">
          <div>
            <span className="text-slate-500 text-[10px] font-bold uppercase tracking-widest block mb-1">
              Fare (Verified)
            </span>
            <div className="text-3xl font-black text-[#39D39F] flex items-baseline gap-1">
              €{flight?.price_eur || "0"}
              <span className="text-xs font-medium opacity-50">.00</span>
            </div>
          </div>

          {/* Decorative Barcode */}
          <div className="flex flex-col items-end gap-2">
            <div className="flex gap-[2px] h-8 items-center bg-white/90 p-1 rounded-sm">
              {[2, 1, 3, 1, 2, 4, 1, 2, 3, 1, 2, 1].map((w, i) => (
                <div
                  key={i}
                  className="bg-black h-full"
                  style={{ width: `${w}px` }}
                />
              ))}
            </div>
            <span className="text-[8px] font-mono text-slate-500 tracking-widest">
              TRIP-ID-{Math.random().toString(36).substr(2, 6).toUpperCase()}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
