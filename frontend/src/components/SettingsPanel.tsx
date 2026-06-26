"use client";

import React, { useState, useEffect } from "react";
import { 
  Settings, Save, Trash2, CheckCircle, Download, LogOut, Shield, 
  User, Palette, Globe, Brain, Database, Info
} from "lucide-react";

interface SettingsPanelProps {
  language: string;
  setLanguage: (lang: string) => void;
  vibe: string;
  setVibe: (vibe: string) => void;
  userName: string;
  setUserName: (name: string) => void;
  theme: string;
  setTheme: (theme: string) => void;
  onReset: () => void;
  onLogout?: () => void;
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
  { id: "Kannada", label: "ਕನ್ನಡ (Kannada)" },
  { id: "Malayalam", label: "മലയാളം (Malayalam)" },
  { id: "Odia", label: "ଓਡ଼ਿଆ (Odia)" },
  { id: "Assamese", label: "অসমীয়া (Assamese)" },
  { id: "Maithili", label: "मैथिली (Maithili)" },
  { id: "Santali", label: "संताली (Santali)" },
  { id: "Kashmiri", label: "کٲشُر (Kashmiri)" },
  { id: "Nepali", label: "नेपाली (Nepali)" },
  { id: "Konkani", label: "कोंकणी (Konkani)" },
  { id: "Sindhi", label: "سنڌੀ (Sindhi)" },
  { id: "Dogri", label: "डोगरी (Dogri)" },
  { id: "Manipuri", label: "মৈতৈলোন (Manipuri)" },
  { id: "Bodo", label: "बर' (Bodo)" },
  { id: "Sanskrit", label: "संस्कृतם (Sanskrit)" }
];

