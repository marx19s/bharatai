"use client";

import React, { useEffect, useState } from "react";
import { MessageSquare, Folder, Bookmark, ArrowRight, ShieldCheck, Sparkles, Clock, Search, Target } from "lucide-react";
import YaarOrb from "./YaarOrb";

interface LifeHubPanelProps {
  token: string | null;
  apiBaseUrl: string;
  onSelectConversation: (id: number | null) => void;
  onNewChat: () => void;
  onNavigateToSection: (section: string) => void;
}

const LOCALIZED_DASHBOARD: Record<string, {
  todayTitle: string;
  continueJourney: string;
  recentDiscoveries: string;
  projectsLabel: string;
  vaultLabel: string;
  viewAll: string;
  newChat: string;
  newChatDesc: string;
  resumeBanner: string;
  resumeBtn: string;
  trustTitle: string;
  trustDesc: string;
  inspiration: string;
}> = {
  English: {
    todayTitle: "Today",
    continueJourney: "Continue Journey",
    recentDiscoveries: "Recent Discoveries",
    projectsLabel: "Active Binders",
    vaultLabel: "Second Brain Vault",
    viewAll: "View All",
    newChat: "Start a new companion session",
    newChatDesc: "Connect with Yaar to get assistance on any topic.",
    resumeBanner: "Last time we were working on:",
    resumeBtn: "Resume Session",
    trustTitle: "Sovereign Trust Safeguard",
    trustDesc: "All chat sessions are saved locally on your device. We never use your conversations for AI training.",
    inspiration: "Progress is made one small step at a time. What are we discovering today?"
  },
  Hindi: {
    todayTitle: "आज",
    continueJourney: "अपनी यात्रा जारी रखें",
    recentDiscoveries: "हालिया खोजें",
    projectsLabel: "सक्रिय बाइंडर्स",
    vaultLabel: "वॉल्ट सेकंड ब्रेन",
    viewAll: "सभी देखें",
    newChat: "यार के साथ नयी चर्चा शुरू करें",
    newChatDesc: "किसी भी विषय पर सलाह या सहायता के लिए यार से जुड़ें।",
    resumeBanner: "पिछली बार हम इस पर काम कर रहे थे:",
    resumeBtn: "काम जारी रखें",
    trustTitle: "संप्रभु सुरक्षा गारंटी",
    trustDesc: "आपके सभी संवाद सुरक्षित रूप से स्थानीय डिवाइस पर संग्रहीत हैं। प्रशिक्षण के लिए कोई डेटा उपयोग नहीं होता।",
    inspiration: "प्रगति हर रोज़ छोटे कदमों से होती है। आज हम क्या नया करने वाले हैं?"
  },
  Punjabi: {
    todayTitle: "ਅੱਜ",
    continueJourney: "ਆਪਣਾ ਸਫ਼ਰ ਜਾਰੀ ਰੱਖੋ",
    recentDiscoveries: "ਹਾਲੀਆ ਖੋਜਾਂ",
    projectsLabel: "ਸਰਗਰਮ ਬਾਈਂਡਰ",
    vaultLabel: "ਵਾਲਟ ਸੈਕਿੰਡ ਬ੍ਰੇਨ",
    viewAll: "ਸਭ ਦੇਖੋ",
    newChat: "ਯਾਰ ਨਾਲ ਨਵੀਂ ਗੱਲਬਾਤ",
    newChatDesc: "ਕਿਸੇ ਵੀ ਵਿਸ਼ੇ 'ਤੇ ਸਹਾਇਤਾ ਲਈ ਆਪਣੇ ਯਾਰ ਨਾਲ ਜੁੜੋ।",
    resumeBanner: "ਪਿਛਲੀ ਵਾਰ ਅਸੀਂ ਇਸ 'ਤੇ ਕੰਮ ਕਰ ਰਹੇ ਸੀ:",
    resumeBtn: "ਸਫ਼ਰ ਜਾਰੀ ਰੱਖੋ",
    trustTitle: "ਸੰਪ੍ਰਭੂ ਸੁਰੱਖਿਆ ਗਾਰੰਟੀ",
    trustDesc: "ਤੁਹਾਡੀਆਂ ਸਾਰੀਆਂ ਚੈਟਾਂ ਤੁਹਾਡੇ ਆਪਣੇ ਮੋਬਾਈਲ 'ਤੇ ਸੁਰੱਖਿਅਤ ਹਨ। ਅਸੀਂ AI ਟ੍ਰੇਨਿੰਗ ਲਈ ਡਾਟਾ ਨਹੀਂ ਵਰਤਦੇ।",
    inspiration: "ਤਰੱਕੀ ਰੋਜ਼ਾਨਾ ਛੋਟੇ ਕਦਮਾਂ ਨਾਲ ਹੁੰਦੀ ਹੈ। ਅੱਜ ਅਸੀਂ ਕੀ ਨਵਾਂ ਕਰਨ ਜਾ ਰਹੇ ਹਾਂ?"
  },
  Gujarati: {
    todayTitle: "આજે",
    continueJourney: "યાત્રા ચાલુ રાખો",
    recentDiscoveries: "તાજેતરની શોધખોળો",
    projectsLabel: "સક્રિય બાઈન્ડર્સ",
    vaultLabel: "વૉલ્ટ સેકન્ડ બ્રેન",
    viewAll: "બધા જુઓ",
    newChat: "નવી ચેટ શરૂ કરો",
    newChatDesc: "કોઈપણ વિષય પર સહાય મેળવવા માટે તમારા યાર સાથે જોડાઓ.",
    resumeBanner: "છેલ્લી વખત આપણે આના પર કામ કરી રહ્યા હતા:",
    resumeBtn: "કામ ફરી શરૂ કરો",
    trustTitle: "સાર્વભૌમ સુરક્ષા ગેરંટી",
    trustDesc: "તમારી બધી ચેટ્સ તમારા ઉપકરણ પર સુરક્ષિત રીતે સંગ્રહિત છે. AI તાલીમ માટે ડેટાનો ઉપયોગ થતો નથી.",
    inspiration: "પ્રગતિ દરરોજ નાના પગલાઓથી થાય છે. આજે આપણે શું નવું શોધીશું?"
  },
  Bengali: {
    todayTitle: "আজ",
    continueJourney: "আপনার যাত্রা জারি রাখুন",
    recentDiscoveries: "সাম্প্রতিক আবিষ্কার",
    projectsLabel: "সক্রিয় বাইন্ডার সমূহ",
    vaultLabel: "ভল্ট সেকেন্ড ব্রেন",
    viewAll: "সব দেখুন",
    newChat: "নতুন ইয়ার সেশন শুরু করুন",
    newChatDesc: "যেকোনো বিষয়ে সাহায্যের জন্য ইয়ারের সাথে সরাসরি যুক্ত হন।",
    resumeBanner: "গত সেশনে আমরা কাজ করছিলাম:",
    resumeBtn: "সেশন আবার শুরু করুন",
    trustTitle: "সার্বভৌম সুরক্ষা গ্যারান্টি",
    trustDesc: "আপনার সমস্ত চ্যাট আপনার ডিভাইসে সুরক্ষিতভাবে সংরক্ষিত থাকে। এআই মডেল প্রশিক্ষণের জন্য ব্যবহার করা হয় না।",
    inspiration: "প্রতিটি ছোট পদক্ষেপই এগিয়ে নিয়ে যায়। আজ আমরা কি নতুন শিখব?"
  },
  Tamil: {
    todayTitle: "இன்று",
    continueJourney: "பயணத்தைத் தொடரவும்",
    recentDiscoveries: "சமீபத்திய கண்டுபிடிப்புகள்",
    projectsLabel: "செயலில் உள்ள திட்டங்கள்",
    vaultLabel: "தி வோல்ட் நினைவகம்",
    viewAll: "அனைத்தையும் பார்",
    newChat: "புதிய யார் அரட்டையைத் தொடங்கு",
    newChatDesc: "எந்தவொரு தலைப்பிலும் உதவி பெற உங்கள் யாருடன் இணையுங்கள்.",
    resumeBanner: "கடந்த முறை நாம் பணிபுரிந்தது:",
    resumeBtn: "பணியைத் தொடரவும்",
    trustTitle: "இறையாண்மை பாதுகாப்பு உத்தரவாதம்",
    trustDesc: "உங்கள் உரையாடல்கள் அனைத்தும் சாதனத்திலேயே சேமிக்கப்படும். AI பயிற்சிக்கு பயன்படுத்தப்படாது.",
    inspiration: "முன்னேற்றம் என்பது சிறு படிகளிலேயே ஆரம்பமாகிறது. இன்று நாம் என்ன கற்கப் போகிறோம்?"
  }
};

