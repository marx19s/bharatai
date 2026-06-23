"use client";

import React, { useEffect, useState } from "react";
import AmbientCanvas from "./AmbientCanvas";
import YaarOrb from "./YaarOrb";

interface GreetingSplashProps {
  onComplete: () => void;
}

const GREETINGS = [
  { text: "Hello 👋", lang: "English", translation: "Universal greeting of welcome" },
  { text: "Namaste 🙏", lang: "Hindi", translation: "I bow to the divine in you" },
  { text: "Sat Sri Akal 🙏", lang: "Punjabi", translation: "Truth is the ultimate timeless reality" },
  { text: "Vanakkam 🙏", lang: "Tamil", translation: "Revered greetings and respects" },
  { text: "Nomoshkar 🙏", lang: "Bengali", translation: "I offer you my respectful greetings" },
  { text: "Kem Cho 👋", lang: "Gujarati", translation: "How are you doing, friend?" },
  { text: "Adaab 🤝", lang: "Urdu", translation: "Respect and polite salutations" }
];

export default function GreetingSplash({ onComplete }: GreetingSplashProps) {
  const [index, setIndex] = useState(0);
  const [state, setState] = useState<"FADE_IN" | "VISIBLE" | "FADE_OUT">("FADE_IN");

  useEffect(() => {
    let active = true;
    let timer: NodeJS.Timeout;

    const runTransition = () => {
      if (!active) return;

      if (state === "FADE_IN") {
        timer = setTimeout(() => {
          if (active) setState("VISIBLE");
        }, 600);
      } else if (state === "VISIBLE") {
        timer = setTimeout(() => {
          if (active) setState("FADE_OUT");
        }, 2000);
      } else if (state === "FADE_OUT") {
        timer = setTimeout(() => {
          if (active) {
            setIndex((prev) => (prev + 1) % GREETINGS.length);
            setState("FADE_IN");
          }
        }, 600);
      }
    };

    runTransition();

    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [state]);

  const isVisible = state !== "FADE_OUT";

  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-[#06070d] text-[#eef2ff] overflow-hidden select-none">
      {/* Slow, Elegant Network Background */}
      <AmbientCanvas />

      <div className="flex flex-col items-center text-center space-y-8 max-w-lg px-6 z-10 animate-fade-in">
        {/* Breathing Companion Orb */}
        <YaarOrb state="idle" size="md" className="animate-pulse" />

        <div className="h-40 flex flex-col items-center justify-center">
          <h1
            className={`text-4xl sm:text-5xl font-black font-display tracking-tight text-white transition-all duration-[600ms] ease-out transform ${
              isVisible
                ? "opacity-100 scale-100 translate-y-0"
                : "opacity-0 scale-95 -translate-y-2"
            }`}
          >
            {GREETINGS[index].text}
          </h1>
          
          <div
            className={`flex items-center gap-2 mt-5 px-3 py-1 bg-white/5 border border-white/10 rounded-full transition-opacity duration-[600ms] ${
              isVisible ? "opacity-75" : "opacity-0"
            }`}
          >
            <span className="text-[10px] font-black uppercase tracking-wider text-amber-500 font-mono">
              {GREETINGS[index].lang}
            </span>
            <span className="w-1 h-1 rounded-full bg-slate-600" />
            <span className="text-[10px] font-medium text-slate-400 italic">
              {GREETINGS[index].translation}
            </span>
          </div>
        </div>

        {/* Action Button Area */}
        <div className="h-16 flex items-center justify-center">
          <button
            onClick={onComplete}
            className="px-8 py-3.5 rounded-full bg-white text-[#06070d] text-xs font-black uppercase tracking-widest transition-premium hover:-translate-y-0.5 hover:shadow-lg active:translate-y-0 cursor-pointer animate-fade-in"
          >
            Get Started &rarr;
          </button>
        </div>
      </div>
    </div>
  );
}
