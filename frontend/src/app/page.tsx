"use client";

import React, { useEffect, useState } from "react";
import DocumentSidebar from "../components/DocumentSidebar";
import ChatInterface from "../components/ChatInterface";
import AmbientCanvas from "../components/AmbientCanvas";
import YaarOrb from "../components/YaarOrb";
import OnboardingWizard from "../components/OnboardingWizard";
import LifeHubPanel from "../components/LifeHubPanel";
import ProjectsPanel from "../components/ProjectsPanel";
import VaultPanel from "../components/VaultPanel";
import SettingsPanel from "../components/SettingsPanel";
import CommandBar from "../components/CommandBar";
import GreetingSplash from "../components/GreetingSplash";
import { Send, Languages, ArrowRight, Sparkles, LogIn, UserPlus, X, Check } from "lucide-react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

const LOCALIZED_LOGIN_TEXTS: Record<string, {
  googleBtn: string;
  emailBtn: string;
  emailLabel: string;
  passLabel: string;
  loginBtn: string;
  registerBtn: string;
  toggleSignUp: string;
  toggleLogIn: string;
  goBack: string;
  nameLabel: string;
}> = {
  English: {
    googleBtn: "Continue with Google",
    emailBtn: "Continue with Email",
    emailLabel: "Email Address",
    passLabel: "Password",
    loginBtn: "Connect Account",
    registerBtn: "Register Companion",
    toggleSignUp: "New to Yaar? Sign Up",
    toggleLogIn: "Have an account? Log In",
    goBack: "Go Back",
    nameLabel: "Your Name"
  },
  Hindi: {
    googleBtn: "गूगल के साथ जारी रखें",
    emailBtn: "ईमेल के साथ जारी रखें",
    emailLabel: "ईमेल पता",
    passLabel: "पासवर्ड",
    loginBtn: "खाता कनेक्ट करें",
    registerBtn: "यार पंजीकृत करें",
    toggleSignUp: "यार में नए हैं? साइन अप करें",
    toggleLogIn: "क्या आपके पास पहले से खाता है? लॉग इन करें",
    goBack: "वापस जाएं",
    nameLabel: "आपका नाम"
  },
  Punjabi: {
    googleBtn: "ਗੂਗਲ ਨਾਲ ਜਾਰੀ ਰੱਖੋ",
    emailBtn: "ਈਮੇਲ ਨਾਲ ਜਾਰੀ ਰੱਖੋ",
    emailLabel: "ਈਮੇਲ ਪਤਾ",
    passLabel: "ਪਾਸਵਰਡ",
    loginBtn: "ਖਾਤਾ ਕਨੈਕਟ ਕਰੋ",
    registerBtn: "ਯਾਰ ਰਜਿਸਟਰ ਕਰੋ",
    toggleSignUp: "ਯਾਰ 'ਤੇ ਨਵੇਂ ਹੋ? ਸਾਈਨ ਅੱਪ ਕਰੋ",
    toggleLogIn: "ਪਹਿਲਾਂ ਹੀ ਖਾਤਾ ਹੈ? ਲੌਗ ਇਨ ਕਰੋ",
    goBack: "ਪਿੱਛੇ ਜਾਓ",
    nameLabel: "ਤੁਹਾਡਾ ਨਾਮ"
  },
  Gujarati: {
    googleBtn: "ગૂગલ સાથે આગળ વધો",
    emailBtn: "ઇમેઇલ સાથે આગળ વધો",
    emailLabel: "ઇમેઇલ સરનામું",
    passLabel: "પાસવર્ડ",
    loginBtn: "ખાતું જોડો",
    registerBtn: "યાર નોંધણી કરો",
    toggleSignUp: "યાર પર નવા છો? સાઇન અપ કરો",
    toggleLogIn: "ખાતું છે? લોગ ઇન કરો",
    goBack: "પાછા જાઓ",
    nameLabel: "આપનું નામ"
  },
  Bengali: {
    googleBtn: "গুগল দিয়ে সাইন ইন করুন",
    emailBtn: "ইমেল দিয়ে সাইন ইন করুন",
    emailLabel: "ইমেল ঠিকানা",
    passLabel: "পাসওয়ার্ড",
    loginBtn: "অ্যাকাউন্ট যুক্ত করুন",
    registerBtn: "ইয়ার রেজিস্টার করুন",
    toggleSignUp: "ইয়ারে নতুন? সাইন আপ করুন",
    toggleLogIn: "অ্যাকাউন্ট আছে? লগ ইন করুন",
    goBack: "পিছনে যান",
    nameLabel: "আপনার নাম"
  },
  Tamil: {
    googleBtn: "கூகுள் மூலம் தொடரவும்",
    emailBtn: "மின்னஞ்சல் மூலம் தொடரவும்",
    emailLabel: "மின்னஞ்சல் முகவரி",
    passLabel: "கடவுச்சொல்",
    loginBtn: "கணக்கை இணைக்கவும்",
    registerBtn: "யாரை பதிவு செய்யவும்",
    toggleSignUp: "யாருக்கு புதியவரா? பதிவு செய்யவும்",
    toggleLogIn: "கணக்கு உள்ளதா? உள்நுழையவும்",
    goBack: "பின்னால் செல்லவும்",
    nameLabel: "உங்கள் பெயர்"
  }
};

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
  { id: "Sindhi", label: "سنڌि (Sindhi)" },
  { id: "Dogri", label: "डोगरी (Dogri)" },
  { id: "Manipuri", label: "মৈতৈলোন (Manipuri)" },
  { id: "Bodo", label: "बर' (Bodo)" },
  { id: "Sanskrit", label: "संस्कृतम् (Sanskrit)" }
];

const COMPANION_GREETINGS: Record<string, { welcome: string; friend: string; queryPlaceholder: string }> = {
  English: { welcome: "Hello", friend: "Friend", queryPlaceholder: "Ask Yaar anything to get started..." },
  Hindi: { welcome: "नमस्ते", friend: "दोस्त", queryPlaceholder: "यार से कुछ भी पूछें..." },
  Punjabi: { welcome: "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ", friend: "ਵੀਰੇ", queryPlaceholder: "ਯਾਰ ਤੋਂ ਕੁਝ ਵੀ ਪੁੱਛੋ..." },
  Bengali: { welcome: "নমস্কার", friend: "বন্ধু", queryPlaceholder: "ইয়ারকে যেকোনো প্রশ্ন করুন..." },
  Telugu: { welcome: "నమస్కారం", friend: "మిత్రమా", queryPlaceholder: "యార్‌ను ఏదైనా అడగండి..." },
  Marathi: { welcome: "नमस्कार", friend: "मित्रा", queryPlaceholder: "यारला काहीही विचारा..." },
  Tamil: { welcome: "வணக்கம்", friend: "நண்பா", queryPlaceholder: "யாரிடம் எதையும் கேளுங்கள்..." },
  Urdu: { welcome: "السلام علیکم", friend: "دوست", queryPlaceholder: "یار سے کچھ بھی پوچھیں..." },
  Gujarati: { welcome: "કેમ છો", friend: "મિત્ર", queryPlaceholder: "યાર ને ગમે તે પૂછો..." },
  Kannada: { welcome: "ನಮಸ್ಕಾರ", friend: "ಸ್ನೇಹಿತನೇ", queryPlaceholder: "ಯಾರ್ ಬಳಿ ಏನಾದರೂ ಕೇಳಿ..." },
  Malayalam: { welcome: "നമസ്കാരം", friend: "கூட்டുകாരാ", queryPlaceholder: "യാറിനോട് എന്ത് വേണമെങ്കിലും ചോദിക്കൂ..." },
  Odia: { welcome: "ନମସ୍କାର", friend: "ବନ୍ଧୁ", queryPlaceholder: "ୟାର୍‌କୁ କିଛି ବି ପଚାରନ୍ତု..." },
  Assamese: { welcome: "নమস্কাৰ", friend: "বন্ধু", queryPlaceholder: "য়াৰক যিকোনো কথা সোধক..." },
  Maithili: { welcome: "प्रणाम", friend: "सखा", queryPlaceholder: "यार सँ किछू पुछू..." },
  Santali: { welcome: "ᱡᱚᱦᱟᱨ", friend: "ᱜᱟᱛᱮ", queryPlaceholder: "ᱭᱟᱨ ᱡᱟᱦᱟᱸᱱᱟᱜ ᱜੇ ᱠᱩᱞིᱭեਮ..." },
  Kashmiri: { welcome: "تسلّم", friend: "دوست", queryPlaceholder: "یارس کینہہ تہِ ژھارو..." },
  Nepali: { welcome: "नमस्ते", friend: "साथी", queryPlaceholder: "यारलाई जे पनि सोध्नुहोस्..." },
  Konkani: { welcome: "नमस्कार", friend: "इष्टा", queryPlaceholder: "यारा कडे कितेंय विचारात..." },
  Sindhi: { welcome: "سلام", friend: "دوست", queryPlaceholder: "يار کان ڪجھہ بہ پڇو..." },
  Dogri: { welcome: "नमस्ते", friend: "मित्तर", queryPlaceholder: "यार थमां किश बी पुच्छो..." },
  Manipuri: { welcome: "খুরুমজরি", friend: "মরুপ", queryPlaceholder: "ইয়ারদা করিশুম্বা হাংবীয়ু..." },
  Bodo: { welcome: "खुलुमबाय", friend: "लोगो", queryPlaceholder: "यारखौ जेबो सोंनो हागोन..." },
  Sanskrit: { welcome: "नमो नमः", friend: "मित्र", queryPlaceholder: "यारं किमपि पृच्छत..." }
};

