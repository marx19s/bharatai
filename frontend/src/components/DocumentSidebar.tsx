"use client";

import React, { useState, useEffect } from "react";
import { MessageSquare, Trash2, RefreshCw, AlertCircle, Plus, Edit2, Check, X, Compass, Folder, Bookmark, Settings, Languages } from "lucide-react";

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
  activeTab: string;
  onChangeTab: (tab: string) => void;
  language: string;
  onChangeLanguage: (lang: string) => void;
}

const LANGUAGES = [
  { id: "English", label: "English (India)" },
  { id: "Hindi", label: "हिन्दी (Hindi)" },
  { id: "Punjabi", label: "ਪੰਜਾਬੀ (Punjabi)" },
  { id: "Bengali", label: "বাংলা (Bengali)" },
  { id: "Telugu", label: "తెలుగు (Telugu)" },
  { id: "Marathi", label: "मराठी (Marathi)" },
  { id: "Tamil", label: "தமிழ் (Tamil)" },
  { id: "Urdu", label: "اردو (Urdu)" },
  { id: "Gujarati", label: "ગુજરાતી (Gujarati)" },
  { id: "Kannada", label: "ಕನ್ನಡ (Kannada)" },
  { id: "Malayalam", label: "മലയാളം (Malayalam)" },
  { id: "Odia", label: "ଓଡ଼ਿଆ (Odia)" },
  { id: "Assamese", label: "অসমীয়া (Assamese)" },
  { id: "Maithili", label: "मैथिली (Maithili)" },
  { id: "Santali", label: "संताली (Santali)" },
  { id: "Kashmiri", label: "کٲشُر (Kashmiri)" },
  { id: "Nepali", label: "नेपाली (Nepali)" },
  { id: "Konkani", label: "कोंकणी (Konkani)" },
  { id: "Sindhi", label: "سنڌي (Sindhi)" },
  { id: "Dogri", label: "डोगरी (Dogri)" },
  { id: "Manipuri", label: "মৈতৈলোন (Manipuri)" },
  { id: "Bodo", label: "बर' (Bodo)" },
  { id: "Sanskrit", label: "संस्कृतम् (Sanskrit)" }
];

