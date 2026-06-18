"use client";

import React, { useState } from "react";
import DocumentSidebar from "../components/DocumentSidebar";
import ChatInterface from "../components/ChatInterface";

const API_BASE_URL = "http://localhost:8000";

export default function Home() {
  const [activeConversationId, setActiveConversationId] = useState<number | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleRefreshSidebar = () => {
    setRefreshTrigger(prev => prev + 1);
  };

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
      <div className={`shrink-0 overflow-hidden ${sidebarOpen ? "w-80" : "w-0 pointer-events-none"}`}>
        <DocumentSidebar
          activeConversationId={activeConversationId}
          onSelectConversation={setActiveConversationId}
          apiBaseUrl={API_BASE_URL}
          refreshTrigger={refreshTrigger}
          onRefreshSidebar={handleRefreshSidebar}
          sidebarOpen={sidebarOpen}
          setSidebarOpen={setSidebarOpen}
        />
      </div>

      {/* Main Chat Workspace */}
      <div className="flex-1 h-full flex flex-col bg-transparent">
        <ChatInterface
          activeConversationId={activeConversationId}
          onSelectConversation={setActiveConversationId}
          apiBaseUrl={API_BASE_URL}
          onRefreshDocuments={handleRefreshSidebar}
          sidebarOpen={sidebarOpen}
          setSidebarOpen={setSidebarOpen}
        />
      </div>
    </div>
  );
}