const LOGIN_GREETINGS: Record<string, string> = {
  English: "Hello Friend 👋",
  Hindi: "Namaste Dost 🙏",
  Punjabi: "Sat Sri Akal Veere 🙏",
  Gujarati: "Kem Cho Mitra 👋",
  Tamil: "Vanakkam Nanba 👋",
  Bengali: "Nomoshkar 👋"
};

export default function Home() {
  const [activeConversationId, setActiveConversationId] = useState<number | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  
  // Navigation tabs
  const [activeTab, setActiveTab] = useState<string>("lifehub");

  // Session recovery helper
  const saveSessionState = (tab: string, convId?: number | null) => {
    if (typeof window !== "undefined") {
      localStorage.setItem("yaar_last_tab", tab);
      if (convId !== undefined) {
        if (convId) localStorage.setItem("yaar_last_conversation", convId.toString());
        else localStorage.removeItem("yaar_last_conversation");
      }
    }
  };

  const handleTabChange = (tab: string) => {
    setActiveTab(tab);
    saveSessionState(tab);
  };

  // Auth states
  const [token, setToken] = useState<string | null>(null);
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authError, setAuthError] = useState("");
  const [authLoading, setAuthLoading] = useState(false);
  const [showEmailFields, setShowEmailFields] = useState(false);
  const [mounted, setMounted] = useState(false);

  // Setup workflows state machine
  // 0: Greeting cycle, 1: Language selection, 2: YAAR intro, 3: Name entry, 4: Login portal, 5: Onboarding wizard, 6: Main App, 7: Account Picker
  const [setupStep, setSetupStep] = useState<number>(0);

  // User details
  const [userName, setUserName] = useState("");
  const [selectedLang, setSelectedLang] = useState("English");
  const [selectedVibe, setSelectedVibe] = useState("friendly");
  const [theme, setTheme] = useState("dark-indigo");

  // Account Picker / Returning Visitor states
  const [selectedAccount, setSelectedAccount] = useState<any | null>(null);
  const [loginPassword, setLoginPassword] = useState("");
  const [showAccountList, setShowAccountList] = useState(false);

  // Cmd+K command bar
  const [isCommandBarOpen, setIsCommandBarOpen] = useState(false);
  const [landingInput, setLandingInput] = useState("");
  const [isMobile, setIsMobile] = useState(false);

  // Hidden Beta Tester Mode
  const [betaTesterMode, setBetaTesterMode] = useState(false);
  const [feedbackType, setFeedbackType] = useState<"issue" | "improvement" | "loved" | null>(null);
  const [feedbackText, setFeedbackText] = useState("");
  const [expectedBehavior, setExpectedBehavior] = useState("");
  const [feedbackSuccessToast, setFeedbackSuccessToast] = useState(false);

  // Check Inactivity Expiry (P0 Memory System)
  const updateSessionExpiry = () => {
    if (typeof window !== "undefined") {
      const expiry = Date.now() + 15 * 60 * 1000; // 15 mins
      localStorage.setItem("yaar_session_expiry", expiry.toString());
    }
  };

  const handleLanguageChange = (newLang: string) => {
    setSelectedLang(newLang);
    localStorage.setItem("yaar_language", newLang);
    
    // Update active user session if logged in
    const activeUserStr = localStorage.getItem("yaar_active_user");
    if (activeUserStr) {
      try {
        const activeUser = JSON.parse(activeUserStr);
        activeUser.language = newLang;
        localStorage.setItem("yaar_active_user", JSON.stringify(activeUser));
        
        // Update in accounts registry
        const accountsStr = localStorage.getItem("yaar_accounts");
        if (accountsStr) {
          const accounts = JSON.parse(accountsStr);
          const updatedAccounts = accounts.map((acc: any) => {
            if (acc.email.toLowerCase() === activeUser.email.toLowerCase()) {
              return { ...acc, language: newLang };
            }
            return acc;
          });
          localStorage.setItem("yaar_accounts", JSON.stringify(updatedAccounts));
        }
      } catch (_) {}
    }
    
    setRefreshTrigger(prev => prev + 1);
  };

  useEffect(() => {
    setMounted(true);
    if (typeof window !== "undefined") {
      const handleResize = () => {
        setIsMobile(window.innerWidth < 768);
      };
      handleResize();
      window.addEventListener("resize", handleResize);

      setSidebarOpen(window.innerWidth >= 768);

      // Local storage reads
      const savedLang = localStorage.getItem("yaar_language") || "English";
      const savedVibe = localStorage.getItem("yaar_personality") || "friendly";
      const savedName = localStorage.getItem("yaar_user_name") || "";
      const savedTheme = localStorage.getItem("yaar_theme") || "dark-indigo";
      
      setSelectedLang(savedLang);
      setSelectedVibe(savedVibe);
      setUserName(savedName);
      setTheme(savedTheme);

      // Step Flow evaluation on mount
      const savedToken = localStorage.getItem("bharatai_token");
      if (savedToken) {
        // Expiry check
        const expiry = localStorage.getItem("yaar_session_expiry");
        if (expiry && Date.now() > parseInt(expiry)) {
          localStorage.removeItem("bharatai_token");
          localStorage.removeItem("bharatai_email");
          localStorage.removeItem("yaar_active_user");
          setToken(null);
          setUserName("");
          
          const accountsStr = localStorage.getItem("yaar_accounts");
          let accountsList = [];
          if (accountsStr) {
            try { accountsList = JSON.parse(accountsStr); } catch (_) {}
          }
          if (accountsList.length > 0) {
            setSelectedAccount(accountsList[0]);
            setShowAccountList(accountsList.length > 1);
            setSetupStep(7);
          } else {
            setSetupStep(4); // Direct to login
          }
        } else {
          setToken(savedToken);
          // Load active user
          const activeUserStr = localStorage.getItem("yaar_active_user");
          if (activeUserStr) {
            try {
              const activeUser = JSON.parse(activeUserStr);
              setUserName(activeUser.name);
              setSelectedLang(activeUser.language || "English");
            } catch (_) {}
          }
          // Session Recovery: restore last tab and conversation
          const lastTab = localStorage.getItem("yaar_last_tab") || "lifehub";
          const lastConvStr = localStorage.getItem("yaar_last_conversation");
          setActiveTab(lastTab);
          if (lastConvStr) {
            const lastConvId = parseInt(lastConvStr);
            if (!isNaN(lastConvId)) setActiveConversationId(lastConvId);
          }
          setSetupStep(6); // Go to main dashboard
          updateSessionExpiry();
        }
      } else {
        const splashSeen = sessionStorage.getItem("yaar_splash_seen");
        if (!splashSeen) {
          setSetupStep(0); // Show rotating greetings first
        } else {
          const accountsStr = localStorage.getItem("yaar_accounts");
          let accountsList = [];
          if (accountsStr) {
            try { accountsList = JSON.parse(accountsStr); } catch (_) {}
          }
          if (accountsList.length > 0) {
            setSelectedAccount(accountsList[0]);
            setShowAccountList(accountsList.length > 1);
            setSetupStep(7); // Show account picker
          } else {
            setSetupStep(1); // Set language
          }
        }
      }

      // Load initial beta tester mode state
      const savedBetaMode = localStorage.getItem("yaar_beta_tester_mode") === "true";
      setBetaTesterMode(savedBetaMode);

      const handleBetaChange = () => {
        const updated = localStorage.getItem("yaar_beta_tester_mode") === "true";
        setBetaTesterMode(updated);
      };
      window.addEventListener("yaar_beta_mode_changed", handleBetaChange);

      return () => {
        window.removeEventListener("resize", handleResize);
        window.removeEventListener("yaar_beta_mode_changed", handleBetaChange);
      };
    }
  }, []);

  // Inactivity activity listener & background expiry checker
  useEffect(() => {
    if (setupStep === 6 && token) {
      const handleActivity = () => updateSessionExpiry();
      window.addEventListener("mousedown", handleActivity);
      window.addEventListener("keydown", handleActivity);
      
      const interval = setInterval(() => {
        const expiry = localStorage.getItem("yaar_session_expiry");
        if (expiry && Date.now() > parseInt(expiry)) {
          handleLogout();
        }
      }, 10000); // Check every 10 seconds
      
      return () => {
        window.removeEventListener("mousedown", handleActivity);
        window.removeEventListener("keydown", handleActivity);
        clearInterval(interval);
      };
    }
  }, [setupStep, token]);

  const handleOpenFeedbackDialog = (type: "issue" | "improvement" | "loved") => {
    setFeedbackType(type);
    setFeedbackText("");
    setExpectedBehavior("");
  };

  const generateCanvasScreenshot = (tab: string, conversationId: number | null): string => {
    if (typeof document === "undefined") return "";
    try {
      const canvas = document.createElement("canvas");
      canvas.width = 300;
      canvas.height = 200;
      const ctx = canvas.getContext("2d");
      if (!ctx) return "";

      // Draw background (dark blue/black)
      ctx.fillStyle = "#06070d";
      ctx.fillRect(0, 0, 300, 200);

      // Draw sidebar (left column, width 60px)
      ctx.fillStyle = "#121316";
      ctx.fillRect(0, 0, 60, 200);
      ctx.strokeStyle = "rgba(255,255,255,0.05)";
      ctx.beginPath();
      ctx.moveTo(60, 0);
      ctx.lineTo(60, 200);
      ctx.stroke();

      // Draw simulated sidebar items
      ctx.fillStyle = "#334155";
      for (let i = 0; i < 4; i++) {
        ctx.fillRect(10, 15 + i * 20, 40, 6);
      }

      // Draw active workspace tab / chat interface on the right (width 240px)
      ctx.fillStyle = "#0c0d12";
      ctx.fillRect(60, 0, 240, 200);

      // Draw header (height 30px)
      ctx.fillStyle = "#121316";
      ctx.fillRect(60, 0, 240, 30);

      // Draw active page indicator text
      ctx.fillStyle = "#ffffff";
      ctx.font = "bold 8px sans-serif";
      ctx.fillText(conversationId ? `Chat: Session #${conversationId}` : `Tab: ${tab}`, 70, 18);

      // Draw simulated content depending on view
      if (conversationId) {
        // Chat interface
        // User bubble
        ctx.fillStyle = "rgba(245, 158, 11, 0.1)";
        ctx.fillRect(160, 50, 130, 25);
        ctx.fillStyle = "#f59e0b";
        ctx.font = "6px sans-serif";
        ctx.fillText("User query input simulation", 165, 60);

        // Companion bubble
        ctx.fillStyle = "rgba(255, 255, 255, 0.05)";
        ctx.fillRect(70, 90, 150, 40);
        ctx.fillStyle = "#94a3b8";
        ctx.fillText("Companion response simulation...", 75, 102);
        ctx.fillText("Source: From Document", 75, 122);
      } else {
        // Other tabs
        ctx.fillStyle = "rgba(255, 255, 255, 0.02)";
        ctx.fillRect(70, 45, 220, 140);
        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 10px sans-serif";
        ctx.fillText(tab, 80, 65);
        ctx.fillStyle = "#475569";
        ctx.font = "7px sans-serif";
        ctx.fillText("Workspace Dashboard Interface Simulator", 80, 85);
      }

      // Draw Simulated Yaar Orb in bottom right corner
      ctx.fillStyle = "#f59e0b";
      ctx.beginPath();
      ctx.arc(275, 175, 12, 0, 2 * Math.PI);
      ctx.fill();

      // Compress to base64 jpeg at 0.4 quality
      return canvas.toDataURL("image/jpeg", 0.4);
    } catch (_) {
      return "";
    }
  };

  const handleSubmitFeedback = (e: React.FormEvent) => {
    e.preventDefault();
    if (!feedbackText.trim() || !feedbackType) return;

    const simulatedScreenshot = generateCanvasScreenshot(activeTab, activeConversationId);

    const report = {
      id: `report-${Date.now()}`,
      type: feedbackType,
      message: feedbackText.trim(),
      expectedBehavior: expectedBehavior.trim(),
      currentPage: activeConversationId ? `chat-${activeConversationId}` : activeTab,
      language: selectedLang,
      viewport: `${window.innerWidth}x${window.innerHeight}`,
      timestamp: new Date().toISOString(),
      screenshot: simulatedScreenshot,
      browser: navigator.userAgent
    };

    if (typeof window !== "undefined") {
      const existing = JSON.parse(localStorage.getItem("yaar_beta_reports") || "[]");
      existing.push(report);
      localStorage.setItem("yaar_beta_reports", JSON.stringify(existing));
    }

    setFeedbackType(null);
    setFeedbackText("");
    setExpectedBehavior("");
    setFeedbackSuccessToast(true);

    setTimeout(() => {
      setFeedbackSuccessToast(false);
    }, 3000);
  };

  // Universal Cmd+K listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setIsCommandBarOpen(prev => !prev);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const handleRefreshSidebar = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  // Login: Mock Google Authenticator
  const handleMockGoogleLogin = () => {
    setAuthLoading(true);
    setTimeout(() => {
      const email = "companion@yaar.ai";
      // Auto seed mock database if not already
      let users = [];
      const localUsers = localStorage.getItem("yaar_users");
      if (localUsers) {
        try { users = JSON.parse(localUsers); } catch (_) {}
      }
      const exists = users.find((u: any) => u.email === email);
      if (!exists) {
        users.push({ email, password: "google-mock-pass", name: userName || "Friend" });
        localStorage.setItem("yaar_users", JSON.stringify(users));
      }

      // Check / Create in accounts registry
      let accounts = [];
      const accountsStr = localStorage.getItem("yaar_accounts");
      if (accountsStr) {
        try { accounts = JSON.parse(accountsStr); } catch (_) {}
      }
      let existingAccount = accounts.find((a: any) => a.email.toLowerCase() === email.toLowerCase());
      if (!existingAccount) {
        existingAccount = {
          id: Date.now().toString(),
          email: email.toLowerCase(),
          name: userName || "Friend",
          displayName: userName || "Friend",
          provider: "demo_google",
          language: selectedLang,
          avatar: (userName || "Friend").slice(0, 2).toUpperCase(),
          createdAt: new Date().toISOString()
        };
        accounts.push(existingAccount);
        localStorage.setItem("yaar_accounts", JSON.stringify(accounts));
      } else {
        existingAccount.provider = "demo_google";
        existingAccount.displayName = existingAccount.name || existingAccount.displayName;
        if (!existingAccount.createdAt) {
          existingAccount.createdAt = new Date().toISOString();
        }
        delete existingAccount.password;
        localStorage.setItem("yaar_accounts", JSON.stringify(accounts));
      }

      setUserName(existingAccount.name || existingAccount.displayName);
      localStorage.setItem("yaar_user_name", existingAccount.name || existingAccount.displayName);
      localStorage.setItem("yaar_active_user", JSON.stringify(existingAccount));
      localStorage.setItem("bharatai_token", "google-mock-jwt-token-yaar");
      localStorage.setItem("bharatai_email", email);
      setToken("google-mock-jwt-token-yaar");
      setAuthLoading(false);
      updateSessionExpiry();
      setRefreshTrigger(prev => prev + 1);
      
      const interest = localStorage.getItem("yaar_onboarding_interest");
      if (!interest) {
        setSetupStep(5); // Onboarding vibe & focus
      } else {
        setSetupStep(6); // Life Hub dashboard
      }
    }, 600);
  };

  // Login: Mock Email Login/Register Action
  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError("");
    setAuthLoading(true);

    setTimeout(() => {
      let users: any[] = [];
      const localUsers = localStorage.getItem("yaar_users");
      if (localUsers) {
        try { users = JSON.parse(localUsers); } catch (_) {}
      }

      if (!isLoginMode) {
        // Register Mode
        const exists = users.find((u: any) => u.email.toLowerCase() === email.toLowerCase());
        if (exists) {
          setAuthError("An account with this email already exists.");
          setAuthLoading(false);
          return;
        }

        const newUser = {
          email: email.toLowerCase(),
          password: password,
          name: userName || "Friend"
        };
        users.push(newUser);
        localStorage.setItem("yaar_users", JSON.stringify(users));

        // Create in accounts registry
        let accounts: any[] = [];
        const accountsStr = localStorage.getItem("yaar_accounts");
        if (accountsStr) {
          try { accounts = JSON.parse(accountsStr); } catch (_) {}
        }
        const newAccount = {
          id: Date.now().toString(),
          email: email.toLowerCase(),
          name: userName || "Friend",
          displayName: userName || "Friend",
          provider: "email",
          language: selectedLang,
          avatar: (userName || "Friend").slice(0, 2).toUpperCase(),
          createdAt: new Date().toISOString(),
          password: password
        };
        accounts.push(newAccount);
        localStorage.setItem("yaar_accounts", JSON.stringify(accounts));

        // Set session
        localStorage.setItem("yaar_active_user", JSON.stringify(newAccount));
        localStorage.setItem("bharatai_token", `mock-token-${email}`);
        localStorage.setItem("bharatai_email", email.toLowerCase());
        setToken(`mock-token-${email}`);
        setUserName(newAccount.name || newAccount.displayName);
        setAuthLoading(false);
        updateSessionExpiry();
        setSetupStep(5); // Onboarding
      } else {
        // Login Mode
        const account = users.find((u: any) => u.email.toLowerCase() === email.toLowerCase() && u.password === password);
        if (!account) {
          setAuthError("Invalid email or password.");
          setAuthLoading(false);
          return;
        }

        // Match found! Load username & language
        setUserName(account.name);
        localStorage.setItem("yaar_user_name", account.name);

        // Check if in accounts registry, if not, add it
        let accounts: any[] = [];
        const accountsStr = localStorage.getItem("yaar_accounts");
        if (accountsStr) {
          try { accounts = JSON.parse(accountsStr); } catch (_) {}
        }
        let existingAccount = accounts.find(a => a.email.toLowerCase() === email.toLowerCase());
        if (!existingAccount) {
          existingAccount = {
            id: Date.now().toString(),
            email: email.toLowerCase(),
            name: account.name,
            displayName: account.name,
            provider: "email",
            language: selectedLang,
            avatar: account.name.slice(0, 2).toUpperCase(),
            createdAt: new Date().toISOString(),
            password: password
          };
          accounts.push(existingAccount);
          localStorage.setItem("yaar_accounts", JSON.stringify(accounts));
        } else {
          existingAccount.provider = "email";
          existingAccount.displayName = existingAccount.name || existingAccount.displayName;
          if (!existingAccount.createdAt) {
            existingAccount.createdAt = new Date().toISOString();
          }
          existingAccount.password = password;
          localStorage.setItem("yaar_accounts", JSON.stringify(accounts));
        }

        localStorage.setItem("yaar_active_user", JSON.stringify(existingAccount));
        localStorage.setItem("bharatai_token", `mock-token-${email}`);
        localStorage.setItem("bharatai_email", email.toLowerCase());
        setToken(`mock-token-${email}`);
        setAuthLoading(false);
        updateSessionExpiry();
        setRefreshTrigger(prev => prev + 1);
        
        const interest = localStorage.getItem("yaar_onboarding_interest");
        if (!interest) {
          setSetupStep(5);
        } else {
          setSetupStep(6);
        }
      }
    }, 600);
  };

  const handleLogout = () => {
    localStorage.removeItem("bharatai_token");
    localStorage.removeItem("bharatai_email");
    localStorage.removeItem("yaar_session_expiry");
    localStorage.removeItem("yaar_active_user");
    localStorage.removeItem("yaar_last_tab");
    localStorage.removeItem("yaar_last_conversation");
    setToken(null);
    setUserName("");
    setActiveConversationId(null);
    setActiveTab("lifehub");
    
    // Check if accounts exist to show returning account picker
    const accountsStr = localStorage.getItem("yaar_accounts");
    let accountsList = [];
    if (accountsStr) {
      try { accountsList = JSON.parse(accountsStr); } catch (_) {}
    }
    if (accountsList.length > 0) {
      setSelectedAccount(accountsList[0]);
      setShowAccountList(accountsList.length > 1);
      setSetupStep(7); // Show account picker
    } else {
      setSetupStep(4); // Back to login screen
    }
  };

  const handleNewChatFromLifeHub = async (initialPrompt = "") => {
    if (!token) return;
    const email = localStorage.getItem("bharatai_email") || "companion@yaar.ai";
    const localChatsKey = `yaar_chats_${email}`;

    // Create locally
    const mockId = Date.now();
    const newConv = {
      id: mockId,
      title: initialPrompt.trim() ? (initialPrompt.length > 25 ? initialPrompt.slice(0, 25) + "..." : initialPrompt) : "New Conversation",
      created_at: new Date().toISOString(),
      document_id: null,
      document_name: null
    };

    // Load existing
    let list: any[] = [];
    const saved = localStorage.getItem(localChatsKey);
    if (saved) {
      try { list = JSON.parse(saved); } catch (_) {}
    }
    const updated = [newConv, ...list];
    localStorage.setItem(localChatsKey, JSON.stringify(updated));

    // Save prompt if pending
    if (initialPrompt.trim()) {
      localStorage.setItem(`yaar_pending_prompt`, initialPrompt.trim());
    }

    setActiveConversationId(mockId);
    handleRefreshSidebar();
    if (isMobile) {
      setSidebarOpen(false);
    }

    // Try backend sync in background
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
        // Replace local mock ID
        const synced = updated.map(c => c.id === mockId ? { ...c, id: data.id } : c);
        localStorage.setItem(localChatsKey, JSON.stringify(synced));
        setActiveConversationId(data.id);
        handleRefreshSidebar();
      }
    } catch (_) {}
  };

  const handleSelectCommandAction = async (action: string) => {
    switch (action) {
      case "new-chat":
      case "ask-yaar":
        await handleNewChatFromLifeHub();
        break;
      case "search-vault":
        setActiveConversationId(null);
        setActiveTab("vault");
        break;
      case "open-project":
        setActiveConversationId(null);
        setActiveTab("projects");
        break;
      default:
        break;
    }
  };

  const getLoginGreeting = () => {
    const name = userName ? userName.trim() : "";
    if (!name) {
      return LOGIN_GREETINGS[selectedLang] || "Hello Friend 👋";
    }
    switch (selectedLang) {
      case "Hindi": return `नमस्ते ${name} 🙏`;
      case "Punjabi": return `ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ ${name} 🙏`;
      case "Gujarati": return `કેમ છો ${name} 👋`;
      case "Tamil": return `வணக்கம் ${name} 👋`;
      case "Bengali": return `নমস্কার ${name} 👋`;
      default: return `Hello ${name} 👋`;
    }
  };

  if (!mounted) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-[#06070d]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 rounded-full border-2 border-amber-900 border-t-amber-500 animate-spin"></div>
          <span className="text-[10px] font-black uppercase tracking-wider text-slate-500">Connecting with Yaar...</span>
        </div>
      </div>
    );
  }

  // -------------------- SETUP FLOW RENDERING --------------------

  // STEP 0: Rotating Greeting Splash Screen
  if (setupStep === 0) {
    return (
      <GreetingSplash
        onComplete={() => {
          sessionStorage.setItem("yaar_splash_seen", "true");
          setSetupStep(1); // Proceed to Language Selection
        }}
      />
    );
  }

  // STEP 1: First-Class Language Selection
  if (setupStep === 1) {
    const handleLangSelect = (id: string) => {
      handleLanguageChange(id);
    };
    return (
      <div className="flex h-screen w-screen items-center justify-center relative p-4 bg-[#06070d] overflow-hidden select-none">
        <AmbientCanvas />
        <div className="w-full max-w-xl p-8 rounded-3xl bg-[#121316]/95 border border-white/5 shadow-2xl z-10 flex flex-col gap-6 items-center text-center animate-fade-in">
          <div className="space-y-1.5">
            <div className="w-10 h-10 rounded-2xl bg-amber-950/20 border border-amber-900/30 text-amber-500 flex items-center justify-center mx-auto mb-2">
              <Languages className="w-5 h-5" />
            </div>
            <h2 className="text-2xl sm:text-3xl font-black text-white tracking-tight font-display">
              Choose Your Language
            </h2>
            <p className="text-slate-450 text-[11px] font-semibold max-w-sm mx-auto leading-relaxed">
              Select your primary tongue. YAAR will customize its interface labels, prompts, and tone.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-3 w-full my-1 max-h-[280px] overflow-y-auto pr-1.5 scroll-smooth-premium border border-white/5 bg-slate-900/10 rounded-2xl p-3">
            {LANGUAGES.map((l) => {
              const isSelected = selectedLang === l.id;
              return (
                <button
                  key={l.id}
                  onClick={() => handleLangSelect(l.id)}
                  className={`p-3 rounded-2xl border text-left flex flex-col gap-1 transition-premium cursor-pointer ${
                    isSelected ? "bg-amber-950/30 border-amber-500 shadow-md shadow-amber-500/5" : "bg-slate-900/10 border-white/5 hover:bg-slate-800/20"
                  }`}
                >
                  <span className="text-sm font-black text-white">{l.label.split(" (")[0]}</span>
                  <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">{l.id}</span>
                </button>
              );
            })}
          </div>
          <button
            onClick={() => setSetupStep(2)}
            className="w-full py-3.5 bg-white hover:bg-slate-100 text-slate-950 text-xs font-black uppercase tracking-widest rounded-xl transition-premium shadow-md shadow-black/10 cursor-pointer text-center"
          >
            Continue →
          </button>
        </div>
      </div>
    );
  }
  // STEP 2: YAAR Companion Introduction
  if (setupStep === 2) {
    return (
      <div className="flex h-screen w-screen items-center justify-center relative p-4 bg-[#06070d] overflow-hidden select-none">
        <AmbientCanvas />
        <div className="w-full max-w-md p-8 rounded-3xl bg-[#121316]/95 border border-white/5 shadow-2xl z-10 flex flex-col gap-6 items-center text-center animate-fade-in">
          <YaarOrb state="idle" size="md" className="my-2" />
          
          <div className="space-y-3">
            <h2 className="text-3xl font-black text-white tracking-tight font-display">
              I{"'"}m Yaar.
            </h2>
            <p className="text-slate-350 text-xs font-semibold leading-relaxed max-w-sm">
              I am here to help you learn, work, build, and explore.<br/>
              I am your digital companion.<br/>
              Not a chatbot. Not an assistant.
            </p>
          </div>

          <button
            onClick={() => setSetupStep(3)}
            className="w-full py-3.5 mt-2 bg-amber-600 hover:bg-amber-500 text-white text-xs font-black uppercase tracking-widest rounded-xl transition-premium shadow-md shadow-amber-950/20 cursor-pointer text-center"
          >
            Next →
          </button>
        </div>
      </div>
    );
  }

  // STEP 3: User Name Entry
  if (setupStep === 3) {
    const handleNameSubmit = (e: React.FormEvent) => {
      e.preventDefault();
      if (!userName.trim()) return;
      localStorage.setItem("yaar_user_name", userName.trim());
      setSetupStep(4); // Proceed to Login Screen
    };

    return (
      <div className="flex h-screen w-screen items-center justify-center relative p-4 bg-[#06070d] overflow-hidden select-none">
        <AmbientCanvas />
        <form
          onSubmit={handleNameSubmit}
          className="w-full max-w-md p-8 rounded-3xl bg-[#121316]/95 border border-white/5 shadow-2xl z-10 flex flex-col gap-6 items-center text-center animate-fade-in"
        >
          <YaarOrb state="idle" size="sm" className="my-1 animate-pulse" />
          
          <div className="space-y-1 w-full">
            <h2 className="text-xl sm:text-2xl font-black text-white tracking-tight font-display">
              What should I call you?
            </h2>
            <p className="text-slate-500 text-[10px] uppercase font-black tracking-widest">
              Introduce Yourself
            </p>
          </div>

          <input
            type="text"
            required
            autoFocus
            value={userName}
            onChange={(e) => setUserName(e.target.value)}
            placeholder="e.g. Manpreet"
            className="w-full px-4 py-3 rounded-xl bg-slate-900/50 border border-white/5 text-white text-xs font-bold text-center placeholder-slate-600 outline-none focus:border-amber-500 transition-premium"
          />

          <button
            type="submit"
            className="w-full py-3.5 bg-white hover:bg-slate-100 text-slate-950 text-xs font-black uppercase tracking-widest rounded-xl transition-premium shadow-md shadow-black/10 cursor-pointer text-center"
          >
            Continue →
          </button>
        </form>
      </div>
    );
  }

  // STEP 4: Redesigned Login Portal with Dynamic Greetings
  if (setupStep === 4) {
    const lText = LOCALIZED_LOGIN_TEXTS[selectedLang] || LOCALIZED_LOGIN_TEXTS["English"];

    return (
      <div className="flex h-screen w-screen items-center justify-center relative p-4 bg-[#06070d] overflow-hidden">
        <AmbientCanvas />

        <div className="w-full max-w-md p-8 rounded-3xl bg-[#121316]/90 backdrop-blur-xl border border-white/5 shadow-2xl z-10 flex flex-col gap-6 items-center text-center animate-fade-in">
          
          <div className="flex justify-end w-full -mb-4">
            <div className="flex items-center gap-1 text-[10px] font-bold text-slate-500">
              <Languages className="w-3.5 h-3.5 text-slate-500" />
              <select
                value={selectedLang}
                onChange={(e) => {
                  const newLang = e.target.value;
                  handleLanguageChange(newLang);
                }}
                className="bg-transparent border-none outline-none text-slate-450 cursor-pointer hover:text-white font-bold"
              >
                {LANGUAGES.map(l => (
                  <option key={l.id} value={l.id} className="bg-[#121316] text-white">{l.label}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="space-y-1.5">
            <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-white font-display">
              {getLoginGreeting()}
            </h1>
            <p className="text-slate-400 text-xs font-semibold leading-normal">
              Let{"'"}s secure your companion binder and proceed.
            </p>
            <p className="text-amber-550 text-[9px] uppercase font-black tracking-widest pt-1">
              SOVEREIGN COMPANION SAFEGUARD
            </p>
          </div>

          <YaarOrb state="idle" size="md" className="my-1" />

          {authError && (
            <div className="w-full p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-450 text-[10px] font-bold text-center uppercase tracking-wider">
              {authError}
            </div>
          )}

          {/* Login Actions */}
          <div className="w-full flex flex-col gap-3">
            {authLoading ? (
              <div className="w-full py-3.5 bg-slate-950 border border-white/5 rounded-xl flex items-center justify-center gap-2">
                <div className="w-4 h-4 border-2 border-amber-500/30 border-t-amber-500 rounded-full animate-spin"></div>
                <span className="text-xs text-slate-450 font-bold uppercase tracking-wider">Authenticating...</span>
              </div>
            ) : (
              <>
                {!showEmailFields ? (
                  <>
                    <button
                      onClick={handleMockGoogleLogin}
                      className="w-full py-3.5 bg-white text-slate-950 text-xs font-black uppercase tracking-wider rounded-xl transition-premium hover:-translate-y-0.5 active:translate-y-0 cursor-pointer shadow-lg shadow-black/10 flex flex-col items-center justify-center gap-0.5"
                    >
                      <div className="flex items-center justify-center gap-2">
                        <svg className="w-4 h-4" viewBox="0 0 24 24">
                          <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                          <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                          <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
                          <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
                        </svg>
                        <span>Demo Google Login</span>
                      </div>
                      <span className="text-[8px] font-semibold text-slate-500 normal-case tracking-normal">Google Authentication Coming Soon</span>
                    </button>

                    <button
                      onClick={() => setShowEmailFields(true)}
                      className="w-full py-3.5 bg-[#06070d] hover:bg-slate-900/60 text-white text-xs font-black uppercase tracking-wider rounded-xl transition-premium hover:-translate-y-0.5 active:translate-y-0 cursor-pointer shadow-sm border border-white/5"
                    >
                      {lText.emailBtn}
                    </button>
                  </>
                ) : (
                  <form onSubmit={handleAuthSubmit} className="w-full flex flex-col gap-3.5 text-left animate-slide-in-right">
                    
                    {!isLoginMode && (
                      <div className="flex flex-col gap-1">
                        <label className="text-[9px] uppercase tracking-wider font-extrabold text-slate-500">{lText.nameLabel}</label>
                        <input
                          type="text"
                          required
                          value={userName}
                          onChange={e => setUserName(e.target.value)}
                          placeholder="e.g. Manpreet"
                          className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-900 text-white text-xs placeholder-slate-600 outline-none focus:border-amber-500 transition-premium"
                        />
                      </div>
                    )}

                    <div className="flex flex-col gap-1">
                      <label className="text-[9px] uppercase tracking-wider font-extrabold text-slate-500">{lText.emailLabel}</label>
                      <input
                        type="email"
                        required
                        value={email}
                        onChange={e => setEmail(e.target.value)}
                        placeholder="you@domain.com"
                        className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-900 text-white text-xs placeholder-slate-600 outline-none focus:border-amber-500 transition-premium"
                      />
                    </div>

                    <div className="flex flex-col gap-1">
                      <label className="text-[9px] uppercase tracking-wider font-extrabold text-slate-500">{lText.passLabel}</label>
                      <input
                        type="password"
                        required
                        value={password}
                        onChange={e => setPassword(e.target.value)}
                        placeholder="••••••••"
                        className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-900 text-white text-xs placeholder-slate-600 outline-none focus:border-amber-500 transition-premium"
                      />
                    </div>

                    <button
                      type="submit"
                      className="w-full py-3.5 mt-1 bg-amber-600 hover:bg-amber-500 text-white text-xs font-black uppercase tracking-wider rounded-xl transition-premium shadow-md shadow-amber-950/20 cursor-pointer text-center flex items-center justify-center gap-1.5"
                    >
                      {isLoginMode ? <LogIn className="w-4.5 h-4.5" /> : <UserPlus className="w-4.5 h-4.5" />}
                      <span>{isLoginMode ? lText.loginBtn : lText.registerBtn}</span>
                    </button>

                    <div className="flex items-center justify-between pt-2 text-[10px] font-bold text-slate-400">
                      <button
                        type="button"
                        onClick={() => setIsLoginMode(!isLoginMode)}
                        className="text-amber-500 hover:underline"
                      >
                        {isLoginMode ? lText.toggleSignUp : lText.toggleLogIn}
                      </button>
                      <button
                        type="button"
                        onClick={() => setShowEmailFields(false)}
                        className="text-slate-500 hover:text-white"
                      >
                        {lText.goBack}
                      </button>
                    </div>
                  </form>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    );
  }

  // STEP 5: Onboarding Wizard (Companion Vibe & Focus Binders)
  if (setupStep === 5) {
    return (
      <OnboardingWizard
        language={selectedLang}
        onComplete={(focus, vibe) => {
          setSelectedVibe(vibe);
          setSetupStep(6); // Landing complete! Go to Main App Life Hub
          handleRefreshSidebar();
        }}
      />
    );
  }

  // STEP 7: Account Picker / Returning Visitor
  if (setupStep === 7) {
    const accountsStr = (typeof window !== "undefined" ? localStorage.getItem("yaar_accounts") : "[]") || "[]";
    let accountsList: any[] = [];
    try { accountsList = JSON.parse(accountsStr); } catch (_) {}

    if (accountsList.length === 0) {
      setSetupStep(1);
      return null;
    }

    const currentAcc = selectedAccount || accountsList[0] || null;

    const handleContinue = (e?: React.FormEvent) => {
      if (e) e.preventDefault();
      if (!currentAcc) return;
      
      setAuthError("");
      setAuthLoading(true);
      
      setTimeout(() => {
        // Validate password (skip if demo_google or default companion email)
        const isDemoGoogle = currentAcc.provider === "demo_google" || currentAcc.email.toLowerCase() === "companion@yaar.ai";
        if (!isDemoGoogle) {
          if (currentAcc.password && loginPassword !== currentAcc.password) {
            setAuthError("Incorrect password. Please try again.");
            setAuthLoading(false);
            return;
          }
        }
        
        // Log in!
        setUserName(currentAcc.name);
        setSelectedLang(currentAcc.language || "English");
        localStorage.setItem("yaar_user_name", currentAcc.name);
        localStorage.setItem("yaar_language", currentAcc.language || "English");
        localStorage.setItem("yaar_active_user", JSON.stringify(currentAcc));
        localStorage.setItem("bharatai_token", `mock-token-${currentAcc.email}`);
        localStorage.setItem("bharatai_email", currentAcc.email.toLowerCase());
        setToken(`mock-token-${currentAcc.email}`);
        setAuthLoading(false);
        setLoginPassword("");
        updateSessionExpiry();
        setRefreshTrigger(prev => prev + 1);
        
        // Redirect
        const interest = localStorage.getItem("yaar_onboarding_interest");
        if (!interest) {
          setSetupStep(5);
        } else {
          setSetupStep(6);
        }
      }, 600);
    };

    return (
      <div className="flex h-screen w-screen items-center justify-center relative p-4 bg-[#06070d] overflow-hidden">
        <AmbientCanvas />
        
        <div className="w-full max-w-md p-8 rounded-3xl bg-[#121316]/90 backdrop-blur-xl border border-white/5 shadow-2xl z-10 flex flex-col gap-6 items-center text-center animate-fade-in">
          
          <div className="flex justify-end w-full -mb-4">
            <div className="flex items-center gap-1 text-[10px] font-bold text-slate-500">
              <Languages className="w-3.5 h-3.5 text-slate-500" />
              <select
                value={selectedLang}
                onChange={(e) => {
                  const newLang = e.target.value;
                  handleLanguageChange(newLang);
                }}
                className="bg-transparent border-none outline-none text-slate-450 cursor-pointer hover:text-white font-bold"
              >
                {LANGUAGES.map(l => (
                  <option key={l.id} value={l.id} className="bg-[#121316] text-white">{l.label}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="space-y-1.5">
            <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-white font-display">
              Welcome Back
            </h1>
            <p className="text-slate-400 text-xs font-semibold leading-normal">
              Select your profile or connect another companion binder.
            </p>
          </div>

          {showAccountList ? (
            /* Show list of all accounts */
            <div className="w-full flex flex-col gap-2.5 max-h-[220px] overflow-y-auto pr-1">
              {accountsList.map((acc: any) => (
                <button
                  key={acc.id || acc.email}
                  onClick={() => {
                    setSelectedAccount(acc);
                    setShowAccountList(false);
                    setAuthError("");
                  }}
                  className="w-full p-3.5 rounded-2xl border border-white/5 bg-slate-900/40 hover:bg-slate-800/40 transition-premium flex items-center gap-3 text-left cursor-pointer"
                >
                  <div className="w-10 h-10 rounded-full bg-amber-600 flex items-center justify-center text-sm font-black text-white uppercase shrink-0">
                    {acc.avatar || acc.name.slice(0, 2).toUpperCase()}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-bold text-white truncate">{acc.name}</p>
                    <p className="text-[9px] font-bold text-slate-500 truncate">{acc.email}</p>
                  </div>
                  <ArrowRight className="w-4 h-4 text-slate-500" />
                </button>
              ))}
            </div>
          ) : (
            /* Show single selected account details and password */
            <div className="w-full flex flex-col items-center gap-4 animate-fade-in">
              <div className="flex flex-col items-center gap-2">
                <div className="w-16 h-16 rounded-full bg-amber-600 flex items-center justify-center text-2xl font-black text-white uppercase shadow-md shadow-amber-950/20">
                  {currentAcc?.avatar || currentAcc?.name?.slice(0, 2).toUpperCase()}
                </div>
                <div className="text-center">
                  <p className="text-[10px] text-slate-500 font-extrabold uppercase tracking-wider">Continue as</p>
                  <p className="text-base font-black text-white">{currentAcc?.name}</p>
                  <p className="text-[10px] text-slate-450 font-bold">{currentAcc?.email}</p>
                </div>
              </div>

              {authError && (
                <div className="w-full p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-450 text-[10px] font-bold text-center uppercase tracking-wider">
                  {authError}
                </div>
              )}

              <form onSubmit={handleContinue} className="w-full flex flex-col gap-3">
                {!((currentAcc?.provider === "demo_google") || (currentAcc?.email?.toLowerCase() === "companion@yaar.ai")) && (
                  <input
                    type="password"
                    placeholder="Enter Account Password"
                    required
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-900 text-white text-xs text-center placeholder-slate-600 outline-none focus:border-amber-500 transition-premium"
                  />
                )}

                <button
                  type="submit"
                  disabled={authLoading}
                  className="w-full py-3.5 bg-white text-slate-950 text-xs font-black uppercase tracking-wider rounded-xl transition-premium hover:-translate-y-0.5 active:translate-y-0 cursor-pointer shadow-lg shadow-black/10 flex items-center justify-center gap-1.5"
                >
                  {authLoading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-amber-950/30 border-t-amber-950 rounded-full animate-spin"></div>
                      <span>Connecting...</span>
                    </>
                  ) : (
                    <span>
                      {((currentAcc?.provider === "demo_google") || (currentAcc?.email?.toLowerCase() === "companion@yaar.ai")) 
                        ? "Continue with Google" 
                        : "Continue"
                      }
                    </span>
                  )}
                </button>
              </form>
            </div>
          )}

          {/* Bottom Actions */}
          <div className="w-full flex flex-col gap-2 pt-2 border-t border-white/5">
            {!showAccountList && accountsList.length > 1 && (
              <button
                onClick={() => {
                  setShowAccountList(true);
                  setAuthError("");
                }}
                className="w-full py-2 bg-transparent hover:bg-slate-900/60 text-slate-450 hover:text-white text-[10px] font-black uppercase tracking-widest rounded-xl transition-premium border border-transparent hover:border-white/5 cursor-pointer"
              >
                Switch Account
              </button>
            )}
            
            {(showAccountList || accountsList.length === 1) && (
              <button
                onClick={() => {
                  setIsLoginMode(true);
                  setShowEmailFields(true);
                  setSetupStep(4);
                }}
                className="w-full py-2 bg-transparent hover:bg-slate-900/60 text-slate-450 hover:text-white text-[10px] font-black uppercase tracking-widest rounded-xl transition-premium border border-transparent hover:border-white/5 cursor-pointer"
              >
                Use Another Account
              </button>
            )}

            <button
              onClick={() => {
                setIsLoginMode(false);
                setShowEmailFields(true);
                setSetupStep(4);
              }}
              className="w-full py-2 bg-transparent hover:bg-slate-900/60 text-slate-450 hover:text-white text-[10px] font-black uppercase tracking-widest rounded-xl transition-premium border border-transparent hover:border-white/5 cursor-pointer"
            >
              Create New Account
            </button>
          </div>

        </div>
      </div>
    );
  }

  // -------------------- STEP 6: MAIN COMPANION INTERFACE --------------------
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-transparent font-sans text-slate-100 relative">
      
      {/* Mobile Sidebar Hamburger Toggle */}
      {!sidebarOpen && (
        <button
          onClick={() => setSidebarOpen(true)}
          className="fixed left-4 top-4 z-50 p-2.5 rounded-xl bg-[#121316] border border-white/5 shadow-md hover:bg-slate-850 text-slate-400 hover:text-white transition-premium cursor-pointer backdrop-blur-md flex items-center justify-center shrink-0"
          title="Expand Sidebar"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      )}

      {/* Sidebar Navigation */}
      {isMobile && sidebarOpen && (
        <button
          className="fixed inset-0 z-30 bg-black/40 backdrop-blur-[1px]"
          onClick={() => setSidebarOpen(false)}
          aria-label="Close sidebar overlay"
        />
      )}
      <div className={`shrink-0 overflow-hidden transition-[width] duration-300 z-40 ${
        isMobile
          ? "fixed left-0 top-0 h-full w-80 max-w-[85vw] shadow-2xl border-r border-white/5"
          : "relative h-full w-80 border-r border-white/5"
      } ${
        sidebarOpen ? "" : "w-0 pointer-events-none"
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
          activeTab={activeTab}
          onChangeTab={handleTabChange}
        />
      </div>

      {/* Main Companion Workspace Viewport */}
      <div className="flex-1 h-full flex flex-col bg-[#121316] relative">
        {activeConversationId ? (
          <ChatInterface
            activeConversationId={activeConversationId}
            onSelectConversation={(id) => {
              setActiveConversationId(id);
              saveSessionState(activeTab, id);
            }}
            apiBaseUrl={API_BASE_URL}
            onRefreshDocuments={handleRefreshSidebar}
            sidebarOpen={sidebarOpen}
            setSidebarOpen={setSidebarOpen}
            token={token}
          />
        ) : (
          <>
            {activeTab === "lifehub" && (
              <div className="flex-1 flex flex-col justify-between overflow-y-auto scroll-smooth-premium bg-[#121316]">
                {/* ABOVE THE FOLD: Breathing Orb & Quick Ask Input */}
                <div className="min-h-[75vh] flex flex-col items-center justify-center text-center p-6 space-y-8 relative overflow-hidden bg-[#121316]">
                  <YaarOrb state="idle" size="lg" className="animate-orb-idle" />

                  <div className="space-y-2 max-w-xl animate-fade-in flex flex-col items-center">
                    <h2 className="text-3xl sm:text-4xl font-black text-white tracking-tight font-display text-gradient-title">
                      {getLoginGreeting()}
                    </h2>
                    
                    <div className="flex items-center gap-1 text-[10px] font-bold text-slate-500 py-1 bg-slate-900/40 px-2.5 border border-white/5 rounded-full">
                      <Languages className="w-3.5 h-3.5 text-slate-500" />
                      <select
                        value={selectedLang}
                        onChange={(e) => {
                          const newLang = e.target.value;
                          handleLanguageChange(newLang);
                        }}
                        className="bg-transparent border-none outline-none text-slate-450 cursor-pointer hover:text-white font-bold"
                      >
                        {LANGUAGES.map(l => (
                          <option key={l.id} value={l.id} className="bg-[#121316] text-white">{l.label}</option>
                        ))}
                      </select>
                    </div>
                    <p className="text-slate-400 text-xs font-semibold leading-normal">
                      {selectedLang === "Hindi" ? "आज हम मिलकर क्या प्रगति करेंगे?" :
                       selectedLang === "Punjabi" ? "ਅੱਜ ਆਪਾਂ ਕਿਸ ਚੀਜ਼ 'ਤੇ ਕੰਮ ਕਰ ਰਹੇ ਹਾਂ?" :
                       selectedLang === "Gujarati" ? "આજે આપણે શેના પર કામ કરવાના છીએ?" :
                       selectedLang === "Tamil" ? "இன்று நாம் என்ன செய்யப் போகிறோம்?" :
                       selectedLang === "Bengali" ? "আজ আমরা কি কাজ করব?" :
                       "What are we working on today?"}
                    </p>
                  </div>

                  {/* Quick Input Box */}
                  <div className="w-full max-w-2xl relative flex items-center bg-slate-900/50 border border-white/5 rounded-2xl px-5 py-4 shadow-2xl focus-within:border-amber-500/40 transition-premium">
                    <input
                      type="text"
                      value={landingInput}
                      onChange={e => setLandingInput(e.target.value)}
                      onKeyDown={e => {
                        if (e.key === "Enter" && landingInput.trim()) {
                          handleNewChatFromLifeHub(landingInput);
                          setLandingInput("");
                        }
                      }}
                      placeholder={selectedLang === "Hindi" ? "यार से कुछ भी पूछें..." :
                                   selectedLang === "Punjabi" ? "ਯਾਰ ਤੋਂ ਕੁਝ ਵੀ ਪੁੱਛੋ..." :
                                   selectedLang === "Gujarati" ? "યાર ને ગમે તે પૂછો..." :
                                   selectedLang === "Tamil" ? "யாரிடம் எதையும் கேளுங்கள்..." :
                                   selectedLang === "Bengali" ? "ইয়ারকে যেকোনো প্রশ্ন করুন..." :
                                   "Ask Yaar anything to get started..."}
                      className="w-full bg-transparent text-white text-xs placeholder-slate-500 outline-none pr-12 font-medium"
                    />
                    <button
                      onClick={() => {
                        if (landingInput.trim()) {
                          handleNewChatFromLifeHub(landingInput);
                          setLandingInput("");
                        }
                      }}
                      className="absolute right-3 p-2 bg-amber-600 hover:bg-amber-500 text-white rounded-xl transition-premium cursor-pointer"
                    >
                      <Send className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* BELOW THE FOLD: Five Sections Dashboard */}
                <div className="border-t border-white/5 pt-1">
                  <LifeHubPanel
                    token={token}
                    apiBaseUrl={API_BASE_URL}
                    onSelectConversation={(id) => {
                      setActiveConversationId(id);
                      saveSessionState(activeTab, id);
                    }}
                    onNewChat={handleNewChatFromLifeHub}
                    onNavigateToSection={handleTabChange}
                  />
                </div>
              </div>
            )}

            {activeTab === "projects" && (
              <ProjectsPanel
                token={token}
                apiBaseUrl={API_BASE_URL}
                onSelectConversation={setActiveConversationId}
              />
            )}
            
            {activeTab === "vault" && (
              <VaultPanel />
            )}

            {activeTab === "settings" && (
              <SettingsPanel
                language={selectedLang}
                setLanguage={setSelectedLang}
                vibe={selectedVibe}
                setVibe={setSelectedVibe}
                userName={userName}
                setUserName={setUserName}
                theme={theme}
                setTheme={setTheme}
                onReset={() => {
                  localStorage.clear();
                  sessionStorage.clear();
                  setToken(null);
                  setSetupStep(0);
                }}
              />
            )}
          </>
        )}
      </div>
      {/* Floating Beta Feedback Widget */}
      {betaTesterMode && (
        <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-2.5">
          <div className="flex flex-row items-center gap-2 bg-[#1c1d22]/90 backdrop-blur-md border border-white/10 p-2 rounded-full shadow-2xl animate-slide-in-right">
            <button
              onClick={() => handleOpenFeedbackDialog("issue")}
              className="px-3.5 py-2.5 rounded-full hover:bg-slate-800 text-xs font-black uppercase tracking-wider text-rose-455 hover:text-white transition-premium cursor-pointer flex items-center gap-1.5"
              title="Report Bug / Issue"
            >
              <span>🐞</span> <span className="hidden sm:inline">Report Issue</span>
            </button>
            <div className="w-[1px] h-4 bg-white/10" />
            <button
              onClick={() => handleOpenFeedbackDialog("improvement")}
              className="px-3.5 py-2.5 rounded-full hover:bg-slate-800 text-xs font-black uppercase tracking-wider text-amber-500 hover:text-white transition-premium cursor-pointer flex items-center gap-1.5"
              title="Suggest Improvement"
            >
              <span>✨</span> <span className="hidden sm:inline">Suggest Improvement</span>
            </button>
            <div className="w-[1px] h-4 bg-white/10" />
            <button
              onClick={() => handleOpenFeedbackDialog("loved")}
              className="px-3.5 py-2.5 rounded-full hover:bg-slate-800 text-xs font-black uppercase tracking-wider text-emerald-450 hover:text-white transition-premium cursor-pointer flex items-center gap-1.5"
              title="Loved This Feature"
            >
              <span>❤️</span> <span className="hidden sm:inline">Loved This</span>
            </button>
          </div>
        </div>
      )}

      {/* Feedback Dialog Modal */}
      {feedbackType && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 animate-fade-in">
          <div className="w-full max-w-md p-6 rounded-3xl bg-[#121316] border border-white/5 shadow-2xl flex flex-col gap-4">
            <div className="flex items-center justify-between border-b border-white/5 pb-3">
              <h3 className="text-sm font-black uppercase tracking-wider text-white">
                {feedbackType === "issue" ? "🐞 Report Issue" :
                 feedbackType === "improvement" ? "✨ Suggest Improvement" : "❤️ Loved This"}
              </h3>
              <button
                onClick={() => setFeedbackType(null)}
                className="text-slate-500 hover:text-white transition-colors"
              >
                <X className="w-4.5 h-4.5" />
              </button>
            </div>
            <form onSubmit={handleSubmitFeedback} className="flex flex-col gap-4">
              <textarea
                required
                autoFocus
                value={feedbackText}
                onChange={(e) => setFeedbackText(e.target.value)}
                placeholder={
                  feedbackType === "issue" ? "Describe the issue or bug you encountered..." :
                  feedbackType === "improvement" ? "What feature or polish would make YAAR better?" :
                  "What did you love about this feature?"
                }
                className="w-full p-4 rounded-2xl bg-[#1c1d22] border border-white/5 text-xs text-white placeholder-slate-555 outline-none focus:border-amber-500 transition-premium min-h-[90px] resize-none font-medium leading-relaxed"
              />

              <textarea
                value={expectedBehavior}
                onChange={(e) => setExpectedBehavior(e.target.value)}
                placeholder="What did you expect to happen? (Expected Behavior)"
                className="w-full p-4 rounded-2xl bg-[#1c1d22] border border-white/5 text-xs text-white placeholder-slate-555 outline-none focus:border-amber-500 transition-premium min-h-[70px] resize-none font-medium leading-relaxed"
              />
              
              <div className="flex gap-2 justify-end">
                <button
                  type="button"
                  onClick={() => setFeedbackType(null)}
                  className="px-4 py-2 border border-slate-800 text-slate-450 hover:text-white rounded-xl text-xs font-bold transition-colors cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-amber-600 hover:bg-amber-500 text-white rounded-xl text-xs font-black uppercase tracking-wider transition-premium cursor-pointer shadow-md"
                >
                  Submit Report
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Feedback Success Toast */}
      {feedbackSuccessToast && (
        <div className="fixed bottom-24 right-6 z-50 p-4 rounded-2xl bg-emerald-950/90 border border-emerald-500/30 text-emerald-450 text-xs font-black uppercase tracking-wider shadow-2xl animate-slide-in-right flex items-center gap-2">
          <Check className="w-4 h-4" /> Feedback saved to sovereign logs!
        </div>
      )}

      {/* Ctrl+K Cmd+K Command Menu Bar */}
      <CommandBar
        isOpen={isCommandBarOpen}
        onClose={() => setIsCommandBarOpen(false)}
        onSelectAction={handleSelectCommandAction}
      />

    </div>
  );
}