export default function LifeHubPanel({
  token,
  apiBaseUrl,
  onSelectConversation,
  onNewChat,
  onNavigateToSection
}: LifeHubPanelProps) {
  const [userName, setUserName] = useState("Friend");
  const [language, setLanguage] = useState("English");
  const [vibe, setVibe] = useState("friendly");

  const [recentChats, setRecentChats] = useState<any[]>([]);
  const [recentProjects, setRecentProjects] = useState<any[]>([]);
  const [recentVaultItems, setRecentVaultItems] = useState<any[]>([]);
  const [lastWorkedItem, setLastWorkedItem] = useState<{ type: "chat" | "project"; name: string; id: any } | null>(null);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);
  const [companionProfile, setCompanionProfile] = useState<any | null>(null);
  const [toastMsg, setToastMsg] = useState<string | null>(null);

  // Dynamic Date string localized
  const getFormattedDate = () => {
    const today = new Date();
    const locales: Record<string, string> = {
      English: "en-IN",
      Hindi: "hi-IN",
      Punjabi: "pa-IN",
      Gujarati: "gu-IN",
      Bengali: "bn-IN",
      Tamil: "ta-IN"
    };
    return today.toLocaleDateString(locales[language] || "en-IN", {
      weekday: "long",
      day: "numeric",
      month: "long",
      year: "numeric"
    });
  };

  // Personalized Welcome greetings
  const getLocalizedWelcome = () => {
    const nameToUse = userName || "Friend";
    switch (language) {
      case "Hindi":
        return vibe === "formal" ? `प्रणाम, ${nameToUse} 🙏` : vibe === "regional" ? `राम राम, ${nameToUse}! 🌾` : `नमस्ते दोस्त, ${nameToUse} 👋`;
      case "Punjabi":
        return vibe === "formal" ? `ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ, ${nameToUse} ਜੀ 🙏` : vibe === "regional" ? `ਕੀ ਹਾਲ ਨੇ, ${nameToUse} ਵੀਰ? 🚜` : `ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ, ${nameToUse} 🙏`;
      case "Gujarati":
        return vibe === "formal" ? `નમસ્તે, ${nameToUse} આપનું સ્વાગત છે 🙏` : vibe === "regional" ? `કેમ છો, ${nameToUse} ભાઈલા! 🍯` : `કેમ છો મિત્ર, ${nameToUse} 👋`;
      case "Bengali":
        return vibe === "formal" ? `নমস্কার, ${nameToUse} আপনাকে স্বাগত 🙏` : vibe === "regional" ? `কি খবর, ${nameToUse} দাদা? 🌸` : `কি খবর বন্ধু, ${nameToUse} 👋`;
      case "Tamil":
        return vibe === "formal" ? `வணக்கம், தங்களை வரவேற்கிறோம் ${nameToUse} 🙏` : vibe === "regional" ? `என்ன தலைவா, எப்படி இருக்கீங்க ${nameToUse}? 🥥` : `வணக்கம் நண்பா, ${nameToUse} 👋`;
      default:
        return vibe === "formal" ? `Welcome back, ${nameToUse} 🙏` : vibe === "regional" ? `Howdy partner, ${nameToUse}! 🤠` : `Hello Friend, ${nameToUse} 👋`;
    }
  };

  useEffect(() => {
    if (typeof window !== "undefined") {
      const savedName = localStorage.getItem("yaar_user_name") || "Friend";
      setUserName(savedName);

      const savedLanguage = localStorage.getItem("yaar_language") || "English";
      setLanguage(savedLanguage);

      const savedVibe = localStorage.getItem("yaar_personality") || "friendly";
      setVibe(savedVibe);

      // Load Projects
      const savedProjects = localStorage.getItem("yaar_projects");
      let parsedProjects: any[] = [];
      if (savedProjects) {
        try {
          parsedProjects = JSON.parse(savedProjects);
          setRecentProjects(parsedProjects.slice(0, 3));
        } catch (_) {}
      }

      // Load Vault
      const savedVault = localStorage.getItem("yaar_vault");
      let parsedVault: any[] = [];
      if (savedVault) {
        try {
          parsedVault = JSON.parse(savedVault);
          setRecentVaultItems(parsedVault.slice(0, 3));
        } catch (_) {}
      }

      // Load Chats locally
      const email = localStorage.getItem("bharatai_email") || "companion@yaar.ai";
      const localMsgKey = `yaar_chats_${email}`;
      const savedLocalChats = localStorage.getItem(localMsgKey);
      let parsedChats: any[] = [];
      if (savedLocalChats) {
        try {
          parsedChats = JSON.parse(savedLocalChats);
          setRecentChats(parsedChats.slice(0, 3));
        } catch (_) {}
      }

      // Calculate Last Worked Item (Resume)
      if (parsedProjects.length > 0) {
        setLastWorkedItem({
          type: "project",
          name: parsedProjects[0].name,
          id: parsedProjects[0].id
        });
      } else if (parsedChats.length > 0) {
        setLastWorkedItem({
          type: "chat",
          name: parsedChats[0].title,
          id: parsedChats[0].id
        });
      }

      // Load Recent Searches
      const savedSearches = localStorage.getItem("yaar_search_memory");
      if (savedSearches) {
        try { setRecentSearches(JSON.parse(savedSearches).slice(0, 5)); } catch (_) {}
      }

      // Load Companion Profile
      const savedProfile = localStorage.getItem("yaar_companion_profile");
      if (savedProfile) {
        try { setCompanionProfile(JSON.parse(savedProfile)); } catch (_) {}
      }
    }
  }, [token]);

  const ui = LOCALIZED_DASHBOARD[language] || LOCALIZED_DASHBOARD["English"];

  const handleResume = () => {
    if (!lastWorkedItem) return;
    if (lastWorkedItem.type === "chat") {
      onSelectConversation(lastWorkedItem.id);
    } else {
      onNavigateToSection("projects");
    }
  };

  return (
    <div className="flex-1 overflow-y-auto scroll-smooth-premium p-6 md:p-12 relative flex flex-col justify-between max-w-5xl mx-auto space-y-10 bg-[#121316] select-none text-slate-100">
      
      {/* 1. TODAY SECTION */}
      <section className="space-y-6">
        <div className="flex flex-col md:flex-row items-center md:items-start justify-between gap-6 pt-4">
          <div className="space-y-2 text-center md:text-left">
            <span className="inline-flex px-3 py-1 bg-amber-900/20 text-amber-500 font-bold text-[10px] uppercase tracking-widest rounded-full border border-amber-900/30">
              {getFormattedDate()}
            </span>
            <h2 className="text-3xl sm:text-4xl font-black text-white tracking-tight font-display text-gradient-title mt-1.5">
              {getLocalizedWelcome()}
            </h2>
            <p className="text-slate-400 text-xs font-semibold max-w-lg leading-relaxed italic">
              &ldquo;{ui.inspiration}&rdquo;
            </p>
          </div>
          <YaarOrb state="idle" size="sm" className="shrink-0 animate-pulse duration-[4000ms]" />
        </div>

        {/* Personalized Welcome Resume Banner */}
        {lastWorkedItem && (
          <div className="p-4 sm:p-5 rounded-2xl bg-amber-950/20 border border-amber-500/20 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 animate-fade-in">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-amber-900/20 border border-amber-900/30 text-amber-500 shrink-0">
                <Clock className="w-5 h-5" />
              </div>
              <div>
                <p className="text-[10px] font-black uppercase tracking-wider text-amber-500">{ui.resumeBanner}</p>
                <h4 className="text-sm font-black text-white mt-0.5">{lastWorkedItem.name}</h4>
                {companionProfile && (
                  <p className="text-[10px] text-slate-500 font-bold mt-0.5">
                    {companionProfile.focus === "learning" ? "📚 Learning Mode" :
                     companionProfile.focus === "work" ? "💼 Work Mode" :
                     companionProfile.focus === "building" ? "🚀 Builder Mode" :
                     companionProfile.focus === "exploring" ? "🔭 Explorer Mode" : "🏡 Everyday Mode"}
                    {companionProfile.region ? ` · ${companionProfile.region}` : ""}
                  </p>
                )}
              </div>
            </div>
            <button
              onClick={handleResume}
              className="px-5 py-2.5 bg-amber-600 hover:bg-amber-500 text-white rounded-xl text-xs font-black uppercase tracking-wider transition-premium cursor-pointer text-center shrink-0 shadow-lg shadow-amber-950/20"
            >
              {ui.resumeBtn} →
            </button>
          </div>
        )}
      </section>

      {/* 2. CONTINUE JOURNEY SECTION */}
      <section className="space-y-4">
        <h3 className="text-[10px] font-black uppercase tracking-wider text-slate-500 px-1">
          {ui.continueJourney}
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {recentChats.map((c) => (
            <button
              key={c.id}
              onClick={() => onSelectConversation(c.id)}
              className="p-4 rounded-2xl bg-slate-900/30 border border-white/5 flex flex-col justify-between items-start text-left cursor-pointer hover:border-amber-500/20 hover:bg-amber-950/5 hover-lift transition-premium min-h-[100px] w-full"
            >
              <div className="p-2 rounded-lg bg-amber-900/10 text-amber-500 border border-amber-900/20">
                <MessageSquare className="w-4 h-4" />
              </div>
              <div className="w-full mt-3">
                <h4 className="text-xs font-bold text-slate-200 truncate group-hover:text-white">
                  {c.title}
                </h4>
                <p className="text-[9px] text-slate-500 font-mono mt-0.5">
                  Opened {new Date(c.created_at).toLocaleDateString()}
                </p>
              </div>
            </button>
          ))}

          {recentChats.length === 0 && (
            <div className="col-span-full p-6 rounded-2xl border border-dashed border-slate-800 text-center space-y-2">
              <Sparkles className="w-5 h-5 text-amber-500/50 mx-auto" />
              <p className="text-xs font-bold text-slate-400">No conversations yet.</p>
              <p className="text-[10px] text-slate-500 max-w-xs mx-auto leading-relaxed">Start your first companion session below. Yaar will remember your chats so you can always pick up where you left off.</p>
            </div>
          )}

          <button
            onClick={onNewChat}
            className="p-4 rounded-2xl border border-dashed border-slate-800 hover:border-amber-500/50 hover:bg-amber-950/10 text-center py-6 group transition-premium cursor-pointer flex flex-col items-center justify-center min-h-[100px]"
          >
            <PlusIcon />
            <h4 className="text-xs font-bold text-slate-405 group-hover:text-white mt-2">{ui.newChat}</h4>
            <p className="text-[9px] text-slate-500 mt-0.5">{ui.newChatDesc}</p>
          </button>
        </div>
      </section>

      {/* 3. PROJECTS SECTION */}
      <section className="space-y-4">
        <div className="flex items-center justify-between px-1">
          <span className="text-[10px] font-black uppercase tracking-wider text-slate-500">{ui.projectsLabel}</span>
          <button
            onClick={() => onNavigateToSection("projects")}
            className="text-[9px] font-black uppercase tracking-widest text-amber-500 hover:text-white transition-colors"
          >
            {ui.viewAll} →
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {recentProjects.map((p) => (
            <button
              key={p.id}
              onClick={() => onNavigateToSection("projects")}
              className="p-4 rounded-2xl bg-slate-900/30 border border-white/5 flex items-center justify-between text-left cursor-pointer hover:border-amber-500/20 hover:bg-amber-950/5 hover-lift transition-premium w-full"
            >
              <div className="flex items-center gap-3 min-w-0">
                <div className="p-2 rounded-lg bg-amber-900/10 text-amber-500 border border-amber-900/20 shrink-0">
                  <Folder className="w-4 h-4" />
                </div>
                <div className="min-w-0">
                  <h4 className="text-xs font-bold text-slate-200 truncate">{p.name}</h4>
                  <span className="px-2 py-0.5 rounded bg-slate-800 text-[8px] font-bold text-slate-450 uppercase mt-1 inline-block">
                    {p.type}
                  </span>
                </div>
              </div>
              <ArrowRight className="w-3.5 h-3.5 text-slate-550 shrink-0" />
            </button>
          ))}

          {recentProjects.length === 0 && (
            <div className="col-span-full p-6 rounded-2xl border border-dashed border-slate-800 text-center space-y-2">
              <Target className="w-5 h-5 text-amber-500/40 mx-auto" />
              <p className="text-xs font-bold text-slate-400">No active binders yet.</p>
              <p className="text-[10px] text-slate-500 max-w-xs mx-auto leading-relaxed">Create a Project Binder to organize your startup ideas, UPSC notes, or work files. Everything stays in one focused workspace.</p>
              <button onClick={() => onNavigateToSection("projects")} className="mt-1 text-[10px] font-black text-amber-500 hover:text-amber-400 uppercase tracking-wider transition-colors">Create First Binder →</button>
            </div>
          )}
        </div>
      </section>

      {/* 4. RECENT DISCOVERIES (VAULT CARDS) SECTION */}
      <section className="space-y-4">
        <div className="flex items-center justify-between px-1">
          <span className="text-[10px] font-black uppercase tracking-wider text-slate-500">{ui.recentDiscoveries}</span>
          <button
            onClick={() => onNavigateToSection("vault")}
            className="text-[9px] font-black uppercase tracking-widest text-amber-500 hover:text-white transition-colors"
          >
            {ui.viewAll} →
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {recentVaultItems.map((item) => (
            <button
              key={item.id}
              onClick={() => onNavigateToSection("vault")}
              className="p-4 rounded-2xl bg-slate-900/30 border border-white/5 flex flex-col justify-between items-start text-left cursor-pointer hover:border-amber-500/20 hover:bg-amber-950/5 hover-lift transition-premium w-full min-h-[100px]"
            >
              <div className="flex items-center gap-2">
                <Bookmark className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                <h4 className="text-xs font-bold text-slate-200 truncate max-w-[200px]">{item.title}</h4>
              </div>
              <p className="text-[10px] text-slate-400 font-medium leading-relaxed mt-2 line-clamp-2">
                {item.content}
              </p>
              <div className="flex flex-wrap gap-1 mt-2.5">
                {(item.tags || []).slice(0, 2).map((tag: string) => (
                  <span key={tag} className="px-1.5 py-0.5 rounded bg-slate-800 text-[8px] font-bold text-slate-500">
                    #{tag}
                  </span>
                ))}
              </div>
            </button>
          ))}

          {recentVaultItems.length === 0 && (
            <div className="col-span-full p-6 rounded-2xl border border-dashed border-slate-800 text-center space-y-2">
              <Bookmark className="w-5 h-5 text-emerald-500/40 mx-auto" />
              <p className="text-xs font-bold text-slate-400">Your second brain is empty.</p>
              <p className="text-[10px] text-slate-500 max-w-xs mx-auto leading-relaxed">Save any YAAR response, web search result, or your own notes to your Vault. Build your personal knowledge base over time.</p>
              <button onClick={() => onNavigateToSection("vault")} className="mt-1 text-[10px] font-black text-emerald-500 hover:text-emerald-400 uppercase tracking-wider transition-colors">Open Vault →</button>
            </div>
          )}
        </div>
      </section>

      {/* SEARCH MEMORY SECTION */}
      {recentSearches.length > 0 && (
        <section className="space-y-4">
          <div className="flex items-center justify-between px-1">
            <span className="text-[10px] font-black uppercase tracking-wider text-slate-500">Recent Searches</span>
            <button
              onClick={() => {
                localStorage.removeItem("yaar_search_memory");
                setRecentSearches([]);
              }}
              className="text-[9px] font-black uppercase tracking-widest text-slate-600 hover:text-rose-400 transition-colors"
            >
              Clear
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {recentSearches.map((s, i) => (
              <button
                key={i}
                onClick={() => onNewChat()}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900/40 border border-white/5 hover:border-amber-500/30 hover:bg-amber-950/10 text-[10px] font-bold text-slate-350 hover:text-white transition-premium cursor-pointer"
              >
                <Search className="w-3 h-3 text-slate-500" />
                <span className="truncate max-w-[200px]">{s}</span>
              </button>
            ))}
          </div>
        </section>
      )}

      {/* 5. TRUST FOOTER SAFEGUARD */}
      <footer className="pt-6 border-t border-slate-900">
        <div className="p-4 rounded-2xl bg-slate-950/30 border border-white/5 flex flex-col sm:flex-row items-center gap-4 text-center sm:text-left">
          <div className="p-2.5 rounded-xl bg-emerald-950/20 text-emerald-500 border border-emerald-900/30 shrink-0">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-xs font-black text-slate-200 uppercase tracking-wider">{ui.trustTitle}</h4>
            <p className="text-[10px] text-slate-450 leading-relaxed font-semibold mt-0.5">
              {ui.trustDesc}
            </p>
          </div>
        </div>
      </footer>

    </div>
  );
}

function PlusIcon() {
  return (
    <svg className="w-5 h-5 text-slate-550 group-hover:text-amber-500 transition-colors" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
    </svg>
  );
}
