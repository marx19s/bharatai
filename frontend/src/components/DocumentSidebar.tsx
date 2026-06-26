"use client";

import React, { useState, useEffect } from "react";
import { MessageSquare, Trash2, RefreshCw, AlertCircle, Plus, Edit2, Check, X, Compass, Folder, Bookmark, Settings, Languages, Home, Menu, LogOut } from "lucide-react";

interface Conversation {
  id: number;
  title: string;
  created_at: string;
  document_id: number | null;
  document_name: string | null;
}

// 6. TEST DATA SCHEMES FOR VERIFICATION

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

const DEFAULT_LABELS = {
  lifeHub: "Life Hub",
  projects: "Projects",
  vault: "The Vault",
  settings: "Settings",
  translation: "Translation",
  newChat: "New Chat",
  recentChats: "Recent Chats",
  welcomeBack: "Welcome Back 👋",
  workingOn: "You were working on:",
  continueBinder: "Continue Binder",
  noChats: "No active chats. Start one above!",
  logOut: "Log Out"
};

const getTranslationPack = (lang: string) => {
  const translations: Record<string, { sidebar: typeof DEFAULT_LABELS }> = {
    English: {
      sidebar: DEFAULT_LABELS
    },
    Hindi: {
      sidebar: {
        lifeHub: "लाइफ़ हब",
        projects: "प्रोजेक्ट्स",
        vault: "द वॉल्ट",
        settings: "सेटिंग्स",
        translation: "अनुवाद",
        newChat: "नया चैट",
        recentChats: "हाल के चैट",
        welcomeBack: "स्वागत है दोस्त 👋",
        workingOn: "आप इस पर काम कर रहे थे:",
        continueBinder: "बाइंडर जारी रखें",
        noChats: "कोई सक्रिय चैट नहीं। ऊपर शुरू करें!",
        logOut: "लॉग आउट"
      }
    },
    Punjabi: {
      sidebar: {
        lifeHub: "ਲਾਈਫ਼ ਹੱਬ",
        projects: "ਪ੍ਰੋਜੈਕਟਸ",
        vault: "ਦਾ ਵਾਲ੍ਟ",
        settings: "ਸੈਟਿੰਗਾਂ",
        translation: "ਅਨੁਵਾਦ",
        newChat: "ਨਵਾਂ ਚੈਟ",
        recentChats: "ਤਾਜ਼ਾ ਚੈਟ",
        welcomeBack: "ਜੀ ਆਇਆਂ ਨੂੰ ਵੀਰੇ 👋",
        workingOn: "ਤੁਸੀਂ ਇਸ 'ਤੇ ਕੰਮ ਕਰ ਰਹੇ ਸੀ:",
        continueBinder: "ਬਾਈਂਡਰ ਜਾਰੀ ਰੱਖੋ",
        noChats: "ਕੋਈ ਸਰਗਰਮ ਚੈਟ ਨਹੀਂ। ਉੱਪਰ ਸ਼ੁਰੂ ਕਰੋ!",
        logOut: "ਲੌਗ ਆਉਟ"
      }
    },
    Bengali: {
      sidebar: {
        lifeHub: "লাইফ হাব",
        projects: "প্রকল্প",
        vault: "ভল্ট",
        settings: "সেটিংস",
        translation: "অনুবাদ",
        newChat: "নতুন চ্যাট",
        recentChats: "সাম্প্রতিক চ্যাট",
        welcomeBack: "স্বাগতম বন্ধু 👋",
        workingOn: "আপনি এটিটিতে কাজ করছিলেন:",
        continueBinder: "বাইন্ডার চালিয়ে যান",
        noChats: "কোনো চ্যাট নেই। উপরে শুরু করুন!",
        logOut: "লগ আউট"
      }
    },
    Tamil: {
      sidebar: {
        lifeHub: "லைப் ஹப்",
        projects: "திட்டங்கள்",
        vault: "வால்ட்",
        settings: "அமைப்புகள்",
        translation: "மொழிபெயர்ப்பு",
        newChat: "புதிய அரட்டை",
        recentChats: "சமீபத்திய அரட்டைகள்",
        welcomeBack: "வரவேற்கிறோம் நண்பா 👋",
        workingOn: "நீங்கள் வேலை செய்து கொண்டிருந்தது:",
        continueBinder: "பைண்டரைத் தொடரவும்",
        noChats: "செயலில் அரட்டைகள் இல்லை. மேலே தொடங்கவும்!",
        logOut: "வெளியேறு"
      }
    },
    Gujarati: {
      sidebar: {
        lifeHub: "લાઇફ ਹับ",
        projects: "પ્રોજેક્ટ્સ",
        vault: "વોલ્ટ",
        settings: "સેટિંગ્સ",
        translation: "અનુવાદ",
        newChat: "નવી ચેટ",
        recentChats: "તાજેતરની ચેટ",
        welcomeBack: "સ્વાગત છે મિત્ર 👋",
        workingOn: "તમે આના પર કામ કરી રહ્યા હતા:",
        continueBinder: "બાઇન્ડર ચાલુ રાખો",
        noChats: "કોઈ સક્રિય ચેટ નથી. ઉપરથી શરૂ કરો!",
        logOut: "લોગ આઉટ"
      }
    }
  };
  return translations[lang] || translations["English"];
};

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
  const [welcomeDismissed, setWelcomeDismissed] = useState(false);
  const [localizedLabels, setLocalizedLabels] = useState({
    lifeHub: "Life Hub",
    projects: "Projects",
    vault: "The Vault",
    settings: "Settings",
    translation: "Translation",
    newChat: "New Chat",
    recentChats: "Recent Chats",
    welcomeBack: "Welcome Back 👋",
    workingOn: "You were working on:",
    continueBinder: "Continue Binder",
    noChats: "No active chats. Start one above!",
    logOut: "Log Out"
  });
  const [logoClicks, setLogoClicks] = useState(0);
  const handleLogoClick = () => {
    const nextClicks = logoClicks + 1;
    if (nextClicks >= 5) {
      setLogoClicks(0);
      if (typeof window !== "undefined") {
        const current = localStorage.getItem("yaar_beta_tester_mode") === "true";
        const newVal = !current;
        localStorage.setItem("yaar_beta_tester_mode", newVal ? "true" : "false");
        window.dispatchEvent(new Event("yaar_beta_mode_changed"));
      }
    } else {
      setLogoClicks(nextClicks);
    }
  };

  useEffect(() => {
    if (logoClicks > 0) {
      const timer = setTimeout(() => setLogoClicks(0), 2500);
      return () => clearTimeout(timer);
    }
  }, [logoClicks]);  // Load language settings & labels
  useEffect(() => {
    if (typeof window !== "undefined") {
      const savedLang = localStorage.getItem("yaar_language") || "English";
      const pack = getTranslationPack(savedLang);
      if (pack && pack.sidebar) {
        setLocalizedLabels(pack.sidebar);
      }
    }
  }, [refreshTrigger, activeTab, language]);

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

  if (!sidebarOpen) {
    const email = typeof window !== "undefined" ? localStorage.getItem("bharatai_email") || "companion@yaar.ai" : "companion@yaar.ai";
    return (
      <aside className="w-full h-full flex flex-col items-center justify-between py-4 glass-sidebar shrink-0 z-20 text-slate-100 bg-[#121316] select-none animate-zoom-in-fade">
        {/* Top Header */}
        <div className="flex flex-col items-center gap-4 w-full border-b border-white/5 pb-4 px-2">
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-2 rounded-xl hover:bg-slate-800/60 text-slate-400 hover:text-white transition-premium cursor-pointer border border-white/5 shadow-sm bg-slate-900/60 flex items-center justify-center"
            title="Expand Sidebar"
          >
            <Menu className="w-4.5 h-4.5" />
          </button>
          
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-amber-600 to-rose-500 flex items-center justify-center font-black text-sm text-white shadow-md">
            अ
          </div>
        </div>

        {/* Navigation Tabs (centered textless icons) */}
        <div className="flex-1 w-full py-4 flex flex-col items-center gap-2">
          <button
            onClick={() => {
              onSelectConversation(null);
              onChangeTab("home");
            }}
            className={`p-2.5 rounded-xl transition-premium cursor-pointer flex items-center justify-center ${
              activeConversationId === null && activeTab === "home"
                ? "bg-amber-950/40 border border-amber-500/40 text-amber-500"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/45 border border-transparent"
            }`}
            title="Home"
          >
            <Home className="w-4.5 h-4.5" />
          </button>

          <button
            onClick={() => {
              onSelectConversation(null);
              onChangeTab("lifehub");
            }}
            className={`p-2.5 rounded-xl transition-premium cursor-pointer flex items-center justify-center ${
              activeConversationId === null && activeTab === "lifehub"
                ? "bg-amber-950/40 border border-amber-500/40 text-amber-500"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/45 border border-transparent"
            }`}
            title={localizedLabels.lifeHub}
          >
            <Compass className="w-4.5 h-4.5" />
          </button>

          <button
            onClick={() => {
              onSelectConversation(null);
              onChangeTab("projects");
            }}
            className={`p-2.5 rounded-xl transition-premium cursor-pointer flex items-center justify-center ${
              activeConversationId === null && activeTab === "projects"
                ? "bg-amber-950/40 border border-amber-500/40 text-amber-500"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/45 border border-transparent"
            }`}
            title={localizedLabels.projects}
          >
            <Folder className="w-4.5 h-4.5" />
          </button>

          <button
            onClick={() => {
              onSelectConversation(null);
              onChangeTab("vault");
            }}
            className={`p-2.5 rounded-xl transition-premium cursor-pointer flex items-center justify-center ${
              activeConversationId === null && activeTab === "vault"
                ? "bg-amber-950/40 border border-amber-500/40 text-amber-500"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/45 border border-transparent"
            }`}
            title={localizedLabels.vault}
          >
            <Bookmark className="w-4.5 h-4.5" />
          </button>

          <button
            onClick={() => {
              onSelectConversation(null);
              onChangeTab("translate");
            }}
            className={`p-2.5 rounded-xl transition-premium cursor-pointer flex items-center justify-center ${
              activeConversationId === null && activeTab === "translate"
                ? "bg-amber-950/40 border border-amber-500/40 text-amber-500"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/45 border border-transparent"
            }`}
            title={localizedLabels.translation || "Translation"}
          >
            <Languages className="w-4.5 h-4.5" />
          </button>

          <button
            onClick={() => {
              onSelectConversation(null);
              onChangeTab("settings");
            }}
            className={`p-2.5 rounded-xl transition-premium cursor-pointer flex items-center justify-center ${
              activeConversationId === null && activeTab === "settings"
                ? "bg-amber-950/40 border border-amber-500/40 text-amber-500"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/45 border border-transparent"
            }`}
            title={localizedLabels.settings}
          >
            <Settings className="w-4.5 h-4.5" />
          </button>

          <div className="w-full border-t border-white/5 my-2" />

          {/* New Chat circular button */}
          <button
            onClick={handleNewConversation}
            disabled={loading}
            className="p-2.5 bg-amber-600 hover:bg-amber-500 text-white rounded-xl flex items-center justify-center transition-premium hover:-translate-y-0.5 active:translate-y-0 cursor-pointer shadow-md disabled:opacity-50"
            title={localizedLabels.newChat}
          >
            <Plus className="w-4.5 h-4.5" />
          </button>
        </div>

        {/* Bottom Profile / Logout */}
        <div className="w-full border-t border-white/5 pt-4 flex flex-col items-center gap-3 px-2">
          <div className="w-8 h-8 rounded-full bg-slate-800 border border-white/10 flex items-center justify-center text-xs font-black text-amber-500" title={email}>
            {email[0].toUpperCase()}
          </div>
          
          <button
            onClick={onLogout}
            className="p-2 bg-slate-900 hover:bg-slate-800 text-rose-500 rounded-xl flex items-center justify-center border border-white/5 transition-premium cursor-pointer"
            title={localizedLabels.logOut}
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </aside>
    );
  }

  return (
    <aside className="w-full h-full flex flex-col glass-sidebar shrink-0 z-20 text-slate-100 bg-[#121316]">
      
      {/* Brand Header */}
      <div 
        onClick={handleLogoClick}
        className="p-5 border-b border-white/5 flex items-center justify-between cursor-pointer select-none"
      >
        <div>
          <h1 className="text-xl sm:text-2xl font-black tracking-tight text-white font-display flex items-center gap-1.5">
            <span className="text-gradient-title">Bharat AI</span>
            <span className="text-[10px] uppercase font-mono tracking-widest text-slate-500 bg-slate-900 border border-slate-800/50 px-1.5 py-0.5 rounded ml-1">Platform</span>
          </h1>
          <p className="text-[8px] text-slate-400 uppercase tracking-[0.22em] font-black mt-0.5">
            Bharat AI Technology
          </p>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            setSidebarOpen(false);
          }}
          className="p-1.5 rounded-xl hover:bg-slate-800/60 text-slate-400 hover:text-white transition-premium cursor-pointer border border-white/5 shadow-sm bg-slate-900/60 shrink-0 flex items-center justify-center"
          title="Collapse Sidebar"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Memory Welcome Box */}
      {memoryProject && activeConversationId === null && !welcomeDismissed && (
        <div className="mx-4 mt-4 p-3.5 rounded-2xl bg-amber-950/20 border border-amber-900/20 flex flex-col gap-1.5 relative">
          <button
            onClick={() => setWelcomeDismissed(true)}
            className="absolute top-2.5 right-2.5 p-0.5 rounded text-slate-500 hover:text-white hover:bg-slate-900 transition-colors cursor-pointer"
            title="Dismiss"
          >
            <X className="w-3 h-3" />
          </button>
          <p className="text-[10px] text-amber-500 font-extrabold uppercase tracking-wider pr-6">{localizedLabels.welcomeBack}</p>
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
            onChangeTab("home");
            if (window.innerWidth < 768) setSidebarOpen(false);
          }}
          className={`w-full py-2.5 px-4 rounded-xl flex items-center gap-3 text-xs font-bold transition-premium cursor-pointer ${
            activeConversationId === null && activeTab === "home"
              ? "bg-amber-950/30 border border-amber-500/30 text-amber-500 font-black"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/45 border border-transparent"
          }`}
        >
          <Home className="w-4.5 h-4.5" />
          <span>Home</span>
        </button>

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
            onChangeTab("translate");
            if (window.innerWidth < 768) setSidebarOpen(false);
          }}
          className={`w-full py-2.5 px-4 rounded-xl flex items-center gap-3 text-xs font-bold transition-premium cursor-pointer ${
            activeConversationId === null && activeTab === "translate"
              ? "bg-amber-950/30 border border-amber-500/30 text-amber-500 font-black"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/45 border border-transparent"
          }`}
        >
          <Languages className="w-4.5 h-4.5" />
          <span>{localizedLabels.translation || "Translation"}</span>
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
          <Plus className="w-4.5 h-4.5" />
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
                          <span className="text-[9px] text-amber-555 font-bold truncate max-w-[80px]">
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
                      className="p-1 text-slate-500 hover:text-rose-455 rounded transition-premium shrink-0"
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

        {/* Relocated Other Products Block */}
        <div className="border-t border-white/5 my-4 pt-4 space-y-2 select-none">
          <span className="text-[9px] text-slate-500 font-black uppercase tracking-widest block pl-1">Other Products</span>
          
          <div className="space-y-1.5 font-sans">
            <div className="flex items-center justify-between p-2 rounded-xl bg-slate-900/10 border border-white/5 opacity-55 text-slate-450">
              <div className="flex items-center gap-2 text-[10px] font-bold">
                <span className="text-xs">📚</span>
                <span>BIRBAL</span>
              </div>
              <span className="text-[7px] uppercase font-mono tracking-wider bg-slate-950 border border-slate-850 px-1.5 py-0.5 rounded text-amber-500">Coming</span>
            </div>

            <div className="flex items-center justify-between p-2 rounded-xl bg-slate-900/10 border border-white/5 opacity-55 text-slate-450">
              <div className="flex items-center gap-2 text-[10px] font-bold">
                <span className="text-xs">🎙️</span>
                <span>UDAAN</span>
              </div>
              <span className="text-[7px] uppercase font-mono tracking-wider bg-slate-950 border border-slate-850 px-1.5 py-0.5 rounded text-amber-500">Coming</span>
            </div>

            <div className="flex items-center justify-between p-2 rounded-xl bg-slate-900/10 border border-white/5 opacity-55 text-slate-450">
              <div className="flex items-center gap-2 text-[10px] font-bold">
                <span className="text-xs">⚡</span>
                <span>SUTRA</span>
              </div>
              <span className="text-[7px] uppercase font-mono tracking-wider bg-slate-950 border border-slate-850 px-1.5 py-0.5 rounded text-amber-500">Coming</span>
            </div>
          </div>
        </div>
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
      </div>

    </aside>
  );
}
