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
}

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
  onChangeTab
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
  }, [logoClicks]);

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
        },
        Telugu: {
          lifeHub: "లైఫ్ హబ్",
          projects: "ప్రాజెక్ట్‌లు",
          vault: "ది వాల్ట్",
          settings: "సెట్టింగ్‌లు",
          newChat: "కొత్త చాట్",
          recentChats: "ఇటీవలి చాట్‌లు",
          welcomeBack: "స్వాగతం 👋",
          workingOn: "మీరు పని చేస్తున్నది:",
          continueBinder: "ప్రాజెక్ట్ తెరవండి",
          noChats: "యాక్టివ్ చాట్‌లు లేవు. పైన కొత్తది ప్రారంభించండి!",
          logOut: "లాగ్ అవుట్"
        },
        Marathi: {
          lifeHub: "लाइफ हब",
          projects: "प्रकल्प",
          vault: "द वॉल्ट",
          settings: "सेटिंग्ज",
          newChat: "नवीन चॅट",
          recentChats: "अलीकडील चॅट्स",
          welcomeBack: "सुस्वागतम 👋",
          workingOn: "तुम्ही काम करत होता:",
          continueBinder: "प्रकल्प सुरू ठेवा",
          noChats: "कोणतेही सक्रिय चॅट नाही. वर सुरू करा!",
          logOut: "लॉग आउट"
        },
        Urdu: {
          lifeHub: "لائف ہب",
          projects: "پروجیکٹس",
          vault: "دی والٹ",
          settings: "ترتیبات",
          newChat: "نیا چیٹ",
          recentChats: "حالیہ چیٹس",
          welcomeBack: "خوش آمدید 👋",
          workingOn: "آپ کام کر رہے تھے:",
          continueBinder: "پروجیکٹ کھولیں",
          noChats: "کوئی فعال چیٹ نہیں ہے۔ اوپر شروع کریں!",
          logOut: "لاگ آؤٹ"
        },
        Kannada: {
          lifeHub: "ಲೈಫ್ ಹಬ್",
          projects: "ಯೋಜನೆಗಳು",
          vault: "ದಿ ವಾಲ್ಟ್",
          settings: "ಸೆಟ್ಟಿಂಗ್‌ಗಳು",
          newChat: "ಹೊಸ ಚಾಟ್",
          recentChats: "ಇತ್ತೀಚಿನ ಚಾಟ್‌ಗಳು",
          welcomeBack: "ಸ್ವಾಗತ 👋",
          workingOn: "ನೀವು ಕೆಲಸ ಮಾಡುತ್ತಿದ್ದದ್ದು:",
          continueBinder: "ಯೋಜನೆ ತೆರೆಯಿರಿ",
          noChats: "ಯಾವುದೇ ಸಕ್ರಿಯ ಚಾಟ್ ಇಲ್ಲ. ಹೊಸದನ್ನು ಪ್ರಾರಂಭಿಸಿ!",
          logOut: "ಲಾಗ್ ಔಟ್"
        },
        Malayalam: {
          lifeHub: "ലൈഫ് ഹബ്",
          projects: "പ്രോജക്റ്റുകൾ",
          vault: "ദി വോൾട്ട്",
          settings: "ക്രമീകരണങ്ങൾ",
          newChat: "പുതിയ ചാറ്റ്",
          recentChats: "സമീപകാല ചാറ്റുകൾ",
          welcomeBack: "സ്വാഗതം 👋",
          workingOn: "നിങ്ങൾ ജോലി ചെയ്യുകയായിരുന്നു:",
          continueBinder: "പ്രോജക്റ്റ് തുറക്കുക",
          noChats: "സജീവ ചാറ്റുകൾ ഒന്നുമില്ല. മുകളിൽ ആരംഭിക്കുക!",
          logOut: "ലോഗ് ഔട്ട്"
        },
        Odia: {
          lifeHub: "ଲାଇଫ୍ ହବ୍",
          projects: "ପ୍ରକଳ୍ପଗୁଡିକ",
          vault: "ଦି ଭଲ୍ଟ",
          settings: "ସେଟିଂସଙ୍ଗ",
          newChat: "ନୂତന ଚାଟ୍",
          recentChats: "ସାମ୍ପ୍ରତିକ ଚାଟ୍",
          welcomeBack: "ସ୍ୱାଗତମ 👋",
          workingOn: "ଆପଣ କାମ କରୁଥିଲେ:",
          continueBinder: "ପ୍ରକଳ୍ପ ଆରମ୍ଭ କରନ୍ତು",
          noChats: "କୌଣସି ସକ୍ରିୟ ଚାଟ୍ ନାହିଁ। ନୂଆ ଆରମ୍ଭ କରନ୍ତୁ!",
          logOut: "ଲଗ୍ ଆଉଟ୍"
        },
        Assamese: {
          lifeHub: "লাইফ হাব",
          projects: "প্ৰকল্পসমূহ",
          vault: "দ্যা ভল্ট",
          settings: "ছেটিংছ",
          newChat: "নতুন চ্যাট",
          recentChats: "সাম্প্রতিক চ্যাটসমূহ",
          welcomeBack: "স্বাগতম 👋",
          workingOn: "আপুনি কাম কৰি আছিল:",
          continueBinder: "প্ৰকল্প খোলক",
          noChats: "কোনো সক্ৰিয় চ্যাট নাই। নতুন চ্যাট কৰক!",
          logOut: "লগ আউট"
        },
        Maithili: {
          lifeHub: "लाइफ हब",
          projects: "परियोजना सभ",
          vault: "द वॉल्ट",
          settings: "सेटिंग्स",
          newChat: "नब गपशप",
          recentChats: "हालक गपशप",
          welcomeBack: "स्वागत अछि 👋",
          workingOn: "अहाँ काज कऽ रहल छलाह:",
          continueBinder: "परियोजना चालू करू",
          noChats: "कोनो सक्रिय चैट नै। नव शुरू करू!",
          logOut: "लॉग आउट"
        },
        Santali: {
          lifeHub: "ᱞᱟᱭᱤᱯᱷ ᱦᱟᱹᱵᱽ",
          projects: "ᱯᱚᱨᱛᱚᱱ ᱠᱚ",
          vault: "ᱫᱤ ᱵᱷᱚᱞᱴ",
          settings: "ᱥᱮᱴᱤᱝ ᱠᱚ",
          newChat: "ᱱᱟᱶᱟ ᱨᱚᱯᱚᱲ",
          recentChats: "ᱱᱤᱛᱚᱜᱟᱜ ᱨᱚᱯᱚᱲ",
          welcomeBack: "ᱥᱟᱹᱜᱩᱱ ᱫᱟᱨᱟᱢ 👋",
          workingOn: "ᱟᱢᱮᱢ ᱠᱟᱹᱢᱤ ᱠាន ᱛᱟᱦᱮᱸᱫ:",
          continueBinder: "ᱯᱚᱨᱛᱚᱱ ᱮᱦᱚᱵᱽ ᱢᱮ",
          noChats: "ᱡᱟᱦᱟᱸᱱ ᱨᱚᱯᱚᱲ ᱵᱟᱹᱱᱩᱜᱼᱟ᱾ ᱱᱟᱶᱟ ᱮᱦᱚᱵᱽ ᱢᱮ!",
          logOut: "ᱵᱟᱜᱤᱭᱟᱜ ᱢᱮ"
        },
        Kashmiri: {
          lifeHub: "لائف ہب",
          projects: "پروجیکٹ",
          vault: "دی والٹ",
          settings: "سیٹنگز",
          newChat: "نئہ چیٹ",
          recentChats: "حالیہ چیٹ",
          welcomeBack: "خوش آمدید 👋",
          workingOn: "تہہ اوسیو کام کران:",
          continueBinder: "پروجیکٹ کھولیو",
          noChats: "کانہہ سرگرم چیٹ چھنہ۔ نئہ شروع کریو!",
          logOut: "لاگ آؤٹ"
        },
        Nepali: {
          lifeHub: "लाइफ हब",
          projects: "परियोजनाहरू",
          vault: "द वॉल्ट",
          settings: "सेटिङहरू",
          newChat: "नयाँ च्याट",
          recentChats: "हालैका च्याटहरू",
          welcomeBack: "स्वागत छ 👋",
          workingOn: "तपाईं काम गर्दै हुनुहुन्थ्यो:",
          continueBinder: "परियोजना खोल्नुहोस्",
          noChats: "कुनै च्याट छैन। नयाँ सुरु गर्नुहोस्!",
          logOut: "लोग आउट"
        },
        Konkani: {
          lifeHub: "लाइफ हब",
          projects: "प्रकल्प",
          vault: "द वॉल्ट",
          settings: "सेटिंग्स",
          newChat: "नवी चेट",
          recentChats: "हालीच्यो चेट्यो",
          welcomeBack: "येवकार 👋",
          workingOn: "तुमी काम करताले:",
          continueBinder: "प्रकल्प चालू दवरात्",
          noChats: "कसलीच चेट चालू ना। नवी सुरू करात!",
          logOut: "भायर वचात"
        },
        Sindhi: {
          lifeHub: "لائف هب",
          projects: "پروجيڪٽ",
          vault: "دي والٽ",
          settings: "سيٽنگون",
          newChat: "نئين ڪچهري",
          recentChats: "تازيون ڪچهريون",
          welcomeBack: "ڀلي ڪري آيا 👋",
          workingOn: "توهان ڪم ڪري رهيا هئا:",
          continueBinder: "پروجيڪٽ کوليو",
          noChats: "ڪا به ڪچهري چالو ناهي. نئين شروع ڪريو!",
          logOut: "لاگ آئوٽ"
        },
        Dogri: {
          lifeHub: "लाइफ हब",
          projects: "प्रोजेक्ट",
          vault: "द वॉल्ट",
          settings: "सेटिंग",
          newChat: "नमां चैट",
          recentChats: "हालै दे चैट",
          welcomeBack: "स्वागत ऐ 👋",
          workingOn: "तुस कम्म करा करदे हे:",
          continueBinder: "प्रोजेक्ट खोलो",
          noChats: "कोई चैट चालू नमां ऐ। नमां शुरू करो!",
          logOut: "लॉग आउट"
        },
        Manipuri: {
          lifeHub: "লাইফ হব",
          projects: "প্রোজেক্টশিং",
          vault: "ভল্ট",
          settings: "সেটিংস",
          newChat: "অনৌবা চ্যাট",
          recentChats: "হৌজিক্কী চ্যাটশিং",
          welcomeBack: "তরাম্না ওকচরি 👋",
          workingOn: "নহাক থবক তৌরিঙৈ:",
          continueBinder: "প্রোজেক্ট হাংবীয়ু",
          noChats: "চ্যাট অমত্তা লৈতে। অনৌবা অমত্তা হৌবীয়ু!",
          logOut: "লগ আউত"
        },
        Bodo: {
          lifeHub: "लाइफ हब",
          projects: "प्रोजेक्टफोर",
          vault: "द वॉल्ट",
          settings: "सेटिंगफोर",
          newChat: "गोदान चैट",
          recentChats: "थांनाय चैटफोर",
          welcomeBack: "बरायबाय 👋",
          workingOn: "नों काम खालामगासिनो दंमोन:",
          continueBinder: "प्रेक्ट खेव",
          noChats: "जेबो चैट गैया। गोदान जागाय!",
          logOut: "लोग आउट खालाम"
        },
        Sanskrit: {
          lifeHub: "जीवनकेन्द्रम्",
          projects: "प्रकल्पाः",
          vault: "सुरक्षितकोशः",
          settings: "व्यवस्थापनानि",
          newChat: "नवीनवार्तालापः",
          recentChats: "सद्यःकालीनवार्तालापाः",
          welcomeBack: "स्वागतम् 👋",
          workingOn: "भवान् कार्यं कुर्वन् आसीत्:",
          continueBinder: "प्रकल्पम् उद्घाटयतु",
          noChats: "कोऽपि सक्रियवार्तालापः नास्ति। नवीनं आरभत!",
          logOut: "बहिर्गमनम्"
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
      <div 
        onClick={handleLogoClick}
        className="p-5 border-b border-white/5 flex items-center justify-between cursor-pointer select-none"
      >
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

      </div>

    </aside>
  );
}
