"use client";

import React, { useState } from "react";
import { 
  GraduationCap, Briefcase, Rocket, BookOpen, Compass, 
  MessageCircle, Heart, User, Check
} from "lucide-react";

interface OnboardingWizardProps {
  language: string;
  onComplete: (focus: string, vibe: string) => void;
}

const LOCALIZED_WIZARD: Record<string, {
  titleVibe: string;
  descVibe: string;
  titleFocus: string;
  descFocus: string;
  back: string;
  next: string;
  finish: string;
  stepIndicator: string;
  stepOf: string;
  vibes: Array<{ id: string; label: string; desc: string }>;
  focuses: Array<{ id: string; label: string; desc: string }>;
}> = {
  English: {
    titleVibe: "Select Companion Vibe",
    descVibe: "How should YAAR talk to you? Select a tone that matches your personal preference.",
    titleFocus: "What are we focusing on?",
    descFocus: "Select your primary area of focus. YAAR will customize suggestions to match.",
    back: "Back",
    next: "Continue",
    finish: "Start Journey",
    stepIndicator: "YAAR Setup",
    stepOf: "Step",
    vibes: [
      { id: "friendly", label: "Friendly / Dostana", desc: "Conversational, casual, talks like a true 'Yaar'" },
      { id: "formal", label: "Formal / Adabi", desc: "Respectful, polite, structured, using respectful honorifics" },
      { id: "regional", label: "Regional / Desi Touch", desc: "Deeply connected to local cultural phrases, idioms, and dialects" }
    ],
    focuses: [
      { id: "learning", label: "Learning & Education", desc: "For students, UPSC preps, skill acquisition, and translations." },
      { id: "work", label: "Work & Career", desc: "For drafts, reports, metrics analysis, and professional emails." },
      { id: "building", label: "Building & Creation", desc: "For startup blueprints, founder advice, marketing, and coding." },
      { id: "exploring", label: "Exploring & Curiosity", desc: "For science discoveries, local history, and deep philosophical queries." },
      { id: "everyday", label: "Everyday Assistance", desc: "For family advice, local recipes, daily plans, and casual conversations." }
    ]
  },
  Hindi: {
    titleVibe: "यार का स्वभाव चुनें",
    descVibe: "यार को आपसे किस तरह बात करनी चाहिए? वह शैली चुनें जो आपको पसंद हो।",
    titleFocus: "हमारा मुख्य ध्यान किस पर है?",
    descFocus: "अपना प्राथमिक क्षेत्र चुनें। यार आपके अनुसार अपने सुझावों को ढालेगा।",
    back: "पीछे",
    next: "आगे बढ़ें",
    finish: "यात्रा शुरू करें",
    stepIndicator: "यार सेटअप",
    stepOf: "चरण",
    vibes: [
      { id: "friendly", label: "दोस्ताना / दोस्ताना", desc: "अनौपचारिक, बातचीत का सहज अंदाज़, जैसे सच्चा 'यार'" },
      { id: "formal", label: "औपचारिक / अदबी", desc: "आदरपूर्ण, सभ्य, स्पष्ट और सम्मानजनक लहजा" },
      { id: "regional", label: "क्षेत्रीय / देसी टच", desc: "स्थानीय बोलियों, मुहावरों और सांस्कृतिक शब्दों से भरपूर" }
    ],
    focuses: [
      { id: "learning", label: "शिक्षा और सीखना", desc: "छात्रों, परीक्षा की तैयारी, नई कौशल प्राप्ति और अनुवाद के लिए।" },
      { id: "work", label: "काम और करियर", desc: "पेशेवर ईमेल, ड्राफ्ट रिपोर्ट, व्यावसायिक आंकड़े और प्रस्तुतियों के लिए।" },
      { id: "building", label: "निर्माण और स्टार्टअप", desc: "स्टार्टअप ब्लूप्रिंट, संस्थापकों के लिए सलाह, विपणन और कोडिंग।" },
      { id: "exploring", label: "अन्वेषण और जिज्ञासा", desc: "विज्ञान की खोजों, इतिहास, और गहरी दार्शनिक चर्चाओं के लिए।" },
      { id: "everyday", label: "दैनिक जीवन सहायता", desc: "पारिवारिक सलाह, व्यंजनों, घरेलू योजनाओं और सहज बातचीत के लिए।" }
    ]
  },
  Punjabi: {
    titleVibe: "ਯਾਰ ਦਾ ਸੁਭਾਅ ਚੁਣੋ",
    descVibe: "ਯਾਰ ਨੂੰ ਤੁਹਾਡੇ ਨਾਲ ਕਿਸ ਤਰ੍ਹਾਂ ਗੱਲ ਕਰਨੀ ਚਾਹੀਦੀ ਹੈ? ਉਹ ਸ਼ੈਲੀ ਚੁਣੋ ਜੋ ਤੁਹਾਨੂੰ ਚੰਗੀ ਲੱਗੇ।",
    titleFocus: "ਸਾਡਾ ਮੁੱਖ ਧਿਆਨ ਕਿਸ ਚੀਜ਼ 'ਤੇ ਹੈ?",
    descFocus: "ਆਪਣਾ ਮੁੱਖ ਖੇਤਰ ਚੁਣੋ। ਯਾਰ ਤੁਹਾਡੇ ਕੰਮਾਂ ਅਨੁਸਾਰ ਸੁਝਾਅ ਤਿਆਰ ਕਰੇਗਾ।",
    back: "ਪਿੱਛੇ",
    next: "ਅੱਗੇ ਵਧੋ",
    finish: "ਸਫ਼ਰ ਸ਼ੁਰੂ ਕਰੋ",
    stepIndicator: "ਯਾਰ ਸੈੱਟਅੱਪ",
    stepOf: "ਕਦਮ",
    vibes: [
      { id: "friendly", label: "ਦੋਸਤਾਨਾ / ਯਾਰਾਨਾ", desc: "ਆਮ ਗੱਲਬਾਤ, ਬੇਫਿਕਰ ਅੰਦਾਜ਼, ਜਿਵੇਂ ਕੋਈ ਪੱਕਾ 'ਯਾਰ' ਹੋਵੇ" },
      { id: "formal", label: "ਰਸਮੀ / ਅਦਬੀ", desc: "ਸਤਿਕਾਰਯੋਗ, ਨਿਮਰਤਾ ਭਰਿਆ, ਸਪਸ਼ਟ ਅਤੇ ਢੁਕਵਾਂ ਅੰਦਾਜ਼" },
      { id: "regional", label: "ਖੇਤਰੀ / ਦੇਸੀ ਟੱਚ", desc: "ਸਾਡੇ ਸੱਭਿਆਚਾਰਕ ਮੁਹਾਵਰਿਆਂ, ਬੋਲੀਆਂ ਅਤੇ ਦੇਸੀ ਲਹਿਜੇ ਨਾਲ ਭਰਪੂਰ" }
    ],
    focuses: [
      { id: "learning", label: "ਸਿੱਖਿਆ ਅਤੇ ਪੜ੍ਹਾਈ", desc: "ਵਿਦਿਆਰਥੀਆਂ, UPSC ਤਿਆਰੀ, ਨਵੇਂ ਹੁਨਰ ਸਿੱਖਣ ਅਤੇ ਅਨੁਵਾਦ ਲਈ।" },
      { id: "work", label: "ਕੰਮ ਅਤੇ ਕਰੀਅਰ", desc: "ਪੇਸ਼ੇਵਰ ਈਮੇਲ, ਡਰਾਫਟ ਰਿਪੋਰਟਾਂ, ਕੰਮ ਦੀਆਂ ਫਾਈਲਾਂ ਅਤੇ ਯੋਜਨਾਵਾਂ ਲਈ।" },
      { id: "building", label: "ਨਿਰਮਾਣ ਅਤੇ ਸਟਾਰਟਅੱਪ", desc: "ਸਟਾਰਟਅੱਪ ਯੋਜਨਾਵਾਂ, ਕਾਰੋਬਾਰੀ ਸੁਝਾਅ, ਮਾਰਕੀਟਿੰਗ ਅਤੇ ਕੋਡਿੰਗ ਲਈ।" },
      { id: "exploring", label: "ਖੋਜ ਅਤੇ ਦਿਲਚਸਪੀ", desc: "ਵਿਗਿਆਨਕ ਲੱਭਤਾਂ, ਇਤਿਹਾਸ ਅਤੇ ਦਾਰਸ਼ਨਿਕ ਚਰਚਾਵਾਂ ਬਾਰੇ ਜਾਨਣ ਲਈ।" },
      { id: "everyday", label: "ਰੋਜ਼ਾਨਾ ਜੀਵਨ ਸਹਾਇਤਾ", desc: "ਪਰਿਵਾਰਕ ਸਲਾਹ, ਦੇਸੀ ਰਸੋਈ ਰੈਸਿਪੀ, ਰੋਜ਼ਾਨਾ ਯੋਜਨਾਵਾਂ ਅਤੇ ਗੱਲਬਾਤ ਲਈ।" }
    ]
  },
  Gujarati: {
    titleVibe: "યારનો સ્વભાવ પસંદ કરો",
    descVibe: "યાર આપની સાથે કઈ રીતે વાત કરે? આપની પસંદગી મુજબનો લહેજો પસંદ કરો.",
    titleFocus: "આપણું મુખ્ય ધ્યાન શેના પર છે?",
    descFocus: "આપનું મુખ્ય ક્ષેત્ર પસંદ કરો. યાર આપના કાર્યો મુજબ જ સૂચનો તૈયાર કરશે.",
    back: "પાછા",
    next: "આગળ વધો",
    finish: "યાત્રા શરૂ કરો",
    stepIndicator: "યાર સેટઅપ",
    stepOf: "પગલું",
    vibes: [
      { id: "friendly", label: "દોસ્તાના / મિત્રતાપૂર્ણ", desc: "સરળ વાતચીત, અનૌપચારિક શૈલી, જેમ સાચો 'યાર' વાત કરતો હોય" },
      { id: "formal", label: "ઔપચારિક / સભ્ય", desc: "આદરપૂર્વક, નમ્ર, વ્યવસ્થિત અને શિષ્ટાચાર સભર વાતચીત" },
      { id: "regional", label: "પ્રાદેશિક / દેશી ટચ", desc: "સ્થાનિક ભાષાના રૂઢિપ્રયોગો, કહેવતો અને લોકબોલીથી સભર" }
    ],
    focuses: [
      { id: "learning", label: "શિક્ષણ અને શિક્ષણ", desc: "વિદ્યાર્થીઓ, સ્પર્ધાત્મક પરીક્ષાઓની તૈયારી, નવું શીખવા અને અનુવાદ માટે." },
      { id: "work", label: "કામ અને કારકિર્દી", desc: "વ્યવસાયિક ઇમેઇલ્સ, અહેવાલોનો મુસદ્દો અને ઓફિસ કાર્યો માટે." },
      { id: "building", label: "નિર્માણ અને સ્ટાર્ટઅપ", desc: "સ્ટાર્ટઅપ બ્લુપ્રિન્ટ્સ, સ્થાપકો માટે માર્ગદર્શન અને કોડિંગ માટે." },
      { id: "exploring", label: "અન્વેષણ અને જિજ્ઞાસા", desc: "વૈજ્ઞાનિક શોધો, સ્થાનિક ઇતિહાસ અને ગહન દાર્શનિક પ્રશ્નો માટે." },
      { id: "everyday", label: "રોજિંદી સહાયતા", desc: "કૌટુંબિક સલાહ, સ્થાનિક વાનગીઓ, દૈનિક આયોજન અને સામાન્ય વાતચીત માટે." }
    ]
  },
  Bengali: {
    titleVibe: "ইয়ারের স্বভাব নির্বাচন করুন",
    descVibe: "আপনার সাথে ইয়ার কিভাবে কথা বলবে? আপনার পছন্দসই একটি ভঙ্গি বেছে নিন।",
    titleFocus: "আমরা প্রধানত কি নিয়ে কাজ করবো?",
    descFocus: "আপনার কাজের মূল ক্ষেত্রটি বেছে নিন। ইয়ার সেই অনুযায়ী পরামর্শ তৈরি করবে।",
    back: "পিছনে",
    next: "এগিয়ে চলুন",
    finish: "যাত্রা শুরু করুন",
    stepIndicator: "ইয়ার সেটআপ",
    stepOf: "ধাপ",
    vibes: [
      { id: "friendly", label: "বন্ধুসুলভ / দোস্তানা", desc: "সহজ আলাপচারিতা, ঘরোয়া মেজাজ, একদম খাঁটি বন্ধুর মতন" },
      { id: "formal", label: "আনুষ্ঠানিক / আদবী", desc: "শ্রদ্ধাশীল, ভদ্র, মার্জিত ও সম্মানজনক ভাষা প্রয়োগ" },
      { id: "regional", label: "আঞ্চলিক / দেশি ছোঁয়া", desc: "স্থানীয় কথ্য রূপ, প্রবাদ-প্রবচন এবং খাঁটি মাটির ভাষার টান" }
    ],
    focuses: [
      { id: "learning", label: "শিক্ষা ও পঠন-পাঠন", desc: "ছাত্রছাত্রীদের পড়াশোনা, প্রতিযোগিতামূলক পরীক্ষা ও অনুবাদের জন্য।" },
      { id: "work", label: "কর্মক্ষেত্র ও পেশা", desc: "অফিসের মেল লেখা, ড্রাফটিং রিপোর্ট এবং পেশাদার নথিপত্র তৈরির জন্য।" },
      { id: "building", label: "সৃষ্টি ও স্টার্টআপ", desc: "নতুন স্টার্টআপ পরিকল্পনা, মার্কেটিং স্ট্র্যাটেজি এবং কোডিং সহায়তার জন্য।" },
      { id: "exploring", label: "অনুসন্ধান ও কৌতূহল", desc: "বিজ্ঞান, ইতিহাস এবং বিভিন্ন দ্শনশাস্ত্রের গভীর খোঁজের জন্য।" },
      { id: "everyday", label: "দৈনন্দিন জীবনের কাজ", desc: "পারিবারিক পরামর্শ, রান্নার রেসিপি, দিনের পরিকল্পনা ও সাধারণ আড্ডার জন্য।" }
    ]
  },
  Tamil: {
    titleVibe: "யாருடைய குணத்தைத் தேர்ந்தெடுக்கவும்",
    descVibe: "யார் உங்களிடம் எப்படிப் பேச வேண்டும்? உங்கள் விருப்பத்திற்கேற்ற தொனியைத் தேர்ந்தெடுக்கவும்.",
    titleFocus: "நாம் எதில் கவனம் செலுத்தப் போகிறோம்?",
    descFocus: "உங்கள் முக்கியப் பணித் துறையைத் தேர்ந்தெடுக்கவும். யார் அதற்கேற்றவாறு பரிந்துரைகளை வழங்கும்.",
    back: "பின்னால்",
    next: "தொடரவும்",
    finish: "பயணத்தைத் தொடங்கு",
    stepIndicator: "யார் அமைவு",
    stepOf: "படி",
    vibes: [
      { id: "friendly", label: "நண்பன் / தோழமை", desc: "இயல்பான உரையாடல், ஒரு நெருங்கிய நண்பனைப் போலப் பேசுவது" },
      { id: "formal", label: "முறையான / மரியாதைக்குரிய", desc: "மதிப்புடன், பணிவுடன், ஒழுங்கமைக்கப்பட்ட உரையாடல்" },
      { id: "regional", label: "வட்டார வழக்கு / தேசி டச்", desc: "உள்ளூர் பழமொழிகள், வட்டார மொழி வழக்கு மற்றும் பழக்கவழக்கங்களுடன்" }
    ],
    focuses: [
      { id: "learning", label: "கல்வி & கற்றல்", desc: "மாணவர்கள், போட்டித் தேர்வு தயாரிப்பு மற்றும் மொழிபெயர்ப்புகளுக்கு." },
      { id: "work", label: "வேலை & தொழில்", desc: "அலுவலக மின்னஞ்சல்கள், அறிக்கைகள் மற்றும் தொழில்முறை திட்டங்களுக்கு." },
      { id: "building", label: "தொழில்முனைவு & உருவாக்கம்", desc: "தொழில் தொடங்குதல், நிறுவனர்களுக்கான ஆலோசனைகள் மற்றும் கோடிங் உதவிக்கு." },
      { id: "exploring", label: "ஆராய்ச்சி & ஆர்வம்", desc: "அறிவியல் கண்டுபிடிப்புகள், உள்ளூர் வரலாறு மற்றும் தத்துவக் கேள்விகளுக்கு." },
      { id: "everyday", label: "தினசரி உதவிகள்", desc: "குடும்ப ஆலோசனைகள், உள்ளூர் சமையல் குறிப்புகள் மற்றும் தினசரி உரையாடல்களுக்கு." }
    ]
  }
};

