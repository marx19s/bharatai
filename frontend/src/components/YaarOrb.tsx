"use client";

import React, { useState } from "react";

export type OrbState = "idle" | "listening" | "thinking" | "responding" | "hover";

interface YaarOrbProps {
  state: OrbState;
  className?: string;
  onClick?: () => void;
  size?: "sm" | "md" | "lg" | "xl";
}

export default function YaarOrb({ state, className = "", onClick, size = "md" }: YaarOrbProps) {
  const [isHovered, setIsHovered] = useState(false);

  // Determine size classes
  const sizeClasses = {
    sm: "w-10 h-10",
    md: "w-20 h-20 sm:w-24 sm:h-24",
    lg: "w-32 h-32 sm:w-36 sm:h-36",
    xl: "w-44 h-44 sm:w-48 sm:h-48"
  }[size];

  // Map state to animation classes
  const getAnimationClass = () => {
    if (isHovered) return "animate-orb-hover";
    switch (state) {
      case "listening":
        return "animate-orb-listening";
      case "thinking":
        return "animate-orb-thinking";
      case "responding":
        return "animate-orb-responding";
      case "hover":
        return "animate-orb-hover";
      case "idle":
      default:
        return "animate-orb-idle";
    }
  };

  // Map state to color gradient classes using Warm Gold, Soft Coral, Electric Indigo & Pearl White
  const getGradientStyle = () => {
    switch (state) {
      case "listening":
        // Listening: Soft Coral and Pearl White glow
        return {
          background: "radial-gradient(circle, rgba(251,113,133,0.95) 0%, rgba(248,250,252,0.8) 50%, rgba(59,130,246,0.1) 100%)",
          boxShadow: "0 0 35px rgba(251,113,133,0.4), 0 0 70px rgba(248,250,252,0.2)"
        };
      case "thinking":
        // Thinking: Conic gradient with Gold, Coral, Electric Indigo & Pearl White
        return {
          background: "conic-gradient(from 180deg, #d97706, #fb7185, #3b82f6, #f8fafc, #d97706)",
          boxShadow: "0 0 45px rgba(217,119,6,0.4), 0 0 80px rgba(59,130,246,0.3)"
        };
      case "responding":
        // Responding: Warm Gold and Soft Coral flow wave
        return {
          background: "radial-gradient(circle, rgba(217,119,6,0.95) 0%, rgba(251,113,133,0.7) 60%, rgba(248,250,252,0.1) 100%)",
          boxShadow: "0 0 40px rgba(217,119,6,0.45), 0 0 75px rgba(251,113,133,0.3)"
        };
      case "hover":
        // Hover state: Glowing Gold & Pearl White
        return {
          background: "radial-gradient(circle, #f59e0b 0%, #fb7185 50%, #f8fafc 90%, rgba(0,0,0,0) 100%)",
          boxShadow: "0 0 55px rgba(217,119,6,0.5), 0 0 95px rgba(251,113,133,0.4)"
        };
      case "idle":
      default:
        // Idle: Warm Gold / Soft Coral slow breathing
        return {
          background: "radial-gradient(circle, rgba(217,119,6,0.85) 0%, rgba(251,113,133,0.5) 60%, rgba(59,130,246,0.15) 100%)",
          boxShadow: "0 0 30px rgba(217,119,6,0.3), 0 0 60px rgba(251,113,133,0.2)"
        };
    }
  };

  return (
    <div 
      className={`relative flex items-center justify-center cursor-pointer ${className}`}
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Outer ambient blur shadow */}
      <div 
        className={`absolute rounded-full transition-premium opacity-55 scale-110 blur-2xl ${sizeClasses}`}
        style={getGradientStyle()}
      />
      
      {/* Core breathing Orb shape */}
      <div
        className={`rounded-full transition-premium border border-white/5 ${sizeClasses} ${getAnimationClass()}`}
        style={getGradientStyle()}
      >
        {/* Internal organic glimmers */}
        <div className="absolute inset-2 rounded-full bg-white/5 filter blur-[4px] mix-blend-overlay" />
        <div className="absolute top-1/4 left-1/4 w-1/3 h-1/3 rounded-full bg-white/10 filter blur-[6px] mix-blend-screen animate-pulse" />
      </div>
    </div>
  );
}