export default function DocumentSidebar({
  activeConversationId,
  onSelectConversation,
  apiBaseUrl,
  refreshTrigger,
  onRefreshSidebar,
  sidebarOpen,
  setSidebarOpen,
  token,
  onLogout,
  activeTab,
  onChangeTab,
  language,
  onChangeLanguage
}: DocumentSidebarProps) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingConvId, setEditingConvId] = useState<number | null>(null);
  const [editingTitle, setEditingTitle] = useState("");
  const [memoryProject, setMemoryProject] = useState<string | null>(null);
  const [localizedLabels, setLocalizedLabels] = useState({
    lifeHub: "Life Hub",
    projects: "Projects",
    vault: "The Vault",
    settings: "Settings",
    newChat: "New Chat",
    recentChats: "Recent Chats",
    welcomeBack: "Welcome Back 👋",
    workingOn: "You were working on:",
    continueBinder: "Continue Binder",
    noChats: "No active chats. Start one above!",
    logOut: "Log Out"
  });

  // Load language settings & labels
  useEffect(() => {
    if (typeof window !== "undefined") {
      const savedLang = localStorage.getItem("yaar_language") || "English";
      
      const sidebarTranslations: Record<string, typeof localizedLabels> = {
        English: {
          lifeHub: "Life Hub",
          projects: "Projects",
          vault: "The Vault",
          settings: "Settings",
          newChat: "New Chat",
          recentChats: "Recent Chats",
          welcomeBack: "Welcome Back 👋",
          workingOn: "You were working on:",
          continueBinder: "Continue Binder",
          noChats: "No active chats. Start one above!",
          logOut: "Log Out"
        },
        Hindi: {
          lifeHub: "लाइफ हब",
          projects: "प्रोजेक्ट्स",
          vault: "द वॉल्ट",
          settings: "सेटिंग्स",
          newChat: "नया चैट",
          recentChats: "हालिया चैट",
          welcomeBack: "स्वागत है 👋",
          workingOn: "आप काम कर रहे थे:",
          continueBinder: "प्रोजेक्ट खोलें",
          noChats: "कोई सक्रिय चैट नहीं। नया शुरू करें!",
          logOut: "लॉग आउट"
        },
        Punjabi: {
          lifeHub: "ਲਾਈਫ ਹੱਬ",
          projects: "ਪ੍ਰੋਜੈਕਟਸ",
          vault: "ਦ ਵਾਲਟ",
          settings: "ਸੈਟਿੰਗਜ਼",
          newChat: "ਨਵਾਂ ਚੈਟ",
          recentChats: "ਹਾਲੀਆ ਚੈਟ",
          welcomeBack: "ਜੀ ਆਇਆਂ ਨੂੰ 👋",
          workingOn: "ਤੁਸੀਂ ਕੰਮ ਕਰ ਰਹੇ ਸੀ:",
          continueBinder: "ਪ੍ਰੋਜੈਕਟ ਖੋਲ੍ਹੋ",
          noChats: "ਕੋਈ ਚੈਟ ਨਹੀਂ ਹੈ। ਨਵਾਂ ਸ਼ੁਰੂ ਕਰੋ!",
          logOut: "ਲੌਗ ਆਊਟ"
        },
        Gujarati: {
          lifeHub: "લાઇફ હબ",
          projects: "પ્રોજેક્ટ્સ",
          vault: "ધ વૉલ્ટ",
          settings: "સેટિંગ્સ",
          newChat: "નવી ચેટ",
          recentChats: "તાજેતરની ચેટ",
          welcomeBack: "સ્વાગત છે 👋",
          workingOn: "તમે કામ કરી રહ્યા હતા:",
          continueBinder: "પ્રોજેક્ટ ખોલો",
          noChats: "કોઈ સક્રિય ચેટ નથી. નવી શરૂ કરો!",
          logOut: "લૉગ આઉટ"
        },
        Bengali: {
          lifeHub: "লাইফ হাব",
          projects: "প্রজেক্ট সমূহ",
          vault: "ভল্ট",
          settings: "সেটিংস",
          newChat: "নতুন চ্যাট",
          recentChats: "সাম্প্রতিক চ্যাট",
          welcomeBack: "স্বাগতম 👋",
          workingOn: "আপনি কাজ করছিলেন:",
          continueBinder: "প্রজেক্ট খুলুন",
          noChats: "কোন চ্যাট নেই। নতুন শুরু করুন!",
          logOut: "লগ আউট"
        },
        Tamil: {
          lifeHub: "லைஃப் ஹப்",
          projects: "திட்டங்கள்",
          vault: "தி வோல்ட்",
          settings: "அமைப்புகள்",
          newChat: "புதிய அரட்டை",
          recentChats: "சமீபத்திய அரட்டைகள்",
          welcomeBack: "வரவேற்கிறோம் 👋",
          workingOn: "நீங்கள் பணிபுரிந்தது:",
          continueBinder: "திட்டத்தை தொடரவும்",
          noChats: "அரட்டைகள் இல்லை. புதியதை தொடங்கவும்!",
          logOut: "வெளியேறு"
        }
      };

      setLocalizedLabels(sidebarTranslations[savedLang] || sidebarTranslations["English"]);
    }
  }, [refreshTrigger, activeTab]);

  // Load project memory
  useEffect(() => {
    if (typeof window !== "undefined") {
      const savedProjs = localStorage.getItem("yaar_projects");
      if (savedProjs) {
        try {
          const parsed = JSON.parse(savedProjs);
          if (parsed.length > 0) {
            setMemoryProject(parsed[0].name);
          }
        } catch (_) {}
      }
    }
  }, [refreshTrigger, activeTab]);

  const fetchConversations = async () => {
    if (!token) return;
    
    // Always load local history as first-class or fallback
    const email = localStorage.getItem("bharatai_email") || "companion@yaar.ai";
    const localChatsKey = `yaar_chats_${email}`;
    const savedLocal = localStorage.getItem(localChatsKey);
    let localList: Conversation[] = [];
    if (savedLocal) {
      try {
        localList = JSON.parse(savedLocal);
      } catch (_) {}
    }

    try {
      const res = await fetch(`${apiBaseUrl}/api/conversations`, {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        // Merge or prioritize backend
        setConversations(data);
        // Sync local storage
        localStorage.setItem(localChatsKey, JSON.stringify(data));
      } else {
        // Fallback to local
        setConversations(localList);
      }
      setError(null);
    } catch (err: unknown) {
      console.error(err);
      // Fallback
      setConversations(localList);
      setError(null); // Keep user calm, fallback succeeded
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConversations();
  }, [refreshTrigger, activeConversationId, token]);

  const handleSaveRename = async (convId: number) => {
    if (!editingTitle.trim()) return;
    const email = localStorage.getItem("bharatai_email") || "companion@yaar.ai";
    const localChatsKey = `yaar_chats_${email}`;

    // 1. Rename locally immediately
    const updated = conversations.map(c => c.id === convId ? { ...c, title: editingTitle.trim() } : c);
    setConversations(updated);
    localStorage.setItem(localChatsKey, JSON.stringify(updated));
    setEditingConvId(null);

    // 2. Sync to backend async
    try {
      await fetch(`${apiBaseUrl}/api/conversations/${convId}`, {
        method: "PUT",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ title: editingTitle.trim() })
      });
      onRefreshSidebar();
    } catch (err) {
      console.error("Rename backend sync failed:", err);
    }
  };

  const handleNewConversation = async () => {
    setLoading(true);
    const email = localStorage.getItem("bharatai_email") || "companion@yaar.ai";
    const localChatsKey = `yaar_chats_${email}`;

    // 1. Create locally immediately
    const mockId = Date.now();
    const newConv: Conversation = {
      id: mockId,
      title: "New Conversation",
      created_at: new Date().toISOString(),
      document_id: null,
      document_name: null
    };

    const updated = [newConv, ...conversations];
    setConversations(updated);
    localStorage.setItem(localChatsKey, JSON.stringify(updated));
    onSelectConversation(mockId);
    
    if (window.innerWidth < 768) {
      setSidebarOpen(false);
    }
    setLoading(false);
    onRefreshSidebar();

    // 2. Sync with backend in background
    try {
      const res = await fetch(`${apiBaseUrl}/api/conversations`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ document_id: null })
      });
      if (res.ok) {
        const data = await res.json();
        // Replace mock ID with backend ID
        const synced = updated.map(c => c.id === mockId ? { ...c, id: data.id } : c);
        setConversations(synced);
        localStorage.setItem(localChatsKey, JSON.stringify(synced));
        onSelectConversation(data.id);
        onRefreshSidebar();
      }
    } catch (err) {
      console.error("Sync new chat failed:", err);
    }
  };

  const handleDelete = async (e: React.MouseEvent, convId: number) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this conversation session? All its messages will be deleted.")) return;

    const email = localStorage.getItem("bharatai_email") || "companion@yaar.ai";
    const localChatsKey = `yaar_chats_${email}`;

    // 1. Delete locally immediately
    const updated = conversations.filter(c => c.id !== convId);
    setConversations(updated);
    localStorage.setItem(localChatsKey, JSON.stringify(updated));

    // Delete associated messages from local storage
    localStorage.removeItem(`yaar_messages_${convId}`);

    if (activeConversationId === convId) {
      onSelectConversation(null);
      onChangeTab("lifehub");
    }
    onRefreshSidebar();

    // 2. Sync backend delete
    try {
      await fetch(`${apiBaseUrl}/api/conversations/${convId}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
    } catch (err) {
      console.error("Backend delete sync failed:", err);
    }
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short"
      });
    } catch {
      return "";
    }
  };

  return (
    <aside className="w-full h-full flex flex-col glass-sidebar shrink-0 z-20 text-slate-100 bg-[#121316]">
      
      {/* Brand Header */}
      <div className="p-5 border-b border-white/5 flex items-center justify-between">
        <div>
          <h1 className="text-xl sm:text-2xl font-black tracking-tight text-white font-display flex items-center gap-1.5">
            <span className="text-gradient-title">yaar</span>
            <span className="text-[10px] uppercase font-mono tracking-widest text-slate-500 bg-slate-900 border border-slate-800/50 px-1.5 py-0.5 rounded ml-1">v1.0</span>
          </h1>
          <p className="text-[8px] text-slate-400 uppercase tracking-[0.22em] font-black mt-0.5">
            Your Digital Companion
          </p>
        </div>
        <button
          onClick={() => setSidebarOpen(false)}
          className="p-1.5 rounded-xl hover:bg-slate-800/60 text-slate-400 hover:text-white transition-premium cursor-pointer border border-white/5 shadow-sm bg-slate-900/60 md:hidden shrink-0 flex items-center justify-center"
          title="Collapse Sidebar"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Memory Welcome Box */}
      {memoryProject && activeConversationId === null && (
        <div className="mx-4 mt-4 p-3.5 rounded-2xl bg-amber-950/20 border border-amber-900/20 flex flex-col gap-1.5">
          <p className="text-[10px] text-amber-500 font-extrabold uppercase tracking-wider">{localizedLabels.welcomeBack}</p>
          <p className="text-[11px] text-slate-350 font-semibold leading-relaxed">
            {localizedLabels.workingOn}<br/>
            <span className="text-white font-bold text-xs">{memoryProject}</span>
          </p>
          <button
            onClick={() => onChangeTab("projects")}
            className="text-[10px] text-amber-550 hover:text-white font-black uppercase tracking-wider text-left flex items-center gap-1 pt-1 transition-colors"
          >
            {localizedLabels.continueBinder} <Plus className="w-3 h-3 rotate-45" />
          </button>
        </div>
      )}

      {/* Sidebar Core Companion Navigation Tabs */}
      <div className="p-4 space-y-1">
        <button
          onClick={() => {
            onSelectConversation(null);
            onChangeTab("lifehub");
            if (window.innerWidth < 768) setSidebarOpen(false);
          }}
          className={`w-full py-2.5 px-4 rounded-xl flex items-center gap-3 text-xs font-bold transition-premium cursor-pointer ${
            activeConversationId === null && activeTab === "lifehub"
              ? "bg-amber-950/30 border border-amber-500/30 text-amber-500 font-black"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/45 border border-transparent"
          }`}
        >
          <Compass className="w-4.5 h-4.5" />
          <span>{localizedLabels.lifeHub}</span>
        </button>

        <button
          onClick={() => {
            onSelectConversation(null);
            onChangeTab("projects");
            if (window.innerWidth < 768) setSidebarOpen(false);
          }}
          className={`w-full py-2.5 px-4 rounded-xl flex items-center gap-3 text-xs font-bold transition-premium cursor-pointer ${
            activeConversationId === null && activeTab === "projects"
              ? "bg-amber-950/30 border border-amber-500/30 text-amber-500 font-black"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/45 border border-transparent"
          }`}
        >
          <Folder className="w-4.5 h-4.5" />
          <span>{localizedLabels.projects}</span>
        </button>

        <button
          onClick={() => {
            onSelectConversation(null);
            onChangeTab("vault");
            if (window.innerWidth < 768) setSidebarOpen(false);
          }}
          className={`w-full py-2.5 px-4 rounded-xl flex items-center gap-3 text-xs font-bold transition-premium cursor-pointer ${
            activeConversationId === null && activeTab === "vault"
              ? "bg-amber-950/30 border border-amber-500/30 text-amber-500 font-black"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/45 border border-transparent"
          }`}
        >
          <Bookmark className="w-4.5 h-4.5" />
          <span>{localizedLabels.vault}</span>
        </button>

        <button
          onClick={() => {
            onSelectConversation(null);
            onChangeTab("settings");
            if (window.innerWidth < 768) setSidebarOpen(false);
          }}
          className={`w-full py-2.5 px-4 rounded-xl flex items-center gap-3 text-xs font-bold transition-premium cursor-pointer ${
            activeConversationId === null && activeTab === "settings"
              ? "bg-amber-950/30 border border-amber-500/30 text-amber-500 font-black"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/45 border border-transparent"
          }`}
        >
          <Settings className="w-4.5 h-4.5" />
          <span>{localizedLabels.settings}</span>
        </button>
      </div>

      {/* Action Button: Start Chat */}
      <div className="px-4 pb-4 border-b border-white/5">
        <button
          onClick={handleNewConversation}
          disabled={loading}
          className="w-full py-3 px-4 bg-amber-600 hover:bg-amber-500 text-white rounded-xl flex items-center justify-center gap-2 text-xs font-bold transition-premium hover:-translate-y-0.5 active:translate-y-0 cursor-pointer shadow-md disabled:opacity-50"
        >
          <Plus className="w-4 h-4" />
          <span>{localizedLabels.newChat}</span>
        </button>
      </div>

      {/* History Conversations list */}
      <div className="flex-1 overflow-y-auto scroll-smooth-premium p-4 space-y-3">
        <div className="flex items-center justify-between text-[9px] text-slate-500 font-black uppercase tracking-widest px-1 mb-1">
          <span>{localizedLabels.recentChats}</span>
          {loading && <RefreshCw className="w-3 h-3 animate-spin text-slate-500" />}
        </div>

        {error && (
          <div className="p-3 bg-red-950/20 border border-red-900/30 rounded-xl flex items-start gap-2 text-[10px] text-red-400">
            <AlertCircle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {!loading && conversations.length === 0 && (
          <div className="py-8 text-center px-2">
            <p className="text-[10px] text-slate-500 font-medium">{localizedLabels.noChats}</p>
          </div>
        )}

        {conversations.map((conv) => {
          const isSelected = activeConversationId === conv.id;
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
              className={`p-3 rounded-xl cursor-pointer border transition-premium group relative overflow-hidden ${
                isSelected
                  ? "bg-slate-900 border-white/5 shadow-md"
                  : "bg-transparent border-transparent hover:bg-slate-900/30 hover:border-white/5"
              }`}
            >
              {isSelected && (
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-amber-500 rounded-r" />
              )}
              <div className="flex items-start gap-2.5 pl-0.5">
                <div className={`p-1.5 rounded-lg shrink-0 transition-premium ${isSelected ? "text-amber-500" : "text-slate-500 group-hover:text-slate-400"}`}>
                  <MessageSquare className="w-4 h-4" />
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
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg text-[11px] px-2 py-0.5 focus:outline-none focus:border-amber-500 font-medium text-slate-100"
                        autoFocus
                      />
                      <button
                        onClick={() => handleSaveRename(conv.id)}
                        className="p-1 text-emerald-500 hover:bg-slate-800 rounded-md shrink-0"
                      >
                        <Check className="w-3 h-3" />
                      </button>
                      <button
                        onClick={() => setEditingConvId(null)}
                        className="p-1 text-slate-400 hover:bg-slate-800 rounded-md shrink-0"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  ) : (
                    <>
                      <h4 className="text-[11px] font-bold truncate text-slate-350 group-hover:text-slate-150 transition-colors">
                        {conv.title}
                      </h4>
                      <div className="flex items-center justify-between gap-2 mt-0.5">
                        <span className="text-[9px] text-slate-500 font-mono">
                          {formatDate(conv.created_at)}
                        </span>
                        {conv.document_name && (
                          <span className="text-[9px] text-amber-550 font-bold truncate max-w-[80px]">
                            📄 {conv.document_name}
                          </span>
                        )}
                      </div>
                    </>
                  )}
                </div>

                {!isEditing && (
                  <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setEditingConvId(conv.id);
                        setEditingTitle(conv.title);
                      }}
                      className="p-1 text-slate-500 hover:text-amber-500 rounded transition-premium shrink-0"
                      title="Rename Chat"
                    >
                      <Edit2 className="w-3 h-3" />
                    </button>
                    <button
                      onClick={(e) => handleDelete(e, conv.id)}
                      className="p-1 text-slate-500 hover:text-rose-450 rounded transition-premium shrink-0"
                      title="Delete Chat"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Account Profile Session / Logout */}
      <div className="p-4 border-t border-white/5 bg-slate-950/20 flex flex-col gap-2 shrink-0">
        <div className="flex items-center justify-between">
          <div className="min-w-0">
            <p className="text-[8px] text-slate-500 font-extrabold uppercase tracking-wider">Account</p>
            <p className="text-xs font-bold text-slate-400 truncate max-w-[140px]">
              {typeof window !== "undefined" ? localStorage.getItem("bharatai_email") || "companion@yaar.ai" : "companion@yaar.ai"}
            </p>
          </div>
          <button
            onClick={onLogout}
            className="px-2.5 py-1.5 bg-slate-900 hover:bg-slate-800 text-slate-350 hover:text-white rounded-lg text-[10px] font-bold uppercase tracking-wider cursor-pointer transition-premium border border-white/5"
          >
            {localizedLabels.logOut}
          </button>
        </div>

        <div className="flex items-center justify-between border-t border-white/5 pt-2 mt-1">
          <span className="text-[8px] text-slate-500 font-extrabold uppercase tracking-wider flex items-center gap-1">
            <Languages className="w-3 h-3 text-slate-450" /> Language
          </span>
          <select
            value={language}
            onChange={(e) => {
              const newLang = e.target.value;
              onChangeLanguage(newLang);
            }}
            className="bg-slate-900 border border-white/5 rounded px-2 py-0.5 text-[10px] font-bold text-slate-300 outline-none cursor-pointer hover:text-white"
          >
            {LANGUAGES.map((l) => (
              <option key={l.id} value={l.id} className="bg-[#121316] text-white">
                {l.label}
              </option>
            ))}
          </select>
        </div>
      </div>

    </aside>
  );
}
