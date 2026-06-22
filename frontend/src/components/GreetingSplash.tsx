"use client";

import React, { useEffect, useState, useRef } from "react";
import AmbientCanvas from "./AmbientCanvas";
import YaarOrb from "./YaarOrb";

interface GreetingSplashProps {
  onComplete: () => void;
}

const GREETINGS = [
  { text: "Namaste 🙏", lang: "Hindi", translation: "I bow to the divine in you" },
  { text: "Sat Sri Akal 🙏", lang: "Punjabi", translation: "Truth is the ultimate timeless reality" },
  { text: "Ram Ram 🙏", lang: "Haryanvi / Hindi", translation: "Supreme greeting of peace" },
  { text: "Kem Cho 👋", lang: "Gujarati", translation: "How are you doing, friend?" },
  { text: "Vanakkam 🙏", lang: "Tamil", translation: "Revered greetings and respects" },
  { text: "Nomoshkar 🙏", lang: "Bengali", translation: "I offer you my respectful greetings" },
  { text: "Adaab 🤝", lang: "Urdu", translation: "Respect and polite salutations" }
];

export default function GreetingSplash({ onComplete }: GreetingSplashProps) {
  const [index, setIndex] = useState(0);
  const [fadeState, setFadeState] = useState<"in" | "out">("in");
  const [sequenceComplete, setSequenceComplete] = useState(false);
  const timeoutsRef = useRef<NodeJS.Timeout[]>([]);

  const clearAllTimeouts = () => {
    timeoutsRef.current.forEach(t => clearTimeout(t));
    timeoutsRef.current = [];
  };

  useEffect(() => {
    let currentIdx = 0;

    const runCycle = () => {
      // Stay visible for 2000ms
      const visibleTimeout = setTimeout(() => {
        setFadeState("out");

        // Take 600ms to fade out, then transition
        const fadeTimeout = setTimeout(() => {
          if (currentIdx < GREETINGS.length - 1) {
            currentIdx += 1;
            setIndex(currentIdx);
            setFadeState("in");
            runCycle();
          } else {
            setSequenceComplete(true);
            setFadeState("in");
          }
        }, 600);

        timeoutsRef.current.push(fadeTimeout);
      }, 2000);

      timeoutsRef.current.push(visibleTimeout);
    };

    setFadeState("in");
    runCycle();

    return () => {
      clearAllTimeouts();
    };
  }, []);

  const handleSkipOrContinue = () => {
    clearAllTimeouts();
    onComplete();
  };

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
              fadeState === "in" 
                ? "opacity-100 scale-100 translate-y-0" 
                : "opacity-0 scale-95 -translate-y-2"
            }`}
          >
            {GREETINGS[index].text}
          </h1>
          
          <div
            className={`flex items-center gap-2 mt-5 px-3 py-1 bg-white/5 border border-white/10 rounded-full transition-opacity duration-[600ms] ${
              fadeState === "in" ? "opacity-75" : "opacity-0"
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
          {sequenceComplete ? (
            <button
              onClick={handleSkipOrContinue}
              className="px-8 py-3.5 rounded-full bg-white text-[#06070d] text-xs font-black uppercase tracking-widest transition-premium hover:-translate-y-0.5 hover:shadow-lg active:translate-y-0 cursor-pointer animate-fade-in"
            >
              Continue to Setup →
            </button>
          ) : (
            <button
              onClick={handleSkipOrContinue}
              className="px-6 py-2.5 rounded-full bg-white/5 border border-white/10 text-[10px] font-black uppercase tracking-widest text-slate-400 hover:text-white hover:bg-white/10 transition-premium cursor-pointer"
            >
              Skip Intro 👋
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