const LOCALIZED_SETTINGS: Record<string, {
  title: string;
  nameLabel: string;
  langLabel: string;
  vibeLabel: string;
  themeLabel: string;
  resetLabel: string;
  resetDesc: string;
  resetBtn: string;
  saveBtn: string;
  successMsg: string;
  privacyTitle: string;
  privacyDesc: string;
  autoDeleteLabel: string;
  localOnlyLabel: string;
  telemetryLabel: string;
  exportTitle: string;
  exportDesc: string;
  exportBtn: string;
  sessionTitle: string;
  sessionDesc: string;
  logoutBtn: string;
  vibes: Array<{ id: string; label: string }>;
  themes: Array<{ id: string; label: string }>;
}> = {
  English: {
    title: "Companion Settings",
    nameLabel: "Your Name",
    langLabel: "Preferred Language",
    vibeLabel: "Companion Vibe",
    themeLabel: "Visual Theme",
    privacyTitle: "Privacy & Sovereignty Controls",
    privacyDesc: "Manage how your personal companion logs are handled locally on this device.",
    autoDeleteLabel: "Auto-Delete Chat Logs after 24h",
    localOnlyLabel: "Strict Local-Only Storage (No Cloud Synced Data)",
    telemetryLabel: "Disable Diagnostic Telemetry",
    exportTitle: "Export Personal Companion Binder",
    exportDesc: "Download all chat logs, binders, second brain vault assets, and companion settings in a single portable JSON file.",
    exportBtn: "Export All Data (JSON)",
    sessionTitle: "Session Security",
    sessionDesc: "For sovereignty, your active session automatically expires after 15 minutes of inactivity.",
    logoutBtn: "Secure Log Out",
    resetLabel: "Danger Zone: Reset Companion",
    resetDesc: "Permanently clear your local companion session, chat history, projects binder, and vault second brain. This cannot be undone.",
    resetBtn: "Clear All Memory & Reset",
    saveBtn: "Save Preferences",
    successMsg: "Preferences updated successfully!",
    vibes: [
      { id: "friendly", label: "Friendly / Dostana" },
      { id: "formal", label: "Formal / Adabi" },
      { id: "regional", label: "Regional / Desi Touch" }
    ],
    themes: [
      { id: "dark-indigo", label: "Midnight Indigo" },
      { id: "onyx-gold", label: "Ox Gold" },
      { id: "slate-calm", label: "Calm Slate" }
    ]
  },
  Hindi: {
    title: "यार सेटिंग्स",
    nameLabel: "आपका नाम",
    langLabel: "पसंदीदा भाषा",
    vibeLabel: "यार का स्वभाव",
    themeLabel: "विजुअल थीम",
    privacyTitle: "गोपनीयता और संप्रभुता नियंत्रण",
    privacyDesc: "प्रबंधित करें कि आपके व्यक्तिगत यार संवादों को इस डिवाइस पर स्थानीय रूप से कैसे रखा जाता है।",
    autoDeleteLabel: "चैट लॉग्स 24 घंटे के बाद स्वतः हटाएं",
    localOnlyLabel: "सख्त केवल-स्थानीय भंडारण (कोई क्लाउड सिंक नहीं)",
    telemetryLabel: "डायग्नोस्टिक टेलीमेट्री अक्षम करें",
    exportTitle: "व्यक्तिगत डेटा निर्यात करें",
    exportDesc: "एक पोर्टेबल JSON फ़ाइल में अपने सभी चैट लॉग्स, बाइंडर्स, वॉल्ट सेकंड ब्रेन और प्राथमिकताएं डाउनलोड करें।",
    exportBtn: "सभी डेटा निर्यात करें (JSON)",
    sessionTitle: "सत्र सुरक्षा",
    sessionDesc: "संप्रभु सुरक्षा के लिए, आपकी निष्क्रियता के 15 मिनट बाद आपका सत्र स्वतः समाप्त हो जाता है।",
    logoutBtn: "सुरक्षित लॉग आउट",
    resetLabel: "खतरनाक क्षेत्र: यार को रीसेट करें",
    resetDesc: "सभी स्थानीय चैट इतिहास, प्रोजेक्ट बाइंडर्स और वॉल्ट सेकंड ब्रेन को स्थायी रूप से हटा दें। इसे वापस नहीं लाया जा सकता।",
    resetBtn: "स्मृति साफ़ करें और रीसेट करें",
    saveBtn: "प्राथमिकताएं सहेजें",
    successMsg: "प्राथमिकताएं सफलतापूर्वक सहेजी गईं!",
    vibes: [
      { id: "friendly", label: "दोस्ताना / दोस्ताना" },
      { id: "formal", label: "औपचारिक / अदबी" },
      { id: "regional", label: "क्षेत्रीय / देसी टच" }
    ],
    themes: [
      { id: "dark-indigo", label: "मिडनाइट इंडिगो" },
      { id: "onyx-gold", label: "ओनिक्स गोल्ड" },
      { id: "slate-calm", label: "शांत स्लेट" }
    ]
  },
  Punjabi: {
    title: "ਯਾਰ ਸੈਟਿੰਗਜ਼",
    nameLabel: "ਤੁਹਾਡਾ ਨਾਮ",
    langLabel: "ਪਸੰਦੀਦਾ ਭਾਸ਼ਾ",
    vibeLabel: "ਯਾਰ ਦਾ ਸੁਭਾਅ",
    themeLabel: "ਵਿਜ਼ੂਅਲ ਥੀਮ",
    privacyTitle: "ਗੋਪਨੀਯਤਾ ਅਤੇ ਪ੍ਰਭੂਸੱਤਾ ਕੰਟਰੋਲ",
    privacyDesc: "ਪ੍ਰਬੰਧਿਤ ਕਰੋ ਕਿ ਇਸ ਡਿਵਾਈਸ 'ਤੇ ਤੁਹਾਡੇ ਸਥਾਨਕ ਚੈਟ ਇਤਿਹਾਸ ਨੂੰ ਕਿਵੇਂ ਸੁਰੱਖਿਅਤ ਰੱਖਿਆ ਜਾਵੇ।",
    autoDeleteLabel: "24 ਘੰਟਿਆਂ ਬਾਅਦ ਚੈਟ ਇਤਿਹਾਸ ਆਟੋ-ਡਿਲੀਟ ਕਰੋ",
    localOnlyLabel: "ਸਖਤ ਲੋਕਲ-ਓਨਲੀ ਸਟੋਰੇਜ (ਕੋਈ ਕਲਾਉਡ ਸਿੰਕ ਨਹੀਂ)",
    telemetryLabel: "ਨਿਦਾਨ ਟੈਲੀਮੈਟਰੀ ਬੰਦ ਕਰੋ",
    exportTitle: "ਆਪਣਾ ਨਿੱਜੀ ਡਾਟਾ ਐਕਸਪੋਰਟ ਕਰੋ",
    exportDesc: "ਆਪਣੇ ਸਾਰੇ ਚੈਟ ਇਤਿਹਾਸ, ਬਾਈਂਡਰ, ਵਾਲਟ ਸੈਕਿੰਡ ਬ੍ਰੇਨ ਅਤੇ ਸੈਟਿੰਗਾਂ ਨੂੰ ਇੱਕ ਸਿੰਗਲ JSON ਫਾਈਲ ਵਿੱਚ ਡਾਊਨਲੋਡ ਕਰੋ।",
    exportBtn: "ਸਾਰਾ ਡਾਟਾ ਐਕਸਪੋਰਟ ਕਰੋ (JSON)",
    sessionTitle: "ਸੈਸ਼ਨ ਸੁਰੱਖਿਆ",
    sessionDesc: "ਪ੍ਰਭੂਸੱਤਾ ਸੁਰੱਖਿਆ ਲਈ, 15 ਮਿੰਟ ਦੀ ਅਕਿਰਿਆਸ਼ੀਲਤਾ ਤੋਂ ਬਾਅਦ ਤੁਹਾਡਾ ਸੈਸ਼ਨ ਆਟੋਮੈਟਿਕਲੀ ਲੌਗ ਆਊਟ ਹੋ ਜਾਵੇਗਾ।",
    logoutBtn: "ਸੁਰੱਖਿਅਤ ਲੌਗ ਆਊਟ",
    resetLabel: "ਖ਼ਤਰਨਾਕ ਖੇਤਰ: ਯਾਰ ਨੂੰ ਰੀਸੈਟ ਕਰੋ",
    resetDesc: "ਆਪਣੇ ਸਾਰੇ ਸਥਾਨਕ ਚੈਟ ਇਤਿਹਾਸ, ਪ੍ਰੋਜੈਕਟ ਬਾਈਂਡਰ ਅਤੇ ਵਾਲਟ ਸੈਕਿੰਡ ਬ੍ਰੇਨ ਨੂੰ ਪੱਕੇ ਤੌਰ 'ਤੇ ਮਿਟਾਓ। ਇਸਨੂੰ ਵਾਪਸ ਨਹੀਂ ਲਿਆਂਦਾ ਜਾ ਸਕਦਾ।",
    resetBtn: "ਯਾਦਾਂ ਸਾਫ਼ ਕਰੋ ਅਤੇ ਰੀਸੈਟ ਕਰੋ",
    saveBtn: "ਬਦਲਾਅ ਸੁਰੱਖਿਅਤ ਕਰੋ",
    successMsg: "ਸੈਟਿੰਗਾਂ ਸਫਲਤਾਪੂਰਵਕ ਅੱਪਡੇਟ ਕੀਤੀਆਂ ਗਈਆਂ!",
    vibes: [
      { id: "friendly", label: "ਦੋਸਤਾਨਾ / ਯਾਰਾਨਾ" },
      { id: "formal", label: "ਰਸਮੀ / ਅਦਬੀ" },
      { id: "regional", label: "ਖੇਤਰੀ / ਦੇਸੀ ਟੱਚ" }
    ],
    themes: [
      { id: "dark-indigo", label: "ਮਿਡਨਾਈਟ ਇੰਡੀਗੋ" },
      { id: "onyx-gold", label: "ਓਨਿਕਸ ਗੋਲਡ" },
      { id: "slate-calm", label: "ਸ਼ਾਂਤ ਸਲੇਟ" }
    ]
  }
};