export default function OnboardingWizard({ language, onComplete }: OnboardingWizardProps) {
  const [wizardStep, setWizardStep] = useState(1);
  const [personality, setPersonality] = useState("friendly");
  const [focus, setFocus] = useState("everyday");

  const langKey = LOCALIZED_WIZARD[language] ? language : "English";
  const texts = LOCALIZED_WIZARD[langKey];

  const LANGUAGE_REGIONS: Record<string, string> = {
    Hindi: "North India", Punjabi: "Punjab", Gujarati: "Gujarat", Bengali: "Bengal / Bangladesh",
    Tamil: "Tamil Nadu", Telugu: "Andhra / Telangana", Marathi: "Maharashtra", Kannada: "Karnataka",
    Malayalam: "Kerala", Odia: "Odisha", Assamese: "Assam", Urdu: "Urdu Belt / Hyderabad",
    Sanskrit: "All India", English: "All India"
  };

  const handleNext = () => {
    if (wizardStep === 1) {
      setWizardStep(2);
    } else {
      localStorage.setItem("yaar_personality", personality);
      localStorage.setItem("yaar_onboarding_interest", focus);

      // Store full Companion Profile
      const companionProfile = {
        tone: personality,
        focus,
        language,
        region: LANGUAGE_REGIONS[language] || "India",
        interests: [focus],
        recentWork: [],
        createdAt: new Date().toISOString()
      };
      localStorage.setItem("yaar_companion_profile", JSON.stringify(companionProfile));

      // Also update the active user record
      const activeUserStr = localStorage.getItem("yaar_active_user");
      if (activeUserStr) {
        try {
          const activeUser = JSON.parse(activeUserStr);
          activeUser.companionProfile = companionProfile;
          localStorage.setItem("yaar_active_user", JSON.stringify(activeUser));
        } catch (_) {}
      }

      onComplete(focus, personality);
    }
  };

  const getVibeIcon = (id: string) => {
    switch (id) {
      case "friendly": return Heart;
      case "formal": return User;
      default: return MessageCircle;
    }
  };

  const getFocusIcon = (id: string) => {
    switch (id) {
      case "learning": return GraduationCap;
      case "work": return Briefcase;
      case "building": return Rocket;
      case "exploring": return BookOpen;
      default: return Compass;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#06070d]/90 backdrop-blur-xl p-4 select-none">
      <div className="w-full max-w-2xl p-6 sm:p-10 rounded-3xl bg-[#121316] border border-white/5 shadow-2xl flex flex-col gap-6 animate-slide-in-right relative">
        
        {/* Header bar */}
        <div className="flex items-center justify-between border-b border-white/5 pb-4">
          <div className="flex items-center gap-2">
            <span className="text-[10px] uppercase font-black tracking-widest text-slate-500">{texts.stepIndicator}</span>
            <span className="text-slate-700 font-bold">•</span>
            <span className="text-[10px] uppercase font-black tracking-widest text-amber-500">{texts.stepOf} {wizardStep} of 2</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full transition-all duration-300 ${wizardStep >= 1 ? "bg-amber-500" : "bg-slate-700"}`} />
            <span className={`w-2 h-2 rounded-full transition-all duration-300 ${wizardStep >= 2 ? "bg-amber-500" : "bg-slate-700"}`} />
          </div>
        </div>

        {/* STEP 1: PERSONALITY/VIBE */}
        {wizardStep === 1 && (
          <div className="space-y-5 animate-fade-in">
            <div className="text-center space-y-2">
              <div className="w-12 h-12 rounded-2xl bg-amber-950/20 border border-amber-900/30 text-amber-500 flex items-center justify-center mx-auto">
                <Heart className="w-6 h-6 animate-pulse" />
              </div>
              <h2 className="text-2xl sm:text-3xl font-black text-white tracking-tight font-display">
                {texts.titleVibe}
              </h2>
              <p className="text-slate-450 text-xs font-semibold max-w-md mx-auto leading-relaxed">
                {texts.descVibe}
              </p>
            </div>

            <div className="flex flex-col gap-3">
              {texts.vibes.map((v) => {
                const Icon = getVibeIcon(v.id);
                const isSelected = personality === v.id;
                return (
                  <button
                    key={v.id}
                    type="button"
                    onClick={() => setPersonality(v.id)}
                    className={`p-4 rounded-2xl border text-left flex items-start gap-4 transition-premium cursor-pointer group ${
                      isSelected
                        ? "bg-amber-950/20 border-amber-500 shadow-md shadow-amber-500/5"
                        : "bg-slate-900/10 border-white/5 hover:bg-slate-800/20"
                    }`}
                  >
                    <div className={`p-2.5 rounded-xl border shrink-0 transition-premium ${
                      isSelected ? "text-amber-500 bg-amber-950/40 border-amber-900/30" : "text-slate-500 bg-slate-800/30 border-white/5"
                    }`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <h4 className={`text-sm font-black transition-colors ${isSelected ? "text-amber-500" : "text-slate-200 group-hover:text-white"}`}>
                        {v.label}
                      </h4>
                      <p className="text-[11px] text-slate-400 font-medium leading-normal mt-0.5">
                        {v.desc}
                      </p>
                    </div>
                    <div className="flex items-center justify-center shrink-0 self-center">
                      <div className={`w-5 h-5 rounded-full border flex items-center justify-center ${isSelected ? "border-amber-500 bg-amber-500" : "border-slate-800"}`}>
                        {isSelected && <Check className="w-3.5 h-3.5 text-white" />}
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* STEP 2: FOCUS AREAS */}
        {wizardStep === 2 && (
          <div className="space-y-5 animate-fade-in">
            <div className="text-center space-y-2">
              <div className="w-12 h-12 rounded-2xl bg-amber-950/20 border border-amber-900/30 text-amber-500 flex items-center justify-center mx-auto">
                <Compass className="w-6 h-6" />
              </div>
              <h2 className="text-2xl sm:text-3xl font-black text-white tracking-tight font-display">
                {texts.titleFocus}
              </h2>
              <p className="text-slate-450 text-xs font-semibold max-w-md mx-auto leading-relaxed">
                {texts.descFocus}
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-[300px] overflow-y-auto pr-1 scroll-smooth-premium">
              {texts.focuses.map((f) => {
                const Icon = getFocusIcon(f.id);
                const isSelected = focus === f.id;
                return (
                  <button
                    key={f.id}
                    type="button"
                    onClick={() => setFocus(f.id)}
                    className={`p-4 rounded-2xl border text-left flex items-start gap-3.5 transition-premium cursor-pointer group ${
                      isSelected
                        ? "bg-amber-950/30 border-amber-500 shadow-md"
                        : "bg-slate-900/10 border-white/5 hover:bg-slate-800/20"
                    }`}
                  >
                    <div className={`p-2 rounded-xl border shrink-0 transition-premium ${
                      isSelected ? "text-amber-500 bg-amber-950/40 border-amber-900/30" : "text-slate-500 bg-slate-800/30 border-white/5"
                    }`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <h4 className={`text-xs font-bold transition-colors ${isSelected ? "text-amber-500" : "text-slate-200 group-hover:text-white"}`}>
                        {f.label}
                      </h4>
                      <p className="text-[10px] text-slate-400 font-medium leading-normal mt-1">
                        {f.desc}
                      </p>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Footer controls */}
        <div className="flex items-center justify-between border-t border-white/5 pt-4">
          {wizardStep > 1 ? (
            <button
              onClick={() => setWizardStep(1)}
              className="px-5 py-2.5 rounded-xl border border-slate-800 text-slate-450 hover:text-white text-xs font-bold transition-premium cursor-pointer"
            >
              {texts.back}
            </button>
          ) : (
            <div />
          )}

          <button
            onClick={handleNext}
            className="px-6 py-2.5 bg-amber-600 hover:bg-amber-500 text-white rounded-xl text-xs font-black uppercase tracking-widest transition-premium cursor-pointer shadow-lg shadow-amber-950/20"
          >
            {wizardStep === 2 ? texts.finish : texts.next}
          </button>
        </div>

      </div>
    </div>
  );
}
