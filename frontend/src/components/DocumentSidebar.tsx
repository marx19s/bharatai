"use client";

import React, { useState, useEffect } from "react";
import { MessageSquare, Trash2, RefreshCw, AlertCircle, Plus, Edit2, Check, X } from "lucide-react";

interface Conversation {
  id: number;
  title: string;
  created_at: string;
  document_id: number | null;
  document_name: string | null;
}

interface DocumentSidebarProps {
  activeConversationId: number | null;
  onSelectConversation: (id: number | null) => void;
  apiBaseUrl: string;
  refreshTrigger: number;
  onRefreshSidebar: () => void;
  sidebarOpen: boolean;
  setSidebarOpen: React.Dispatch<React.SetStateAction<boolean>>;
  token: string | null;
  onLogout: () => void;
}

export default function DocumentSidebar({
  activeConversationId,
  onSelectConversation,
  apiBaseUrl,
  refreshTrigger,
  onRefreshSidebar,
  setSidebarOpen,
  token,
  onLogout
}: DocumentSidebarProps) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingConvId, setEditingConvId] = useState<number | null>(null);
  const [editingTitle, setEditingTitle] = useState("");

  const handleSaveRename = async (convId: number) => {
    if (!editingTitle.trim()) return;
    try {
      const res = await fetch(`${apiBaseUrl}/api/conversations/${convId}`, {
        method: "PUT",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ title: editingTitle.trim() })
      });
      if (!res.ok) throw new Error("Failed to rename conversation");
      
      setConversations(prev => prev.map(c => c.id === convId ? { ...c, title: editingTitle.trim() } : c));
      setEditingConvId(null);
      onRefreshSidebar();
    } catch {
      alert("Failed to save new conversation title.");
    }
  };

  // Fetch past conversations
  const fetchConversations = async () => {
    if (!token) return;
    try {
      const res = await fetch(`${apiBaseUrl}/api/conversations`, {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      if (!res.ok) throw new Error("Failed to fetch conversations");
      const data = await res.json();
      setConversations(data);
      setError(null);
    } catch (err: unknown) {
      console.error(err);
      setError("Failed to fetch conversation history.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchConversations();
  }, [refreshTrigger, activeConversationId, token]);

  // Handle new conversation creation
  const handleNewConversation = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${apiBaseUrl}/api/conversations`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ document_id: null })
      });
      if (!res.ok) throw new Error("Failed to create conversation");
      const data = await res.json();
      
      // Select the new conversation
      onSelectConversation(data.id);
      
      // Auto-collapse sidebar on mobile screen ratios
      if (window.innerWidth < 768) {
        setSidebarOpen(false);
      }
      
      onRefreshSidebar();
    } catch {
      alert("Failed to start new conversation session.");
    } finally {
      setLoading(false);
    }
  };

  // Handle conversation deletion
  const handleDelete = async (e: React.MouseEvent, convId: number) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this conversation session? All its messages will be deleted.")) return;

    try {
      const res = await fetch(`${apiBaseUrl}/api/conversations/${convId}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });

      if (!res.ok) throw new Error("Delete failed");

      if (activeConversationId === convId) {
        onSelectConversation(null);
      }
      
      setConversations(prev => prev.filter(c => c.id !== convId));
      onRefreshSidebar();
    } catch {
      alert("Failed to delete conversation.");
    }
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
        hour: "2-digit",
        minute: "2-digit"
      });
    } catch {
      return "";
    }
  };

  return (
    <aside className="w-full h-full flex flex-col glass-sidebar shrink-0 z-20 text-slate-100">
      {/* Brand Header */}
      <div className="p-6 border-b border-slate-800/40 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black tracking-tight text-white font-display flex items-center gap-1.5">
            <span className="text-gradient-title">bharat</span><span className="text-gradient-orange">ai</span>
          </h1>
          <p className="text-[8px] text-slate-400 uppercase tracking-[0.22em] font-black mt-0.5">
            India{"'"}s Sovereign Workspace
          </p>
        </div>
        <button
          onClick={() => setSidebarOpen(false)}
          className="p-1.5 rounded-xl hover:bg-slate-800/60 text-slate-400 hover:text-white transition-premium cursor-pointer border border-slate-800/60 shadow-sm bg-slate-900/60 shrink-0 flex items-center justify-center"
          title="Collapse Sidebar"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* New Chat Action Button */}
      <div className="p-4 border-b border-slate-800/40">
        <button
          onClick={handleNewConversation}
          disabled={loading}
          className="w-full py-3 px-4 bg-purple-600 hover:bg-purple-550 text-white rounded-full flex items-center justify-center gap-2 text-xs font-bold transition-premium hover:-translate-y-0.5 active:translate-y-0 active:scale-[0.98] cursor-pointer shadow-md hover:shadow-lg disabled:opacity-50"
        >
          <Plus className="w-4 h-4" />
          <span>New Conversation</span>
        </button>
      </div>

      {/* Conversation History list */}
      <div className="flex-1 overflow-y-auto scroll-smooth-premium p-4 space-y-3">
        <div className="flex items-center justify-between text-[10px] text-slate-400 font-black uppercase tracking-wider px-1 mb-2">
          <span>Conversation History</span>
          {loading && <RefreshCw className="w-3.5 h-3.5 animate-spin text-slate-400" />}
        </div>

        {error && (
          <div className="p-3 bg-red-50/70 border border-red-200/50 rounded-2xl flex items-start gap-2 text-xs text-red-650 backdrop-blur-sm">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {!loading && conversations.length === 0 && (
          <div className="h-40 flex flex-col items-center justify-center text-center p-4">
            <MessageSquare className="w-8 h-8 text-slate-300 mb-2 animate-pulse" />
            <p className="text-xs text-slate-400 font-medium">No chats started yet. Click New Conversation above to begin.</p>
          </div>
        )}

        {conversations.map((conv, index) => {
          const isSelected = activeConversationId === conv.id;
          const isLastChat = index === 0;
          const isEditing = editingConvId === conv.id;
          
          return (
            <div
              key={conv.id}
              onClick={() => {
                if (!isEditing) {
                  onSelectConversation(conv.id);
                  if (window.innerWidth < 768) {
                    setSidebarOpen(false);
                  }
                }
              }}
              className={`p-3.5 rounded-2xl cursor-pointer border transition-premium group relative overflow-hidden ${
                isSelected
                  ? "bg-purple-950/60 border-purple-800/40 shadow-md glow-primary"
                  : "bg-slate-900/30 border-transparent hover:bg-slate-800/45 hover:border-slate-800/40 hover:shadow-sm"
              }`}
            >
              {isSelected && (
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-purple-500 to-pink-500 rounded-r" />
              )}
              <div className="flex items-start gap-3 pl-1">
                <div className={`p-2.5 rounded-xl shrink-0 transition-premium ${isSelected ? "bg-purple-900/60 text-purple-400 border border-purple-800/40" : "bg-slate-800/50 text-slate-400 group-hover:text-slate-300"}`}>
                  <MessageSquare className="w-4.5 h-4.5" />
                </div>
                <div className="flex-1 min-w-0">
                  {isEditing ? (
                    <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
                      <input
                        type="text"
                        value={editingTitle}
                        onChange={(e) => setEditingTitle(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === "Enter") {
                            handleSaveRename(conv.id);
                          } else if (e.key === "Escape") {
                            setEditingConvId(null);
                          }
                        }}
                        className="w-full bg-slate-900 border border-slate-700 rounded-lg text-xs px-2 py-1 focus:outline-none focus:border-purple-500 font-medium text-slate-100"
                        autoFocus
                      />
                      <button
                        onClick={() => handleSaveRename(conv.id)}
                        className="p-1 text-emerald-600 hover:bg-emerald-50 rounded-md shrink-0"
                        title="Save"
                      >
                        <Check className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => setEditingConvId(null)}
                        className="p-1 text-slate-400 hover:bg-slate-100 rounded-md shrink-0"
                        title="Cancel"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  ) : (
                    <>
                      <h4 className="text-xs font-bold truncate text-slate-200 group-hover:text-white transition-colors">
                        {conv.title}
                      </h4>
                      <div className="flex flex-col gap-0.5 mt-1">
                        <span className="text-[9px] text-slate-400 font-medium">
                          {formatDate(conv.created_at)}
                        </span>
                        {conv.document_name && (
                          <span className="text-[9px] text-purple-400 font-bold truncate flex items-center gap-1 mt-0.5">
                            <span className="inline-block shrink-0">📄</span> {conv.document_name}
                          </span>
                        )}
                      </div>
                    </>
                  )}
                </div>
                {!isEditing && (
                  <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 focus-within:opacity-100 transition-opacity">
                    {isLastChat && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setEditingConvId(conv.id);
                          setEditingTitle(conv.title);
                        }}
                        className="p-1.5 text-slate-400 hover:text-purple-400 hover:bg-purple-950/40 rounded-lg transition-premium shrink-0"
                        title="Rename Chat"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>
                    )}
                    <button
                      onClick={(e) => handleDelete(e, conv.id)}
                      className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-950/40 rounded-lg transition-premium shrink-0"
                      title="Delete Chat"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
      {/* User Session Info & Logout */}
      <div className="p-4 border-t border-slate-800/40 bg-slate-900/60 flex flex-col gap-2 shrink-0">
        <div className="flex items-center justify-between">
          <div className="min-w-0">
            <p className="text-[10px] text-slate-400 font-extrabold uppercase tracking-wider">Account</p>
            <p className="text-xs font-bold text-slate-200 truncate max-w-[160px]">
              {typeof window !== "undefined" ? localStorage.getItem("bharatai_email") || "you@domain.com" : "you@domain.com"}
            </p>
          </div>
          <button
            onClick={onLogout}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-[10px] font-black uppercase tracking-wider cursor-pointer transition-premium shadow-sm shrink-0 border border-slate-700/60"
          >
            Log Out
          </button>
        </div>
      </div>
    </aside>
  );
}