export default function SettingsPanel({
  language,
  setLanguage,
  vibe,
  setVibe,
  userName,
  setUserName,
  theme,
  setTheme,
  onReset,
  onLogout
}: SettingsPanelProps) {
  const [activeSection, setActiveSection] = useState<"profile" | "appearance" | "language" | "memory" | "privacy" | "data" | "about">("profile");

  const [localName, setLocalName] = useState(userName);
  const [localLang, setLocalLang] = useState(language);
  const [localVibe, setLocalVibe] = useState(vibe);
  const [localTheme, setLocalTheme] = useState(theme);
  const [showSuccess, setShowSuccess] = useState(false);

  // Privacy states loaded from localstorage
  const [autoDelete, setAutoDelete] = useState(false);
  const [localOnly, setLocalOnly] = useState(true);
  const [disableDiagnostics, setDisableDiagnostics] = useState(false);

  const [betaTesterMode, setBetaTesterMode] = useState(false);
  const [storedReports, setStoredReports] = useState<any[]>([]);
  const [copiedReports, setCopiedReports] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const savedPrivacy = localStorage.getItem("yaar_privacy_settings");
      if (savedPrivacy) {
        try {
          const parsed = JSON.parse(savedPrivacy);
          setAutoDelete(parsed.autoDelete ?? false);
          setLocalOnly(parsed.localOnly ?? true);
          setDisableDiagnostics(parsed.disableDiagnostics ?? false);
        } catch (_) {}
      }

      const savedBetaMode = localStorage.getItem("yaar_beta_tester_mode") === "true";
      setBetaTesterMode(savedBetaMode);

      const savedReports = localStorage.getItem("yaar_feedback");
      if (savedReports) {
        try { setStoredReports(JSON.parse(savedReports)); } catch (_) {}
      }
    }
  }, []);

  const handleClearReports = () => {
    if (confirm("Are you sure you want to clear all stored beta feedback reports?")) {
      localStorage.removeItem("yaar_feedback");
      setStoredReports([]);
    }
  };

  const handleExportReportsJson = () => {
    const blob = new Blob([JSON.stringify(storedReports, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `yaar_feedback_logs_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleCopyReports = () => {
    navigator.clipboard.writeText(JSON.stringify(storedReports, null, 2));
    setCopiedReports(true);
    setTimeout(() => setCopiedReports(false), 2000);
  };

  const langKey = LOCALIZED_SETTINGS[language] ? language : "English";
  const texts = LOCALIZED_SETTINGS[langKey];

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    if (!localName.trim()) return;

    setUserName(localName.trim());
    setLanguage(localLang);
    setVibe(localVibe);
    setTheme(localTheme);

    localStorage.setItem("yaar_user_name", localName.trim());
    localStorage.setItem("yaar_language", localLang);
    localStorage.setItem("yaar_personality", localVibe);
    localStorage.setItem("yaar_theme", localTheme);

    // Update active user session & accounts registry
    if (typeof window !== "undefined") {
      const activeUserStr = localStorage.getItem("yaar_active_user");
      if (activeUserStr) {
        try {
          const activeUser = JSON.parse(activeUserStr);
          activeUser.name = localName.trim();
          activeUser.language = localLang;
          localStorage.setItem("yaar_active_user", JSON.stringify(activeUser));

          // Also update in accounts list
          const accountsStr = localStorage.getItem("yaar_accounts");
          if (accountsStr) {
            const accounts = JSON.parse(accountsStr);
            const updatedAccounts = accounts.map((acc: any) => {
              if (acc.email.toLowerCase() === activeUser.email.toLowerCase()) {
                return { ...acc, name: localName.trim(), language: localLang };
              }
              return acc;
            });
            localStorage.setItem("yaar_accounts", JSON.stringify(updatedAccounts));
          }
        } catch (_) {}
      }
    }

    // Save privacy configurations
    const privacyObj = {
      autoDelete,
      localOnly,
      disableDiagnostics
    };
    localStorage.setItem("yaar_privacy_settings", JSON.stringify(privacyObj));

    setShowSuccess(true);
    setTimeout(() => setShowSuccess(false), 3000);
  };

  const handleExportData = () => {
    if (typeof window === "undefined") return;

    const email = localStorage.getItem("bharatai_email") || "companion@yaar.ai";
    
    // Aggregate all data from local storage
    const chatsKey = `yaar_chats_${email}`;
    const chatsStr = localStorage.getItem(chatsKey);
    let chatsList = [];
    if (chatsStr) {
      try { chatsList = JSON.parse(chatsStr); } catch (_) {}
    }

    const messagesRegistry: Record<string, any> = {};
    chatsList.forEach((c: any) => {
      const msgKey = `yaar_messages_${c.id}`;
      const msgsStr = localStorage.getItem(msgKey);
      if (msgsStr) {
        try { messagesRegistry[c.id] = JSON.parse(msgsStr); } catch (_) {}
      }
    });

    const projectsStr = localStorage.getItem("yaar_projects");
    let projectsList = [];
    if (projectsStr) {
      try { projectsList = JSON.parse(projectsStr); } catch (_) {}
    }

    const vaultStr = localStorage.getItem("yaar_vault");
    let vaultList = [];
    if (vaultStr) {
      try { vaultList = JSON.parse(vaultStr); } catch (_) {}
    }

    const exportObject = {
      profile: {
        name: userName,
        email: email,
        language: language,
        vibe: vibe,
        theme: theme,
        exportedAt: new Date().toISOString()
      },
      preferences: {
        autoDelete,
        localOnly,
        disableDiagnostics
      },
      chats: chatsList,
      messages: messagesRegistry,
      projects: projectsList,
      vault: vaultList
    };

    const blob = new Blob([JSON.stringify(exportObject, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `yaar_export_${email.split("@")[0]}_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleClearMemory = () => {
    if (confirm("Are you absolutely sure you want to delete all chats, projects, vault cards, and preferences? YAAR will restart from the greeting splash.")) {
      onReset();
    }
  };

  const sections = [
    { id: "profile", label: "Profile", icon: User },
    { id: "language", label: "Language", icon: Globe },
    { id: "memory", label: "Memory", icon: Brain },
    { id: "privacy", label: "Privacy", icon: Shield },
    { id: "data", label: "Data", icon: Database },
    { id: "about", label: "About", icon: Info }
  ];

  return (
    <div className="flex-1 flex flex-col md:flex-row h-full min-h-[500px] bg-[#121316] text-slate-100 rounded-2xl overflow-hidden border border-white/5">
      {/* Left Sidebar Menu */}
      <div className="w-full md:w-56 bg-slate-950 border-b md:border-b-0 md:border-r border-white/5 p-4 flex flex-col justify-between shrink-0">
        <div className="space-y-4">
          <div className="flex items-center gap-2.5 px-2 pb-3 border-b border-white/5">
            <Settings className="w-4.5 h-4.5 text-amber-500" />
            <h3 className="text-xs font-black uppercase tracking-wider text-white">Settings</h3>
          </div>
          <nav className="flex flex-row md:flex-col gap-1 overflow-x-auto md:overflow-x-visible pb-2 md:pb-0 scrollbar-none">
            {sections.map(s => (
              <button
                key={s.id}
                type="button"
                onClick={() => setActiveSection(s.id as any)}
                className={`w-auto md:w-full text-left px-3 py-2 rounded-xl text-xs font-bold flex items-center gap-2.5 transition-colors cursor-pointer whitespace-nowrap ${
                  activeSection === s.id
                    ? "bg-amber-950/20 text-amber-500 border border-amber-900/30"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/30 border border-transparent"
                }`}
              >
                <s.icon className="w-4 h-4 shrink-0" />
                <span>{s.label}</span>
              </button>
            ))}
          </nav>
        </div>
        {onLogout && (
          <button
            type="button"
            onClick={onLogout}
            className="hidden md:flex w-full text-left px-3 py-2 rounded-xl text-xs font-bold text-rose-450 hover:bg-rose-950/10 items-center gap-2.5 transition-colors cursor-pointer mt-4"
          >
            <LogOut className="w-4 h-4 shrink-0" />
            <span>Secure Log Out</span>
          </button>
        )}
      </div>

      {/* Right Content Area */}
      <div className="flex-1 overflow-y-auto p-6 md:p-10 space-y-6">
        {showSuccess && (
          <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-bold flex items-center gap-2 animate-fade-in mb-4">
            <CheckCircle className="w-4.5 h-4.5 shrink-0" />
            <span>{texts.successMsg}</span>
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-6">
          {activeSection === "profile" && (
            <div className="space-y-4 animate-fade-in">
              <div className="border-b border-white/5 pb-2">
                <h2 className="text-lg font-black text-white">Profile Settings</h2>
                <p className="text-[10px] text-slate-500">Configure your companion identification and tone persona.</p>
              </div>
              <div className="grid grid-cols-1 gap-4">
                <div className="flex flex-col gap-1.5">
                  <label className="text-[9px] uppercase tracking-wider font-extrabold text-slate-500">{texts.nameLabel}</label>
                  <input
                    type="text"
                    required
                    value={localName}
                    onChange={(e) => setLocalName(e.target.value)}
                    className="w-full px-4 py-3 rounded-xl bg-slate-900/40 border border-white/5 text-white text-xs font-bold focus:border-amber-500 outline-none transition-premium"
                  />
                </div>
                <div className="flex flex-col gap-1.5">
                  <label className="text-[9px] uppercase tracking-wider font-extrabold text-slate-500">{texts.vibeLabel}</label>
                  <select
                    value={localVibe}
                    onChange={(e) => setLocalVibe(e.target.value)}
                    className="w-full px-4 py-3 rounded-xl bg-slate-900/40 border border-white/5 text-white text-xs font-bold focus:border-amber-500 outline-none transition-premium appearance-none cursor-pointer"
                  >
                    {texts.vibes.map((v) => (
                      <option key={v.id} value={v.id} className="bg-[#121316] text-white">
                        {v.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          )}


          {activeSection === "language" && (
            <div className="space-y-4 animate-fade-in">
              <div className="border-b border-white/5 pb-2">
                <h2 className="text-lg font-black text-white">Language Settings</h2>
                <p className="text-[10px] text-slate-500">Select your preferred system language.</p>
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="text-[9px] uppercase tracking-wider font-extrabold text-slate-500">{texts.langLabel}</label>
                <select
                  value={localLang}
                  onChange={(e) => setLocalLang(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl bg-slate-900/40 border border-white/5 text-white text-xs font-bold focus:border-amber-500 outline-none transition-premium appearance-none cursor-pointer"
                >
                  {LANGUAGES.map((l) => (
                    <option key={l.id} value={l.id} className="bg-[#121316] text-white">
                      {l.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          )}

          {activeSection === "memory" && (
            <div className="space-y-4 animate-fade-in">
              <div className="border-b border-white/5 pb-2">
                <h2 className="text-lg font-black text-white">Memory Settings</h2>
                <p className="text-[10px] text-slate-500">Configure log retention and auto-expiry.</p>
              </div>
              <div className="space-y-3">
                <label className="flex items-center gap-3 p-3.5 rounded-xl bg-slate-950/20 border border-white/5 hover:border-slate-800 transition-colors cursor-pointer text-xs font-bold text-slate-300">
                  <input
                    type="checkbox"
                    checked={autoDelete}
                    onChange={(e) => setAutoDelete(e.target.checked)}
                    className="w-4 h-4 accent-amber-600 rounded cursor-pointer"
                  />
                  <span>{texts.autoDeleteLabel}</span>
                </label>
                <div className="p-3.5 rounded-xl bg-slate-950/20 border border-white/5 text-xs text-slate-400 space-y-1">
                  <h4 className="font-bold text-slate-300">{texts.sessionTitle}</h4>
                  <p className="leading-normal">{texts.sessionDesc}</p>
                </div>
              </div>
            </div>
          )}

          {activeSection === "privacy" && (
            <div className="space-y-4 animate-fade-in">
              <div className="border-b border-white/5 pb-2">
                <h2 className="text-lg font-black text-white">{texts.privacyTitle}</h2>
                <p className="text-[10px] text-slate-500">{texts.privacyDesc}</p>
              </div>
              <div className="flex flex-col gap-3">
                <label className="flex items-center gap-3 p-3.5 rounded-xl bg-slate-950/20 border border-white/5 hover:border-slate-800 transition-colors cursor-pointer text-xs font-bold text-slate-300">
                  <input
                    type="checkbox"
                    checked={localOnly}
                    onChange={(e) => setLocalOnly(e.target.checked)}
                    className="w-4 h-4 accent-amber-600 rounded cursor-pointer"
                  />
                  <span>{texts.localOnlyLabel}</span>
                </label>

                <label className="flex items-center gap-3 p-3.5 rounded-xl bg-slate-950/20 border border-white/5 hover:border-slate-800 transition-colors cursor-pointer text-xs font-bold text-slate-300">
                  <input
                    type="checkbox"
                    checked={disableDiagnostics}
                    onChange={(e) => setDisableDiagnostics(e.target.checked)}
                    className="w-4 h-4 accent-amber-600 rounded cursor-pointer"
                  />
                  <span>{texts.telemetryLabel}</span>
                </label>

                <label className="flex items-center gap-3 p-3.5 rounded-xl bg-slate-950/20 border border-white/5 hover:border-slate-800 transition-colors cursor-pointer text-xs font-bold text-slate-300">
                  <input
                    type="checkbox"
                    checked={betaTesterMode}
                    onChange={(e) => {
                      setBetaTesterMode(e.target.checked);
                      localStorage.setItem("yaar_beta_tester_mode", e.target.checked ? "true" : "false");
                      window.dispatchEvent(new Event("yaar_beta_mode_changed"));
                    }}
                    className="w-4 h-4 accent-amber-600 rounded cursor-pointer"
                  />
                  <span>Enable Beta Tester Feedback Overlay</span>
                </label>
              </div>
            </div>
          )}

          {activeSection === "data" && (
            <div className="space-y-6 animate-fade-in">
              <div className="border-b border-white/5 pb-2">
                <h2 className="text-lg font-black text-white">Data Management</h2>
                <p className="text-[10px] text-slate-500">Export or clear your personal companion data.</p>
              </div>

              <div className="space-y-4">
                <div className="space-y-1">
                  <h3 className="text-xs font-black text-slate-200 uppercase tracking-wider">{texts.exportTitle}</h3>
                  <p className="text-slate-450 text-[10px] leading-relaxed max-w-xl">
                    {texts.exportDesc}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={handleExportData}
                  className="px-5 py-3 bg-slate-900 hover:bg-slate-800 border border-white/5 hover:border-slate-800 text-white rounded-xl text-[10px] font-extrabold uppercase tracking-widest transition-premium cursor-pointer flex items-center gap-2"
                >
                  <Download className="w-4 h-4 text-amber-500" />
                  <span>{texts.exportBtn}</span>
                </button>
              </div>

              {storedReports.length > 0 && (
                <div className="pt-6 border-t border-white/5 space-y-4">
                  <div className="space-y-1">
                    <h3 className="text-xs font-black text-slate-200 uppercase tracking-wider">Beta Tester Logs ({storedReports.length})</h3>
                    <p className="text-slate-450 text-[10px] leading-relaxed max-w-xl">
                      Extract or purge local feedback logs stored during your beta test.
                    </p>
                  </div>
                  <div className="flex gap-2 flex-wrap">
                    <button
                      type="button"
                      onClick={handleCopyReports}
                      className="px-5 py-3 bg-slate-900 hover:bg-slate-800 border border-white/5 hover:border-slate-800 text-white rounded-xl text-[10px] font-extrabold uppercase tracking-widest transition-premium cursor-pointer flex items-center gap-2"
                    >
                      <span>{copiedReports ? "Copied! ✓" : "Copy logs to clipboard"}</span>
                    </button>
                    <button
                      type="button"
                      onClick={handleExportReportsJson}
                      className="px-5 py-3 bg-amber-600 hover:bg-amber-500 text-white rounded-xl text-[10px] font-extrabold uppercase tracking-widest transition-premium cursor-pointer flex items-center gap-2"
                    >
                      <Download className="w-4 h-4" />
                      <span>Export Feedback Logs JSON</span>
                    </button>
                    <button
                      type="button"
                      onClick={handleClearReports}
                      className="px-5 py-3 bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-rose-450 rounded-xl text-[10px] font-extrabold uppercase tracking-widest transition-premium cursor-pointer flex items-center gap-2"
                    >
                      <span>Clear logs</span>
                    </button>
                  </div>
                </div>
              )}

              <div className="pt-6 border-t border-white/5 space-y-4">
                <div className="space-y-1">
                  <h3 className="text-xs font-black text-rose-450 uppercase tracking-wider">{texts.resetLabel}</h3>
                  <p className="text-slate-450 text-[10px] leading-relaxed max-w-xl">
                    {texts.resetDesc}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={handleClearMemory}
                  className="px-5 py-3 bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-rose-450 rounded-xl text-[10px] font-extrabold uppercase tracking-widest transition-premium cursor-pointer flex items-center gap-2"
                >
                  <Trash2 className="w-4 h-4" />
                  <span>{texts.resetBtn}</span>
                </button>
              </div>
            </div>
          )}

          {activeSection === "about" && (
            <div className="space-y-4 animate-fade-in">
              <div className="border-b border-white/5 pb-2">
                <h2 className="text-lg font-black text-white">About YAAR</h2>
                <p className="text-[10px] text-slate-500">Information about the YAAR Sovereign Companion.</p>
              </div>
              <div className="p-5 rounded-2xl bg-slate-900/30 border border-white/5 space-y-3 text-xs leading-relaxed text-slate-300">
                <p>
                  <strong>YAAR v1.0</strong> is a modern sovereign AI assistant designed for high reliability, local-first data storage, and zero-compromise privacy.
                </p>
                <p>
                  Built for builders, learners, and creators in India, it features advanced indicating translation capabilities, integrated project binders, and an automated knowledge router.
                </p>
                <div className="text-[10px] text-slate-500 pt-2 border-t border-white/5">
                  &copy; {new Date().getFullYear()} YAAR. Private by Default.
                </div>
              </div>
            </div>
          )}

          {/* Show Save preferences button on sections that are forms */}
          {["profile", "language", "memory", "privacy"].includes(activeSection) && (
            <div className="pt-4 border-t border-white/5 flex justify-between items-center">
              <button
                type="submit"
                className="px-5 py-3 bg-amber-600 hover:bg-amber-500 text-white rounded-xl text-xs font-black uppercase tracking-wider transition-premium cursor-pointer shadow-lg shadow-amber-950/20 flex items-center gap-1.5"
              >
                <Save className="w-4 h-4" />
                <span>{texts.saveBtn}</span>
              </button>
              
              {onLogout && activeSection === "profile" && (
                <button
                  type="button"
                  onClick={onLogout}
                  className="flex md:hidden px-4 py-2 border border-white/5 hover:bg-rose-950/10 text-rose-450 rounded-xl text-xs font-bold items-center gap-1.5 transition-colors cursor-pointer"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  <span>Log Out</span>
                </button>
              )}
            </div>
          )}
        </form>
      </div>
    </div>
  );
}
