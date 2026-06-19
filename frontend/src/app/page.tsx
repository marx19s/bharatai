"use client";

import React, { useEffect, useState } from "react";
import DocumentSidebar from "../components/DocumentSidebar";
import ChatInterface from "../components/ChatInterface";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function Home() {
  const [activeConversationId, setActiveConversationId] = useState<number | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  
  // Auth states
  const [token, setToken] = useState<string | null>(null);
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authError, setAuthError] = useState("");
  const [authLoading, setAuthLoading] = useState(false);
  const [checkingAuth, setCheckingAuth] = useState(false);
  const [mounted, setMounted] = useState(false);
  
  useEffect(() => {
    setMounted(true);
    if (typeof window !== "undefined") {
      setSidebarOpen(window.matchMedia("(min-width: 768px)").matches);
      
      const savedToken = localStorage.getItem("bharatai_token");
      if (savedToken) {
        setToken(savedToken);
      }
    }
  }, []);

  const handleRefreshSidebar = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError("");
    setAuthLoading(true);

    const endpoint = isLoginMode ? "/api/auth/login" : "/api/auth/register";

    try {
      const res = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Authentication failed");
      }

      localStorage.setItem("bharatai_token", data.access_token);
      localStorage.setItem("bharatai_email", data.email);
      setToken(data.access_token);
      setRefreshTrigger(prev => prev + 1);
    } catch (err: any) {
      setAuthError(err.message || "An unexpected error occurred");
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("bharatai_token");
    localStorage.removeItem("bharatai_email");
    setToken(null);
    setActiveConversationId(null);
  };

  if (!mounted) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 rounded-full border-4 border-indigo-200 border-t-indigo-650 animate-spin"></div>
          <span className="text-xs font-bold text-slate-500">Loading BharatAI...</span>
        </div>
      </div>
    );
  }

  // Render Login/Register Overlay Portal
  if (!token) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 relative p-4">
        {/* Abstract background glowing circles */}
        <div className="absolute top-1/4 left-1/4 w-72 h-72 rounded-full bg-orange-500/10 blur-[120px] pointer-events-none" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 rounded-full bg-indigo-500/15 blur-[140px] pointer-events-none" />

        <div className="w-full max-w-md p-8 rounded-3xl bg-white/10 backdrop-blur-xl border border-white/10 shadow-2xl z-10 flex flex-col gap-6">
          <div className="text-center space-y-2">
            <h1 className="text-3xl font-black tracking-tight text-white font-display">
              <span className="text-gradient-title">bharat</span><span className="text-orange-500">ai</span>
            </h1>
            <p className="text-slate-400 text-xs font-medium">
              {isLoginMode ? "Log in to access your Sovereign AI Workspace" : "Create your secure account to start"}
            </p>
          </div>

          <form onSubmit={handleAuthSubmit} className="flex flex-col gap-4">
            {authError && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs font-bold text-center">
                {authError}
              </div>
            )}

            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] uppercase tracking-wider font-extrabold text-slate-400">Email Address</label>
              <input
                type="email"
                required
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="you@domain.com"
                className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white text-sm placeholder-slate-500 outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50 transition-premium"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] uppercase tracking-wider font-extrabold text-slate-400">Password</label>
              <input
                type="password"
                required
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white text-sm placeholder-slate-500 outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50 transition-premium"
              />
            </div>

            <button
              type="submit"
              disabled={authLoading}
              className="w-full py-3.5 mt-2 bg-gradient-to-r from-orange-500 to-indigo-600 hover:from-orange-600 hover:to-indigo-700 text-white text-xs font-black uppercase tracking-wider rounded-xl transition-premium shadow-lg shadow-indigo-950/20 disabled:opacity-50 cursor-pointer text-center flex items-center justify-center gap-2"
            >
              {authLoading ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
              ) : isLoginMode ? (
                "Log In"
              ) : (
                "Create Account"
              )}
            </button>
          </form>

          <div className="text-center text-xs text-slate-400 pt-2 border-t border-white/5">
            {isLoginMode ? "New to BharatAI? " : "Already have an account? "}
            <button
              onClick={() => {
                setIsLoginMode(!isLoginMode);
                setAuthError("");
              }}
              className="text-indigo-400 hover:text-indigo-300 font-bold transition-colors cursor-pointer"
            >
              {isLoginMode ? "Sign Up Free" : "Log In"}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-transparent font-sans text-slate-900 relative">
      {!sidebarOpen && (
        <button
          onClick={() => setSidebarOpen(true)}
          className="fixed left-4 top-4 z-50 p-2 rounded-xl bg-white/80 border border-slate-200/50 shadow-md hover:bg-slate-100/80 text-slate-500 hover:text-slate-700 transition-premium cursor-pointer backdrop-blur-md flex items-center justify-center shrink-0"
          title="Expand Sidebar"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      )}

      {/* Left Sidebar showing Conversation History Sessions */}
      {sidebarOpen && (
        <button
          className="fixed inset-0 z-30 bg-slate-950/20 backdrop-blur-[1px] md:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-label="Close sidebar overlay"
        />
      )}
      <div className={`shrink-0 overflow-hidden transition-[width] duration-300 z-40 md:relative ${
        sidebarOpen
          ? "fixed md:static left-0 top-0 h-full w-80 max-w-[86vw] shadow-2xl md:shadow-none border-r border-slate-200/50 md:border-r-0"
          : "w-0 pointer-events-none"
      }`}>
        <DocumentSidebar
          activeConversationId={activeConversationId}
          onSelectConversation={setActiveConversationId}
          apiBaseUrl={API_BASE_URL}
          refreshTrigger={refreshTrigger}
          onRefreshSidebar={handleRefreshSidebar}
          sidebarOpen={sidebarOpen}
          setSidebarOpen={setSidebarOpen}
          token={token}
          onLogout={handleLogout}
        />
      </div>

      {/* Main Chat Workspace / Welcome Screen */}
      <div className="flex-1 h-full flex flex-col bg-transparent">
        {activeConversationId ? (
          <ChatInterface
            activeConversationId={activeConversationId}
            onSelectConversation={setActiveConversationId}
            apiBaseUrl={API_BASE_URL}
            onRefreshDocuments={handleRefreshSidebar}
            sidebarOpen={sidebarOpen}
            setSidebarOpen={setSidebarOpen}
            token={token}
          />
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center p-6 text-center relative overflow-hidden bg-[linear-gradient(180deg,rgba(255,255,255,0.72)_0%,rgba(248,250,252,0.54)_45%,rgba(255,247,237,0.38)_100%)]">
            {/* Ambient Background Blobs */}
            <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-96 h-96 rounded-full bg-orange-400/5 blur-[120px] pointer-events-none" />
            <div className="absolute bottom-1/4 right-1/3 w-80 h-80 rounded-full bg-indigo-500/10 blur-[130px] pointer-events-none" />
            
            <div className="max-w-2xl space-y-6 z-10 p-4">
              <span className="inline-flex px-3.5 py-1.5 bg-orange-50 text-orange-700 font-black text-[9px] uppercase tracking-[0.18em] rounded-full border border-orange-200/60 shadow-sm animate-pulse-soft">
                India-first Sovereign AI workspace
              </span>
              <h2 className="text-4xl sm:text-5xl font-black tracking-tight text-slate-950 font-display leading-tight">
                Welcome to <span className="text-gradient-title">bharat</span><span className="text-gradient-orange">ai</span>
              </h2>
              <p className="text-slate-600 text-sm md:text-base leading-relaxed max-w-lg mx-auto">
                Search the web, analyze PDFs, translate Indian languages, and query documents in one premium workspace. Select an existing conversation from the sidebar history or create a new session.
              </p>
              
              <div className="pt-4 flex flex-col sm:flex-row gap-3 justify-center items-center">
                <button
                  onClick={async () => {
                    try {
                      const res = await fetch(`${API_BASE_URL}/api/conversations`, {
                        method: "POST",
                        headers: { 
                          "Content-Type": "application/json",
                          "Authorization": `Bearer ${token}`
                        },
                        body: JSON.stringify({ document_id: null })
                      });
                      if (res.ok) {
                        const data = await res.json();
                        setActiveConversationId(data.id);
                        handleRefreshSidebar();
                        if (window.innerWidth < 768) {
                          setSidebarOpen(false);
                        }
                      }
                    } catch {
                      alert("Failed to start new conversation session.");
                    }
                  }}
                  className="px-6 py-3.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-black uppercase tracking-wider rounded-xl transition-premium shadow-md hover:shadow-lg cursor-pointer min-w-[200px]"
                >
                  Create New Chat
                </button>
                <button
                  onClick={() => setSidebarOpen(true)}
                  className="px-6 py-3.5 bg-white border border-slate-200 text-slate-700 hover:text-slate-900 text-xs font-black uppercase tracking-wider rounded-xl transition-premium shadow-sm hover:shadow-md cursor-pointer min-w-[200px]"
                >
                  View Chat History
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
