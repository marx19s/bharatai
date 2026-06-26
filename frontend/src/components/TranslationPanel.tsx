"use client";

import React, { useState } from "react";
import { Languages, Copy, Share2, ArrowRight, ClipboardCheck, Bookmark, RefreshCw } from "lucide-react";

interface TranslationPanelProps {
  token: string | null;
  apiBaseUrl: string;
}

const SUPPORTED_LANGUAGES = [
  { id: "Punjabi", label: "ਪੰਜਾਬੀ (Punjabi)" },
  { id: "Hindi", label: "हिन्दी (Hindi)" },
  { id: "Gujarati", label: "ગુજરાતી (Gujarati)" },
  { id: "Tamil", label: "தமிழ் (Tamil)" },
  { id: "Bengali", label: "বাংলা (Bengali)" },
  { id: "Telugu", label: "తెలుగు (Telugu)" },
  { id: "Marathi", label: "मराठी (Marathi)" },
  { id: "Urdu", label: "اردو (Urdu)" },
  { id: "Kannada", label: "ಕನ್ನಡ (Kannada)" },
  { id: "Malayalam", label: "മലയാളം (Malayalam)" }
];

export default function TranslationPanel({ token, apiBaseUrl }: TranslationPanelProps) {
  const [sourceText, setSourceText] = useState("");
  const [targetLang, setTargetLang] = useState("Punjabi");
  const [translatedText, setTranslatedText] = useState("");
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [shared, setShared] = useState(false);
  const [vaulted, setVaulted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleTranslate = async () => {
    if (!sourceText.trim()) return;
    setLoading(true);
    setError(null);
    setCopied(false);
    setShared(false);
    setVaulted(false);

    try {
      const res = await fetch(`${apiBaseUrl}/api/tools/translate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          text: sourceText,
          target_language: targetLang
        })
      });

      if (res.ok) {
        const data = await res.json();
        setTranslatedText(data.translated_text);
      } else {
        const errData = await res.json();
        setError(errData.detail || "Translation failed");
      }
    } catch (err: any) {
      setError("Unable to connect to the translation service.");
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (!translatedText) return;
    navigator.clipboard.writeText(translatedText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleShare = async () => {
    if (!translatedText) return;
    const shareData = {
      title: "YAAR Translation",
      text: translatedText
    };

    if (navigator.share && navigator.canShare && navigator.canShare(shareData)) {
      try {
        await navigator.share(shareData);
        setShared(true);
        setTimeout(() => setShared(false), 2000);
      } catch (_) {}
    } else {
      // Fallback: Copy share link or text representation
      navigator.clipboard.writeText(`YAAR Translation [English -> ${targetLang}]:\n\nOriginal: ${sourceText}\n\nTranslation: ${translatedText}`);
      setShared(true);
      setTimeout(() => setShared(false), 2000);
    }
  };

  const handleSaveToVault = () => {
    if (!translatedText) return;
    
    // Save translation to local storage vault
    try {
      const savedVault = localStorage.getItem("yaar_vault") || "[]";
      const items = JSON.parse(savedVault);
      
      const newItem = {
        id: `vault-trans-${Date.now()}`,
        title: `Translation: English to ${targetLang}`,
        content: `Original:\n${sourceText}\n\nTranslation:\n${translatedText}`,
        type: "Saved Answer",
        tags: ["Translation", targetLang],
        created_at: new Date().toISOString()
      };
      
      localStorage.setItem("yaar_vault", JSON.stringify([newItem, ...items]));
      setVaulted(true);
      setTimeout(() => setVaulted(false), 2000);
    } catch (_) {}
  };

  return (
    <div className="flex-1 overflow-y-auto scroll-smooth-premium p-6 md:p-12 text-slate-150 max-w-5xl mx-auto space-y-8 animate-slide-in-right bg-[#121316]">
      {/* Header section */}
      <div className="flex flex-col sm:flex-row items-center sm:items-start justify-between gap-4 border-b border-white/5 pb-6">
        <div className="space-y-1.5 text-center sm:text-left">
          <h2 className="text-3xl font-black text-white tracking-tight font-display">
            Translation
          </h2>
          <p className="text-slate-400 text-xs font-medium max-w-md">
            Indic Sovereign Translation Engine. Dedicated tool to convert text into natural regional Indian languages.
          </p>
        </div>
      </div>

      {/* Translation Workspace */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-stretch">
        {/* Source Text Container */}
        <div className="flex flex-col gap-3 p-6 rounded-2xl bg-slate-900/40 border border-white/5 shadow-xl">
          <div className="flex items-center justify-between">
            <span className="text-[10px] uppercase tracking-wider font-extrabold text-slate-450">Source Text</span>
            <span className="text-xs font-bold text-slate-300">English (India)</span>
          </div>

          <textarea
            value={sourceText}
            onChange={(e) => setSourceText(e.target.value)}
            placeholder="Type or paste English text to translate..."
            className="flex-1 min-h-[220px] p-4 rounded-xl bg-[#121316] border border-slate-800 text-xs text-white placeholder-slate-550 outline-none focus:border-amber-500 transition-premium resize-none font-medium leading-relaxed"
          />

          <div className="flex items-center gap-3 pt-2">
            <div className="flex-1 flex flex-col gap-1">
              <label className="text-[9px] uppercase tracking-wider font-extrabold text-slate-500">Target Language</label>
              <select
                value={targetLang}
                onChange={(e) => setTargetLang(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl bg-[#121316] border border-slate-800/80 text-white text-xs outline-none focus:border-amber-500 transition-premium cursor-pointer font-bold"
              >
                {SUPPORTED_LANGUAGES.map((l) => (
                  <option key={l.id} value={l.id}>{l.label}</option>
                ))}
              </select>
            </div>

            <button
              onClick={handleTranslate}
              disabled={loading || !sourceText.trim()}
              className="px-6 py-3 mt-4 bg-amber-600 hover:bg-amber-500 disabled:opacity-40 text-white rounded-xl flex items-center justify-center gap-2 text-xs font-black uppercase tracking-wider transition-premium cursor-pointer shadow-md"
            >
              {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Languages className="w-4 h-4" />}
              <span>Translate</span>
            </button>
          </div>
        </div>

        {/* Translation Output Container */}
        <div className="flex flex-col gap-3 p-6 rounded-2xl bg-slate-900/40 border border-white/5 shadow-xl relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-[10px] uppercase tracking-wider font-extrabold text-slate-450">Translation Output</span>
            <span className="text-xs font-bold text-amber-550 font-display">
              {SUPPORTED_LANGUAGES.find((l) => l.id === targetLang)?.label.split(" (")[0]}
            </span>
          </div>

          <div className="flex-1 min-h-[220px] p-4 rounded-xl bg-[#121316] border border-slate-800 text-xs text-white overflow-y-auto whitespace-pre-wrap select-text font-medium leading-relaxed">
            {loading ? (
              <div className="h-full flex items-center justify-center text-slate-500 gap-2">
                <div className="w-4 h-4 border-2 border-amber-500/20 border-t-amber-500 rounded-full animate-spin"></div>
                <span className="text-[10px] uppercase font-bold tracking-wider">Translating Indic Text...</span>
              </div>
            ) : error ? (
              <span className="text-rose-455 font-bold">{error}</span>
            ) : translatedText ? (
              translatedText
            ) : (
              <span className="text-slate-600 italic">Translated output will appear here...</span>
            )}
          </div>

          {/* Action Row */}
          <div className="flex items-center justify-end gap-2 pt-2 border-t border-white/5">
            <button
              onClick={handleCopy}
              disabled={!translatedText || loading}
              className={`p-2.5 rounded-xl border transition-premium flex items-center gap-1.5 text-[10px] font-black uppercase tracking-wider cursor-pointer ${
                copied
                  ? "bg-emerald-950/40 border-emerald-500 text-emerald-450"
                  : "bg-[#121316] border-slate-800 text-slate-400 hover:text-white"
              }`}
              title="Copy to clipboard"
            >
              {copied ? <ClipboardCheck className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? "Copied" : "Copy"}</span>
            </button>

            <button
              onClick={handleShare}
              disabled={!translatedText || loading}
              className={`p-2.5 rounded-xl border transition-premium flex items-center gap-1.5 text-[10px] font-black uppercase tracking-wider cursor-pointer ${
                shared
                  ? "bg-blue-955/40 border-blue-500 text-blue-450"
                  : "bg-[#121316] border-slate-800 text-slate-400 hover:text-white"
              }`}
              title="Share translation"
            >
              <Share2 className="w-3.5 h-3.5" />
              <span>{shared ? "Shared!" : "Share"}</span>
            </button>

            <button
              onClick={handleSaveToVault}
              disabled={!translatedText || loading}
              className={`p-2.5 rounded-xl border transition-premium flex items-center gap-1.5 text-[10px] font-black uppercase tracking-wider cursor-pointer ${
                vaulted
                  ? "bg-emerald-955/40 border-emerald-500 text-emerald-450"
                  : "bg-[#121316] border-slate-800 text-slate-400 hover:text-white"
              }`}
              title="Save to Second Brain Vault"
            >
              <Bookmark className="w-3.5 h-3.5" />
              <span>{vaulted ? "Saved!" : "Vault"}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
