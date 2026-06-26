"use client";

import React, { useState, useEffect, useRef } from "react";
import { 
  Send, Mic, Globe, Sparkles, Search,
  ArrowUpRight, Paperclip, X, FileText, RefreshCw, AlertCircle, 
  CheckCircle, BookOpen, Volume2, Smile, Edit2, Trash2, Copy, Share2, Download, ArrowRight, ShieldCheck, Bookmark, Compass, Folder, MoreVertical
} from "lucide-react";
import YaarOrb from "./YaarOrb";

interface Message {
  id?: number;
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
  has_search?: boolean;
  search_results?: Array<{ title: string; link: string; snippet: string; source?: string; domain?: string; date?: string; summary?: string }> | null;
  rating?: number;
  feedback_notes?: string;
  versions?: string[]; // Version branching content
  currentVersionIndex?: number;
  is_translation_card?: boolean;
  translation_data?: any;
  translations?: Record<string, string>;
  selected_translation_lang?: string;
  source?: "document" | "partial_document" | "web" | "knowledge";
}

interface Document {
  id: number;
  filename: string;
  file_size?: number;
  status: string;
  summary: string | null;
  summary_punjabi: string | null;
  created_at: string;
}

interface ConversationSummary {
  id: number;
  document_id: number | null;
}

interface SpeechRecognitionLike {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  onstart: (() => void) | null;
  onerror: (() => void) | null;
  onend: (() => void) | null;
  onresult: ((event: { results: { [index: number]: { [index: number]: { transcript: string } } } }) => void) | null;
  start: () => void;
  stop: () => void;
}

type SpeechRecognitionConstructor = new () => SpeechRecognitionLike;

/* Legacy local translation responses are intentionally disabled.
  const t = text.toLowerCase().trim();
  const phrases = [
    "kive ho", "kiveho", "ki haal", "ki haal hai", "kem cho", "kemcho", "vanakkam", "namaste", "nomoshkar",
    "kaisa hai", "kya haal", "ela unnavu", "hegidya", "sugamano", "kemit achha", "kive ho veere"
  ];
  if (phrases.some(p => t.includes(p))) return true;

  const keywords = [
    "translate", "translation", "meaning of", "how to say", "how do you say", "meaning lookup",
    "phrase interpretation", "language conversion", "in english", "in hindi", "in punjabi",
    "translate to", "translate into"
  ];
  if (keywords.some(kw => t.includes(kw))) return true;

  return false;
};

const getTranslationDetails = (text: string) => {
  const t = text.toLowerCase().trim();
  if (t.includes("kive ho") || t.includes("ki haal") || t.includes("kem cho") || t.includes("how are you") || t.includes("kaisa hai") || t.includes("kya haal")) {
    return {
      english: "How are you?",
      hindi: "आप कैसे हैं?",
      punjabi: "ਕੀ ਹਾਲ ਹੈ?"
    };
  }
  if (t.includes("thank") || t.includes("dhanyavad") || t.includes("shukriya") || t.includes("meharbani")) {
    return {
      english: "Thank you very much.",
      hindi: "आपका बहुत-बहुत धन्यवाद।",
      punjabi: "ਤੁਹਾਡਾ ਬਹੁਤ-ਬਹੁਤ ਧੰਨਵਾਦ।"
    };
  }
  if (t.includes("morning") || t.includes("saver") || t.includes("prabhat")) {
    return {
      english: "Good morning.",
      hindi: "शुभ प्रभात।",
      punjabi: "ਸ਼ੁਭ ਸਵੇਰ।"
    };
  }
  
  const cleaned = text
    .replace(/translate|meaning of|what is the meaning of|how to say|in english|in hindi|in punjabi/gi, "")
    .trim();
  
  return {
    english: cleaned || "Hello, welcome to YAAR.",
    hindi: cleaned ? `अनुवाद: ${cleaned}` : "नमस्ते, यार में आपका स्वागत है।",
    punjabi: cleaned ? `ਅਨੁਵਾਦ: ${cleaned}` : "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ, ਯਾਰ ਵਿੱਚ ਤੁਹਾਡਾ ਸਵਾਗਤ ਹੈ।"
  };
}; */

const renderContentFormatted = (content: string, searchResults: any[] | null | undefined, msgIndex?: number) => {
  if (!content) return null;

  // 1. Process Citations in the raw string if we have searchResults
  let annotatedContent = content;
  if (searchResults && searchResults.length > 0 && !content.includes("[1]")) {
    const sentences = content.split(". ");
    if (sentences.length > 2) {
      const mid = Math.floor(sentences.length / 2);
      sentences[mid] = sentences[mid] + " [1]";
      sentences[sentences.length - 1] = sentences[sentences.length - 1] + " [2]";
      annotatedContent = sentences.join(". ");
    } else {
      annotatedContent = content + " [1]";
    }
  }

  // 2. Parse inline Markdown (Bold + Citations)
  const parseInlineElements = (text: string): React.ReactNode[] => {
    // First, split by bold markdown
    const boldParts = text.split(/\*\*([^*]+)\*\*/g);
    const nodes: React.ReactNode[] = [];

    boldParts.forEach((part, boldIdx) => {
      const isBold = boldIdx % 2 === 1;
      
      // For each part, further split by citations regex: /\[(\d+)\]/g
      const citationRegex = /\[(\d+)\]/g;
      const citationParts = part.split(citationRegex);
      
      const parsedParts = citationParts.map((subPart, subIdx) => {
        if (subIdx % 2 === 1) {
          const num = parseInt(subPart);
          if (searchResults && searchResults.length >= num) {
            const source = searchResults[num - 1];
            return (
              <a
                key={`cit-${boldIdx}-${subIdx}`}
                href={`#source-card-${msgIndex}-${subPart}`}
                onClick={(e) => {
                  e.preventDefault();
                  if (msgIndex !== undefined) {
                    const target = document.getElementById(`source-card-${msgIndex}-${subPart}`);
                    if (target) {
                      target.scrollIntoView({ behavior: "smooth", block: "center" });
                      target.classList.add("border-amber-500", "bg-amber-950/20");
                      setTimeout(() => {
                        target.classList.remove("border-amber-500", "bg-amber-950/20");
                      }, 2000);
                    }
                  }
                }}
                className="text-amber-500 hover:text-amber-400 font-bold inline-block mx-0.5 font-mono text-[9px] align-super bg-amber-500/10 px-1.5 rounded hover:bg-amber-500/20 transition-premium border border-amber-500/20"
                title={source.title}
              >
                [{subPart}]
              </a>
            );
          }
          return `[${subPart}]`;
        }
        return subPart;
      });

      if (isBold) {
        nodes.push(
          <strong key={`b-${boldIdx}`} className="font-extrabold text-white">
            {parsedParts}
          </strong>
        );
      } else {
        nodes.push(...parsedParts);
      }
    });

    return nodes;
  };

  // 3. Process lines for paragraph and list structure
  const lines = annotatedContent.split('\n');
  const elements: React.ReactNode[] = [];
  
  let inList = false;
  let listItems: React.ReactNode[] = [];

  lines.forEach((line, index) => {
    const trimmed = line.trim();
    // A line starting with '*' or '-' followed by a space is a bullet point
    const isBullet = trimmed.startsWith('* ') || trimmed.startsWith('- ');

    if (isBullet) {
      if (!inList) {
        inList = true;
        listItems = [];
      }
      const itemText = trimmed.substring(2);
      listItems.push(
        <li key={`li-${index}`} className="ml-4 list-disc pl-1 mb-1.5 text-slate-200 leading-relaxed">
          {parseInlineElements(itemText)}
        </li>
      );
    } else {
      if (inList) {
        elements.push(
          <ul key={`ul-${index}`} className="my-2.5 space-y-1 list-inside">
            {listItems}
          </ul>
        );
        inList = false;
      }

      if (trimmed === '') {
        elements.push(<div key={`br-${index}`} className="h-2" />);
      } else {
        elements.push(
          <p key={`p-${index}`} className="mb-2 leading-relaxed text-slate-200">
            {parseInlineElements(line)}
          </p>
        );
      }
    }
  });

  if (inList) {
    elements.push(
      <ul key="ul-final" className="my-2.5 space-y-1 list-inside">
        {listItems}
      </ul>
    );
  }

  return <div className="space-y-1">{elements}</div>;
};

interface ChatInterfaceProps {
  activeConversationId: number | null;
  onSelectConversation: (id: number | null) => void;
  apiBaseUrl: string;
  onRefreshDocuments: () => void;
  sidebarOpen: boolean;
  setSidebarOpen: React.Dispatch<React.SetStateAction<boolean>>;
  token: string | null;
}

export default function ChatInterface({ 
  activeConversationId, 
  onSelectConversation, 
  apiBaseUrl,
  onRefreshDocuments,
  sidebarOpen,
  setSidebarOpen,
  token
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [showControlsDropdown, setShowControlsDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        showControlsDropdown &&
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        buttonRef.current &&
        !buttonRef.current.contains(event.target as Node)
      ) {
        setShowControlsDropdown(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [showControlsDropdown]);

  const [conversationTitle, setConversationTitle] = useState("Chat Session");
  const [inputText, setInputText] = useState("");
  const [enableSearch, setEnableSearch] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [chatLoading, setChatLoading] = useState(false);
  const [grammarFixing, setGrammarFixing] = useState(false);
  const [translatingInput, setTranslatingInput] = useState(false);
  const [translatingMessageIndex, setTranslatingMessageIndex] = useState<number | null>(null);
  const [selectedLanguage, setSelectedLanguage] = useState("Hindi");

  const [projects, setProjects] = useState<any[]>([]);
  const [activeProjectName, setActiveProjectName] = useState<string | null>(null);

  useEffect(() => {
    const loadProjects = () => {
      const saved = localStorage.getItem("yaar_projects");
      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          setProjects(parsed);
          // Find if activeConversationId belongs to any project
          const activeProj = parsed.find((p: any) => (p.chatIds || []).includes(activeConversationId));
          setActiveProjectName(activeProj ? activeProj.name : null);
        } catch (_) {}
      }
    };

    loadProjects();
    window.addEventListener("yaar_projects_updated", loadProjects);
    return () => window.removeEventListener("yaar_projects_updated", loadProjects);
  }, [activeConversationId]);

  const handleMoveToProject = (projName: string) => {
    const saved = localStorage.getItem("yaar_projects");
    if (!saved) return;
    try {
      const parsedProjects: any[] = JSON.parse(saved);
      const updated = parsedProjects.map(p => {
        const chatIds = p.chatIds || [];
        if (p.name === projName) {
          if (!chatIds.includes(activeConversationId)) {
            return { ...p, chatIds: [...chatIds, activeConversationId] };
          }
          return p;
        } else {
          return { ...p, chatIds: chatIds.filter((id: any) => id !== activeConversationId) };
        }
      });
      localStorage.setItem("yaar_projects", JSON.stringify(updated));
      setActiveProjectName(projName === "No Project" ? null : projName);
      window.dispatchEvent(new Event("yaar_projects_updated"));
    } catch (_) {}
  };

  // Inline editing state
  const [editingMsgIndex, setEditingMsgIndex] = useState<number | null>(null);
  const [editingContent, setEditingContent] = useState("");

  const INDIAN_LANGUAGES = [
    "Hindi", "Tamil", "Telugu", "Bengali", "Marathi", "Gujarati",
    "Kannada", "Malayalam", "Odia", "Punjabi", "Assamese", "Urdu", "Sanskrit"
  ];

  const STARTER_PROMPTS = [
    {
      label: "Summarize PDF",
      prompt: "Summarize this PDF in simple bullet points and create action items.",
      icon: FileText
    },
    {
      label: "Translate Punjabi",
      prompt: "Translate this into Punjabi and keep the tone natural for Indian readers: ",
      icon: Globe
    },
    {
      label: "Search Schemes",
      prompt: "Search the web and explain current Government schemes for students in Punjab with eligibility and links.",
      icon: Search
    },
    {
      label: "Create UPSC Notes",
      prompt: "Create UPSC-style notes on Digital Public Infrastructure in India with examples and mains answer points.",
      icon: BookOpen
    }
  ];
  
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
  const [mobileTab, setMobileTab] = useState<"chat" | "document">("chat");
  const [uploading, setUploading] = useState(false);
  const [speakingMessageIndex, setSpeakingMessageIndex] = useState<number | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (messages.length > 0 || chatLoading) {
      scrollToBottom();
    }
  }, [messages, chatLoading]);

  // Load conversations
  useEffect(() => {
    window.speechSynthesis.cancel();
    setSpeakingMessageIndex(null);
    setEditingMsgIndex(null);

    if (activeConversationId) {
      const email = localStorage.getItem("bharatai_email") || "companion@yaar.ai";
      const localMsgKey = `yaar_messages_${activeConversationId}`;

      const loadHistory = async () => {
        // 1. First-class local read
        const savedMsg = localStorage.getItem(localMsgKey);
        if (savedMsg) {
          try {
            setMessages(JSON.parse(savedMsg));
          } catch (_) {}
        }

        // 2. Try backend sync
        try {
          const res = await fetch(`${apiBaseUrl}/api/conversations/${activeConversationId}/messages`, {
            headers: { "Authorization": `Bearer ${token}` }
          });
          if (res.ok) {
            const data = await res.json();
            let localParsed: any[] = [];
            if (savedMsg) {
              try { localParsed = JSON.parse(savedMsg); } catch (_) {}
            }
            const formatted = data.map((m: any, idx: number) => {
              const localMsg = localParsed[idx];
              const isMatch = localMsg && localMsg.role === m.role;
              const selected_lang = isMatch ? (localMsg.selected_translation_lang || "Original") : "Original";
              const translations = isMatch ? (localMsg.translations || {}) : {};
              const content = (selected_lang !== "Original" && translations[selected_lang]) 
                ? translations[selected_lang] 
                : m.content;
              return {
                ...m,
                content: content,
                versions: isMatch ? (localMsg.versions || [m.content]) : (m.versions || [m.content]),
                currentVersionIndex: isMatch ? (localMsg.currentVersionIndex ?? 0) : (m.currentVersionIndex ?? 0),
                translations: translations,
                selected_translation_lang: selected_lang
              };
            });
            setMessages(formatted);
            localStorage.setItem(localMsgKey, JSON.stringify(formatted));
          }
        } catch (err) {
          console.error("Failed to sync conversation history from backend:", err);
        }
      };
      loadHistory();

      // Local title lookup
      const localChatsKey = `yaar_chats_${email}`;
      const savedLocal = localStorage.getItem(localChatsKey);
      if (savedLocal) {
        try {
          const localList = JSON.parse(savedLocal);
          const current = localList.find((c: any) => c.id === activeConversationId);
          if (current) {
            setConversationTitle(current.title || "Chat Session");
          }
        } catch (_) {}
      }

      const loadDocDetails = async () => {
        try {
          const res = await fetch(`${apiBaseUrl}/api/conversations`, {
            headers: { "Authorization": `Bearer ${token}` }
          });
          if (res.ok) {
            const conversations = await res.json();
            const current = (conversations as any[]).find((c) => c.id === activeConversationId);
            if (current) {
              setConversationTitle(current.title || "Chat Session");
            }
            
            if (current && current.document_id) {
              const docRes = await fetch(`${apiBaseUrl}/api/documents/${current.document_id}`, {
                headers: { "Authorization": `Bearer ${token}` }
              });
              if (docRes.ok) {
                const docDetails = await docRes.json();
                setSelectedDoc(docDetails);
                return;
              }
            }
          }
        } catch (err) {
          console.error("Failed to load conversation details:", err);
        }
        setSelectedDoc(null);
      };
      loadDocDetails();
    } else {
      setMessages([]);
      setSelectedDoc(null);
    }
  }, [activeConversationId, token, apiBaseUrl]);

  // Handle auto-sending of pending prompts from Life Hub
  useEffect(() => {
    if (activeConversationId && messages.length === 0 && !chatLoading) {
      if (typeof window !== "undefined") {
        const isNewPending = localStorage.getItem("yaar_new_conversation_pending");
        const pendingPrompt = localStorage.getItem("yaar_pending_prompt");
        const pendingSearch = localStorage.getItem("yaar_pending_search");
        if (isNewPending === "true") {
          localStorage.removeItem("yaar_new_conversation_pending");
          if (pendingSearch === "true") {
            setEnableSearch(true);
            localStorage.removeItem("yaar_pending_search");
          }
          if (pendingPrompt) {
            localStorage.removeItem("yaar_pending_prompt");
            handleSend(pendingPrompt);
          }
        }
      }
    }
  }, [activeConversationId, messages.length, chatLoading]);

  // Document polling
  useEffect(() => {
    if (!selectedDoc || selectedDoc.status !== "processing" || !token) return;

    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${apiBaseUrl}/api/documents/${selectedDoc.id}`, {
          headers: { "Authorization": `Bearer ${token}` }
        });
        if (res.ok) {
          const updated = await res.json();
          if (updated.status !== "processing") {
            setSelectedDoc(updated);
            onRefreshDocuments();
            clearInterval(interval);
          }
        }
      } catch (err) {
        console.error("Error polling document status:", err);
      }
    }, 2500);

    return () => clearInterval(interval);
  }, [selectedDoc?.id, selectedDoc?.status, token, apiBaseUrl, onRefreshDocuments]);

  const ensureConversation = async (): Promise<number> => {
    if (activeConversationId) return activeConversationId;
    
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
        onSelectConversation(data.id);
        onRefreshDocuments();
        return data.id;
      }
    } catch (err) {
      console.error("Auto-creation of conversation session failed, using local ID:", err);
    }

    const localId = Date.now();
    onSelectConversation(localId);
    onRefreshDocuments();
    return localId;
  };

  /* Legacy local chat responses are intentionally disabled.
    const p = prompt.toLowerCase();
    const name = localStorage.getItem("yaar_user_name") || "Dost";
    
    const translations: Record<string, {
      default: string;
      help: string;
      greet: string;
      learn: string;
      work: string;
      build: string;
    }> = {
      English: {
        default: `That sounds like an amazing journey, ${name}! Let's dive deeper. Tell me more, what else is on your mind?`,
        help: "I'd be glad to help you. We can break this down into clear steps or organize a visual plan.",
        greet: `Hello friend! I am very glad to connect with you. What should we learn or build today?`,
        learn: "Learning is a marathon. Let's outline the core terms, summarize the main points, and structure a study list.",
        work: "Let's focus on structured efficiency. We can draft this email, summarize the notes, or organize your roadmap.",
        build: "Building a startup requires focus. Let's brainstorm your customer profile, outline your MVP, or discuss the tech stack."
      },
      Hindi: {
        default: `यह बहुत ही बढ़िया है, ${name}! आइए इसके बारे में और विस्तार से बात करते हैं। आपके पास क्या विचार हैं?`,
        help: "मुझे आपकी मदद करने में बहुत खुशी होगी। हम इसे आसान चरणों में बांट सकते हैं या एक योजना बना सकते हैं।",
        greet: "नमस्ते दोस्त! आपसे जुड़कर बहुत अच्छा लगा। आज हम किस चीज़ पर काम करने वाले हैं?",
        learn: "सीखना एक सुंदर अनुभव है। आइए मुख्य बातों को समझते हैं और एक अध्ययन सूची तैयार करते हैं।",
        work: "आइए आज का काम आसान बनाते हैं। हम ईमेल का मसौदा बना सकते हैं या आपकी कार्ययोजना व्यवस्थित कर सकते हैं।",
        build: "स्टार्टअप बनाना एक जुनून है। आइए आपके बिजनेस मॉडल, एमवीपी योजना, या तकनीकी पहलुओं पर विचार करें।"
      },
      Punjabi: {
        default: `ਇਹ ਬਹੁਤ ਹੀ ਵਧੀਆ ਵਿਚਾਰ ਹੈ, ${name}! ਆਓ ਇਸ ਬਾਰੇ ਹੋਰ ਗੱਲ ਕਰੀਏ। ਮੈਂ ਹਮੇਸ਼ਾ ਤੁਹਾਡੇ ਨਾਲ ਹਾਂ।`,
        help: "ਮੈਨੂੰ ਤੁਹਾਡੀ ਮਦਦ ਕਰਕੇ ਬਹੁਤ ਖੁਸ਼ੀ ਮਿਲੇਗੀ। ਆਓ ਮਿਲ ਕੇ ਇੱਕ ਸੌਖੀ ਯੋਜਨਾ ਤਿਆਰ ਕਰੀਏ।",
        greet: "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ ਦੋਸਤ! ਤੁਹਾਡੇ ਨਾਲ ਗੱਲ ਕਰਕੇ ਬਹੁਤ ਚੰਗਾ ਲੱਗਿਆ। ਅੱਜ ਆਪਾਂ ਕਿਸ ਚੀਜ਼ 'ਤੇ ਕੰਮ ਕਰਨਾ ਹੈ?",
        learn: "ਪੜ੍ਹਾਈ ਇੱਕ ਯਾਤਰਾ ਹੈ। ਆਓ ਸਾਰੇ ਮੁੱਖ ਨੁਕਤੇ ਸਮਝੀਏ ਅਤੇ ਤੁਹਾਡੇ ਲਈ ਇੱਕ ਵਧੀਆ ਸਟੱਡੀ ਪਲਾਨ ਬਣਾਈਏ।",
        work: "ਆਓ ਤੁਹਾਡਾ ਕੰਮ ਸੌਖਾ ਕਰੀਏ। ਅਸੀਂ ਈਮੇਲ ਲਿਖ ਸਕਦੇ ਹਾਂ, ਰਿਪੋਰਟ ਦੀ ਰੂਪਰੇਖਾ ਬਣਾ ਸਕਦੇ ਹਾਂ ਜਾਂ ਕੰਮਾਂ ਨੂੰ ਤਰਤੀਬ ਦੇ ਸਕਦੇ ਹਾਂ।",
        build: "ਸਟਾਰਟਅੱਪ ਸ਼ੁਰੂ ਕਰਨਾ ਇੱਕ ਵੱਡਾ ਹੌਸਲਾ ਹੈ। ਆਓ ਮਿਲ ਕੇ ਬਿਜ਼ਨਸ ਮਾਡਲ, MVP ਯੋਜਨਾ ਜਾਂ ਤਕਨੀਕੀ ਚੀਜ਼ਾਂ 'ਤੇ ਵਿਚਾਰ ਕਰੀਏ।"
      },
      Gujarati: {
        default: `આ ખરેખર સરસ બાબત છે, ${name}! ચાલો આ વિશે વધુ વાત કરીએ. આપનો વિચાર શું છે?`,
        help: "મને આપની મદદ કરતાં ખૂબ જ આનંદ થશે. આપણે આને સરળ ભાગોમાં વહેંચીને આયોજન કરી શકીએ.",
        greet: "કેમ cho મિત્ર! આપની સાથે જોડાઈને આનંદ થયો. આજે આપણે શેના પર કામ કરવાના છીએ?",
        learn: "શીખવું એ એક સુંદર સફર છે. ચાલો મુખ્ય બાબતો સમજીએ અને આપના માટે અભ્યાસનું આયોજન કરીએ.",
        work: "ચાલો કામને વ્યવસ્થિત કરીએ. આપણે ઇમેઇલ ડ્રાફ્ટ કરી શકીએ, રિપોર્ટ બનાવી શકીએ અથવા કામોની યાદી ગોઠવી શકીએ.",
        build: "સ્ટાર્ટઅપ શરૂ કરવું એ દોડ સમાન છે. ચાલો આપના બિઝનેસ મોડલ કે ટેકનોલોજી વિશે ચર્ચા કરીએ."
      },
      Bengali: {
        default: `এটি দারুণ বিষয়, ${name}! চলুন এটি নিয়ে আরও গভীরে আলোচনা করি। আমি সবসময় পাশে আছি।`,
        help: "আপনার সাহায্য করতে পারলে আমার খুব ভালো লাগবে। আমরা এটিকে সহজ ধাপে ভাগ করে পরিকল্পনা করতে পারি।",
        greet: "নমস্কার বন্ধু! আপনার সাথে যুক্ত হতে পেরে খুব আনন্দিত হলাম। আজ আমরা কি নিয়ে কাজ শুরু করব?",
        learn: "শেখার কোন শেষ নেই। চলুন মূল বিষয়গুলো সংক্ষেপে বুঝে নিয়ে একটি সহজ রুটিন তৈরি করি।",
        work: "চলুন কাজটিকে গুছিয়ে নেওয়া যাক। আমরা মেইল ড্রাফট করতে পারি বা আপনার কাজের তালিকা সাজাতে পারি।",
        build: "স্টার্টআপ তৈরি করা একটি ম্যারাথন। চলুন আপনার বিজনেস মডেল, এমভিপি পরিকল্পনা কিংবা টেকনিক্যাল দিকগুলো নিয়ে আলোচনা করি।"
      },
      Tamil: {
        default: `இது மிகவும் சுவாரஸ்யமானது, ${name}! இதைப் பற்றி விரிவாகப் பேசுவோம். நான் உங்களுக்கு உதவ எப்போதும் தயாராக உள்ளேன்.`,
        help: "உங்களுக்கு உதவுவதில் எனக்கு மகிழ்ச்சி. இதை எளிய படிகளாகப் பிரித்து நாம் ஒரு திட்டத்தை உருவாக்கலாம்.",
        greet: "வணக்கம் நண்பா! உங்களுடன் இணைந்ததில் மகிழ்ச்சி. இன்று நாம் என்ன வேலை செய்யப் போகிறோம்?",
        learn: "கற்றல் ஒரு பயணம். முக்கிய கருத்துக்களைப் புரிந்துகொண்டு உங்களுக்கான ஒரு படிப்புத் திட்டத்தை உருவாக்குவோம்.",
        work: "வேலையை எளிதாக்குவோம். மின்னஞ்சல் எழுதலாம், அறிக்கையைத் தயாரித்து பணிகளை வரிசைப்படுத்தலாம்.",
        build: "தொழில் தொடங்குவது ஒரு நெடும் பயணம். உங்கள் தொழில் மாதிரி, MVP திட்டம் அல்லது தொழில்நுட்பம் பற்றி விவாதிப்போம்."
      }
    };

    const selectedDict = translations[lang] || translations["English"];
    if (p.includes("help") || p.includes("madad") || p.includes("ਸਹਾਇਤਾ")) return selectedDict.help;
    if (p.includes("hello") || p.includes("hi") || p.includes("namaste") || p.includes("greetings") || p.includes("akal")) return selectedDict.greet;
    if (p.includes("learn") || p.includes("study") || p.includes("padhai") || p.includes("ਪੜ੍ਹਾਈ")) return selectedDict.learn;
    if (p.includes("work") || p.includes("job") || p.includes("email") || p.includes("kaam") || p.includes("ਕੰਮ")) return selectedDict.work;
    if (p.includes("build") || p.includes("startup") || p.includes("founder")) return selectedDict.build;

    return selectedDict.default;
  }; */

  const handleSend = async (textToSend = inputText) => {
    const text = textToSend.trim();
    if (!text || chatLoading) return;

    setChatLoading(true);
    const userLang = localStorage.getItem("yaar_language") || "English";
    const userVibe = localStorage.getItem("yaar_personality") || "friendly";

    // Track search memory
    if (enableSearch && text.length > 3) {
      try {
        const savedSearches: string[] = JSON.parse(localStorage.getItem("yaar_search_memory") || "[]");
        const deduped = [text, ...savedSearches.filter(s => s !== text)].slice(0, 10);
        localStorage.setItem("yaar_search_memory", JSON.stringify(deduped));
      } catch (_) {}
    }

    const newUserMessage: Message = {
      role: "user",
      content: text,
      has_search: enableSearch,
      versions: [text],
      currentVersionIndex: 0
    };
    
    const nextMessages = [...messages, newUserMessage];
    setMessages(nextMessages);
    setInputText("");

    const convId = await ensureConversation();
    const localMsgKey = `yaar_messages_${convId}`;
    localStorage.setItem(localMsgKey, JSON.stringify(nextMessages));

    try {
      const response = await fetch(`${apiBaseUrl}/api/chat`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          message: text,
          conversation_id: convId,
          enable_search: enableSearch,
          history: nextMessages.slice(-10).map(m => ({ role: m.role, content: m.content })),
          language: userLang,
          personality: userVibe
        }),
      });

      if (!response.ok) throw new Error("Failed to send message");

      const data = await response.json();
      
      const newAssistantMessage: Message = {
        id: data.message_id,
        role: "assistant",
        content: data.response,
        has_search: data.has_search,
        search_results: data.search_results,
        versions: [data.response],
        currentVersionIndex: 0,
        source: data.source
      };

      const updatedHistory = [...nextMessages, newAssistantMessage];
      setMessages(updatedHistory);
      localStorage.setItem(localMsgKey, JSON.stringify(updatedHistory));
      onRefreshDocuments();
    } catch (err) {
      console.error("Backend chat failed:", err);
      const errorMessage = "I couldn't reach the AI service just now. Please check that the backend is running and try again.";
      const newAssistantMessage: Message = {
        id: Date.now(),
        role: "assistant",
        content: errorMessage,
        versions: [errorMessage],
        currentVersionIndex: 0
      };
      const updatedHistory = [...nextMessages, newAssistantMessage];
      setMessages(updatedHistory);
      localStorage.setItem(localMsgKey, JSON.stringify(updatedHistory));
    } finally {
      setChatLoading(false);
    }
  };

  const handleStarterPrompt = (prompt: string) => {
    setInputText(prompt);
    if (prompt.toLowerCase().includes("search")) {
      setEnableSearch(true);
    }
  };

  const handleFileUpload = async (file: File) => {
    if (!file.name.endsWith(".pdf")) {
      alert("Only PDF files are supported.");
      return;
    }

    const maxUploadBytes = 10 * 1024 * 1024;
    if (file.size > maxUploadBytes) {
      alert("This PDF is too large for beta. Please upload a file under 10MB.");
      return;
    }

    setUploading(true);

    try {
      const convId = await ensureConversation();

      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(`${apiBaseUrl}/api/documents/upload`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`
        },
        body: formData,
      });

      if (!res.ok) {
        const detail = await res.json().then(d => d.detail).catch(() => "Upload failed");
        throw new Error(detail);
      }

      const docData = await res.json();

      const attachRes = await fetch(`${apiBaseUrl}/api/conversations/${convId}`, {
        method: "PUT",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ document_id: docData.id })
      });
      if (!attachRes.ok) throw new Error("Failed to bind document to conversation");

      const docDetailsRes = await fetch(`${apiBaseUrl}/api/documents/${docData.id}`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (docDetailsRes.ok) {
        const docDetails = await docDetailsRes.json();
        setSelectedDoc(docDetails);
        setMobileTab("chat");
        
        const promptSystemMsg: Message = {
          role: "assistant",
          content: `📎 **Document '${file.name}' attached successfully!**\n\nWhat would you like me to do with this document?\n1. **Summarize** the contents in Simple English or Punjabi.\n2. Run a **Compliance Audit** (DPDP Act, Legal Risk, or IRDAI).\n3. Extract text with **Layout-Preserved OCR**.\n4. Answer specific questions based on the text.`,
          versions: [`📎 **Document '${file.name}' attached successfully!**\n\nWhat would you like me to do with this document?\n1. **Summarize** the contents in Simple English or Punjabi.\n2. Run a **Compliance Audit** (DPDP Act, Legal Risk, or IRDAI).\n3. Extract text with **Layout-Preserved OCR**.\n4. Answer specific questions based on the text.`],
          currentVersionIndex: 0
        };
        setMessages(prev => [...prev, promptSystemMsg]);
      }

      onRefreshDocuments();
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "An error occurred during file upload.");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileUpload(e.target.files[0]);
    }
  };

  const handleDetachDoc = async () => {
    if (!activeConversationId) return;
    try {
      const res = await fetch(`${apiBaseUrl}/api/conversations/${activeConversationId}`, {
        method: "PUT",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ document_id: -1 })
      });
      if (res.ok) {
        setSelectedDoc(null);
        onRefreshDocuments();
      }
    } catch (err) {
      console.error("Failed to detach document:", err);
    }
  };

  const toggleListening = () => {
    const browserWindow = window as Window & {
      SpeechRecognition?: SpeechRecognitionConstructor;
      webkitSpeechRecognition?: SpeechRecognitionConstructor;
    };
    const SpeechRecognition = browserWindow.SpeechRecognition || browserWindow.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Voice input is not supported in this browser. Please use Chrome or Edge.");
      return;
    }

    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-IN";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => setIsListening(true);
    recognition.onerror = () => setIsListening(false);
    recognition.onend = () => setIsListening(false);

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInputText(prev => prev + (prev ? " " : "") + transcript);
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  // Advanced Message Actions: Edit Message
  const handleStartEdit = (idx: number, content: string) => {
    setEditingMsgIndex(idx);
    setEditingContent(content);
  };

  const handleSaveEdit = async (idx: number) => {
    if (!editingContent.trim() || chatLoading) return;

    setChatLoading(true);
    setEditingMsgIndex(null);

    const userLang = localStorage.getItem("yaar_language") || "English";
    const userVibe = localStorage.getItem("yaar_personality") || "friendly";

    // 1. Remove all subsequent messages from list
    const prunedMessages = messages.slice(0, idx);
    
    // 2. Add edited message as a new user message
    const editedUserMsg: Message = {
      role: "user",
      content: editingContent.trim(),
      versions: [editingContent.trim()],
      currentVersionIndex: 0
    };

    const nextMessages = [...prunedMessages, editedUserMsg];
    setMessages(nextMessages);

    const convId = await ensureConversation();
    const localMsgKey = `yaar_messages_${convId}`;
    localStorage.setItem(localMsgKey, JSON.stringify(nextMessages));

    try {
      const response = await fetch(`${apiBaseUrl}/api/chat`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          message: editingContent.trim(),
          conversation_id: convId,
          enable_search: enableSearch,
          history: prunedMessages.map(m => ({ role: m.role, content: m.content })),
          language: userLang,
          personality: userVibe
        }),
      });

      if (!response.ok) throw new Error("Failed to send message");

      const data = await response.json();
      
      const newAssistantMessage: Message = {
        id: data.message_id,
        role: "assistant",
        content: data.response,
        has_search: data.has_search,
        search_results: data.search_results,
        versions: [data.response],
        currentVersionIndex: 0,
        source: data.source
      };

      const updatedHistory = [...nextMessages, newAssistantMessage];
      setMessages(updatedHistory);
      localStorage.setItem(localMsgKey, JSON.stringify(updatedHistory));
      onRefreshDocuments();
    } catch (e) {
      console.error("Save edit backend failed:", e);
      const errorMessage = "I couldn't reach the AI service just now. Please check that the backend is running and try again.";
      const newAssistantMessage: Message = {
        id: Date.now(),
        role: "assistant",
        content: errorMessage,
        versions: [errorMessage],
        currentVersionIndex: 0
      };
      const updatedHistory = [...nextMessages, newAssistantMessage];
      setMessages(updatedHistory);
      localStorage.setItem(localMsgKey, JSON.stringify(updatedHistory));
    } finally {
      setChatLoading(false);
    }
  };

  // Advanced Message Actions: Delete Message
  const handleDeleteMessage = (idx: number) => {
    if (!confirm("Are you sure you want to remove this message?")) return;
    const email = localStorage.getItem("bharatai_email") || "companion@yaar.ai";
    const updated = messages.filter((_, i) => i !== idx);
    setMessages(updated);
    if (activeConversationId) {
      localStorage.setItem(`yaar_messages_${activeConversationId}`, JSON.stringify(updated));
    }
  };

  // Advanced Message Actions: Copy Response
  const handleCopyMessage = (text: string) => {
    navigator.clipboard.writeText(text);
    alert("Message copied to clipboard!");
  };

  // Advanced Message Actions: Regenerate Response
  const handleRegenerate = async (idx: number) => {
    if (chatLoading) return;
    setChatLoading(true);

    const userLang = localStorage.getItem("yaar_language") || "English";
    const userVibe = localStorage.getItem("yaar_personality") || "friendly";
    const convId = await ensureConversation();
    const localMsgKey = `yaar_messages_${convId}`;

    // Find the user prompt for this assistant message (the previous user message)
    let promptText = "";
    for (let i = idx - 1; i >= 0; i--) {
      if (messages[i].role === "user") {
        promptText = messages[i].content;
        break;
      }
    }

    if (!promptText) promptText = "Regenerate last response";
    const historyMsg = messages.slice(0, idx);

    try {
      const response = await fetch(`${apiBaseUrl}/api/chat`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          message: promptText,
          conversation_id: convId,
          enable_search: enableSearch,
          history: historyMsg.slice(-10).map(m => ({ role: m.role, content: m.content })),
          language: userLang,
          personality: userVibe
        }),
      });

      if (!response.ok) throw new Error("Failed to regenerate");

      const data = await response.json();
      
      const updated = messages.map((m, i) => {
        if (i === idx) {
          const currentVersions = m.versions || [m.content];
          const newVersions = [...currentVersions, data.response];
          return {
            ...m,
            content: data.response,
            versions: newVersions,
            currentVersionIndex: newVersions.length - 1,
            source: data.source
          };
        }
        return m;
      });
      setMessages(updated);
      localStorage.setItem(localMsgKey, JSON.stringify(updated));
    } catch (e) {
      console.error("Regenerate backend failed:", e);
      alert("I couldn't reach the AI service just now. Please check that the backend is running and try again.");
    } finally {
      setChatLoading(false);
    }
  };

  // Version toggling
  const handleToggleVersion = (msgIdx: number, direction: "prev" | "next") => {
    setMessages(prev => prev.map((m, i) => {
      if (i === msgIdx) {
        const versions = m.versions || [m.content];
        let currentIdx = m.currentVersionIndex ?? 0;
        
        if (direction === "prev") {
          currentIdx = Math.max(0, currentIdx - 1);
        } else {
          currentIdx = Math.min(versions.length - 1, currentIdx + 1);
        }
        
        return {
          ...m,
          content: versions[currentIdx],
          currentVersionIndex: currentIdx
        };
      }
      return m;
    }));
  };

  // Advanced Message Actions: Share message
  const handleShareMessage = (text: string) => {
    navigator.clipboard.writeText(text);
    alert("Shareable link copied to clipboard (Mocked)!");
  };

  // Advanced Message Actions: Export Conversation as Markdown
  const handleExportChat = () => {
    if (messages.length === 0) return;
    const content = messages
      .map(m => `**${m.role.toUpperCase()}**:\n${m.content}\n\n---`)
      .join("\n\n");
    
    const blob = new Blob([content], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `yaar-chat-${activeConversationId || "export"}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const [vaultToast, setVaultToast] = useState<string | null>(null);

  // Second Brain: Save to Vault Integration
  const handleSaveToVault = (content: string, customTitle?: string) => {
    if (typeof window === "undefined") return;

    const savedVault = localStorage.getItem("yaar_vault");
    let items: any[] = [];
    if (savedVault) {
      try { items = JSON.parse(savedVault); } catch (_) {}
    }

    // Generate a smart title from content
    const words = content.replace(/[*#`_]/g, "").trim().split(/\s+/);
    const autoTitle = customTitle || (words.slice(0, 6).join(" ") + (words.length > 6 ? "..." : ""));

    const newItem = {
      id: `vault-${Date.now()}`,
      title: autoTitle,
      content: content,
      type: "Saved Answer",
      tags: ["Companion", "Saved"],
      created_at: new Date().toISOString()
    };

    localStorage.setItem("yaar_vault", JSON.stringify([newItem, ...items]));
    setVaultToast("✓ Saved to your Vault");
    setTimeout(() => setVaultToast(null), 2500);
  };

  // Indian Languages Translation integration
  const handleTranslateMessage = async (idx: number, targetLanguage: string) => {
    const msg = messages[idx];
    if (!msg) return;
    const original = msg.versions?.[0] || msg.content;
    const localMsgKey = activeConversationId ? `yaar_messages_${activeConversationId}` : null;
    
    // If target language is Original, revert instantly
    if (targetLanguage === "Original") {
      setMessages(prev => prev.map((m, i) => {
        if (i === idx) {
          const updated = {
            ...m,
            content: original,
            selected_translation_lang: "Original"
          };
          if (localMsgKey) {
            const saved = localStorage.getItem(localMsgKey);
            if (saved) {
              try {
                const list = JSON.parse(saved);
                list[idx] = updated;
                localStorage.setItem(localMsgKey, JSON.stringify(list));
              } catch (_) {}
            }
          }
          return updated;
        }
        return m;
      }));
      return;
    }

    // Check cache
    const cached = msg.translations?.[targetLanguage];
    if (cached) {
      setMessages(prev => prev.map((m, i) => {
        if (i === idx) {
          const updated = {
            ...m,
            content: cached,
            selected_translation_lang: targetLanguage
          };
          if (localMsgKey) {
            const saved = localStorage.getItem(localMsgKey);
            if (saved) {
              try {
                const list = JSON.parse(saved);
                list[idx] = updated;
                localStorage.setItem(localMsgKey, JSON.stringify(list));
              } catch (_) {}
            }
          }
          return updated;
        }
        return m;
      }));
      return;
    }

    setTranslatingMessageIndex(idx);
    try {
      const res = await fetch(`${apiBaseUrl}/api/tools/translate`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ text: original, target_language: targetLanguage })
      });
      if (res.ok) {
        const data = await res.json();
        setMessages(prev => prev.map((m, i) => {
          if (i === idx) {
            const currentVersions = m.versions || [original];
            const translationCache = { ...(m.translations || {}), [targetLanguage]: data.translated_text };
            const newVersions = currentVersions.includes(data.translated_text)
              ? currentVersions
              : [...currentVersions, data.translated_text];
            const updated = {
              ...m,
              content: data.translated_text,
              translations: translationCache,
              versions: newVersions,
              currentVersionIndex: newVersions.length - 1,
              selected_translation_lang: targetLanguage
            };
            if (localMsgKey) {
              const saved = localStorage.getItem(localMsgKey);
              if (saved) {
                try {
                  const list = JSON.parse(saved);
                  list[idx] = updated;
                  localStorage.setItem(localMsgKey, JSON.stringify(list));
                } catch (_) {}
              }
            }
            return updated;
          }
          return m;
        }));
      }
    } catch (e) {
      console.error(e);
    } finally {
      setTranslatingMessageIndex(null);
    }
  };

  const toggleSpeakMessage = (idx: number, content: string) => {
    if (speakingMessageIndex === idx) {
      window.speechSynthesis.cancel();
      setSpeakingMessageIndex(null);
      return;
    }
    window.speechSynthesis.cancel();
    const cleanText = content.replace(/[*#`_]/g, "");
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.onend = () => setSpeakingMessageIndex(null);
    setSpeakingMessageIndex(idx);
    window.speechSynthesis.speak(utterance);
  };

  const handleFixGrammar = async () => {
    if (!inputText.trim() || grammarFixing) return;
    setGrammarFixing(true);
    try {
      const res = await fetch(`${apiBaseUrl}/api/tools/grammar-fix`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ text: inputText })
      });
      if (res.ok) {
        const data = await res.json();
        setInputText(data.fixed_text);
        setGrammarFixing(false);
        return;
      }
    } catch (e) {
      console.error("Grammar backend failed, running local fix:", e);
    }
    
    // Local simple clean
    setTimeout(() => {
      const trimmed = inputText.trim();
      const fixed = trimmed.charAt(0).toUpperCase() + trimmed.slice(1) + (trimmed.endsWith(".") || trimmed.endsWith("?") || trimmed.endsWith("!") ? "" : ".");
      setInputText(fixed);
      setGrammarFixing(false);
    }, 400);
  };



  return (
    <div className="flex-1 h-full flex flex-col md:flex-row bg-[#06070d] overflow-hidden">
      
      {/* LEFT CHAT PORTAL */}
      <div className={`flex-1 h-full flex flex-col border-r border-slate-900 ${mobileTab === "chat" ? "flex" : "hidden md:flex"} relative`}>
        
        {/* Vault Toast notification */}
        {vaultToast && (
          <div className="absolute bottom-24 left-1/2 -translate-x-1/2 z-50 px-4 py-2.5 bg-emerald-900/90 border border-emerald-700/50 text-emerald-300 text-xs font-black uppercase tracking-wider rounded-xl shadow-lg backdrop-blur-md animate-fade-in flex items-center gap-2">
            <span>{vaultToast}</span>
          </div>
        )}
        
        {/* Top controls menu header */}
        <div className={`p-4 border-b border-slate-900 flex items-center justify-between shrink-0 bg-[#06070d]/60 backdrop-blur-md ${!sidebarOpen ? "pl-14" : "pl-4"}`}>
          <div className="flex items-center gap-3 min-w-0">
            <h2 className="text-xs font-black uppercase tracking-wider text-slate-100 truncate font-display">
              {conversationTitle}
            </h2>
          </div>

          <div className="flex items-center gap-2 shrink-0 relative">
            <button
              onClick={handleExportChat}
              disabled={messages.length === 0}
              className="p-1.5 rounded-lg hover:bg-slate-900 text-slate-400 hover:text-white transition-premium cursor-pointer border border-transparent disabled:opacity-40"
              title="Export conversation as Markdown"
            >
              <Download className="w-4 h-4" />
            </button>
            <button
              ref={buttonRef}
              onClick={() => setShowControlsDropdown(!showControlsDropdown)}
              className={`p-1.5 rounded-lg hover:bg-slate-900 text-slate-400 hover:text-white transition-premium cursor-pointer ${showControlsDropdown ? "bg-slate-900 text-white" : ""}`}
              title="Workspace Controls"
            >
              <MoreVertical className="w-4 h-4" />
            </button>
            <button
              onClick={() => onSelectConversation(null)}
              className="p-1.5 rounded-lg hover:bg-slate-900 text-slate-400 hover:text-white transition-premium cursor-pointer border border-transparent"
              title="Return to Dashboard"
            >
              <X className="w-4 h-4" />
            </button>

            {/* Dropdown Menu */}
            {showControlsDropdown && (
              <div 
                ref={dropdownRef}
                onClick={(e) => e.stopPropagation()}
                onMouseDown={(e) => e.stopPropagation()}
                className="absolute right-0 top-10 w-64 bg-slate-950 border border-slate-900 rounded-xl shadow-2xl p-3.5 z-50 space-y-4 animate-fade-in text-left"
              >
                <div className="flex items-center justify-between border-b border-white/5 pb-2">
                  <span className="text-[10px] font-black uppercase tracking-widest text-amber-500">Workspace Menu</span>
                  <button
                    onClick={() => setShowControlsDropdown(false)}
                    className="text-slate-500 hover:text-white"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>

                {/* Home navigation */}
                <button
                  onClick={() => {
                    onSelectConversation(null);
                    setShowControlsDropdown(false);
                  }}
                  className="w-full flex items-center gap-2 px-3 py-2 bg-slate-900/60 border border-slate-900 hover:border-amber-500/20 text-xs font-bold text-slate-300 hover:text-white rounded-lg transition-colors cursor-pointer"
                >
                  <Compass className="w-4 h-4 text-amber-500" />
                  <span>Go to Home</span>
                </button>

                {/* Active Session Mode Badges */}
                <div className="space-y-1">
                  <span className="text-[9px] uppercase tracking-wider font-extrabold text-slate-500 block px-1">Active Mode</span>
                  {selectedDoc ? (
                    <div className="flex items-center justify-between bg-blue-950/40 border border-blue-900/30 rounded-lg p-2">
                      <span className="text-[10px] font-black text-blue-400 truncate max-w-[170px]">
                        📄 Document: {selectedDoc.filename}
                      </span>
                      <button
                        onClick={handleDetachDoc}
                        className="text-blue-400 hover:text-white"
                        title="Detach Document"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  ) : enableSearch ? (
                    <div className="bg-emerald-950/40 border border-emerald-900/30 rounded-lg p-2 flex items-center gap-1.5">
                      <Globe className="w-3.5 h-3.5 text-emerald-500" />
                      <span className="text-[10px] font-black text-emerald-450">
                        🌐 Live Search Enabled
                      </span>
                    </div>
                  ) : (
                    <div className="bg-purple-950/40 border border-purple-900/30 rounded-lg p-2 flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-purple-500" />
                      <span className="text-[10px] font-black text-purple-450">
                        🧠 General Knowledge
                      </span>
                    </div>
                  )}
                </div>

                {/* Project selector */}
                <div className="space-y-1">
                  <span className="text-[9px] uppercase tracking-wider font-extrabold text-slate-500 block px-1">Project Binder</span>
                  <div className="flex items-center gap-2 bg-slate-900 border border-slate-900 rounded-lg p-2">
                    <Folder className="w-3.5 h-3.5 text-amber-500 shrink-0" />
                    <select
                      value={activeProjectName || "No Project"}
                      onChange={(e) => {
                        handleMoveToProject(e.target.value);
                      }}
                      className="bg-transparent border-none text-[10px] font-black uppercase text-amber-550 outline-none cursor-pointer hover:text-amber-450 w-full truncate"
                    >
                      <option value="No Project" className="bg-[#121316] text-white">No Project</option>
                      {projects.map(p => (
                        <option key={p.id} value={p.name} className="bg-[#121316] text-white">{p.name}</option>
                      ))}
                    </select>
                  </div>
                </div>

              </div>
            )}
          </div>
        </div>

        {/* MESSAGES SCREEN CONTENT CONTAINER */}
        <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 scroll-smooth-premium scrollbar-none bg-[#06070d]">
          {messages.length === 0 ? (
            <div className="max-w-xl mx-auto text-center space-y-6 py-[8vh]">
              <YaarOrb state="idle" size="sm" className="mx-auto" />
              <h3 className="text-xl font-black text-white tracking-tight font-display">
                How can I help you today?
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 pt-2">
                {STARTER_PROMPTS.map((p, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleStarterPrompt(p.prompt)}
                    className="p-4 rounded-2xl glass-card text-left transition-premium hover-lift cursor-pointer group flex flex-col gap-2"
                  >
                    <p.icon className="w-4.5 h-4.5 text-purple-400" />
                    <span className="text-xs font-bold text-slate-200 group-hover:text-white">{p.label}</span>
                    <span className="text-[10px] text-slate-500 font-medium leading-relaxed truncate-3-lines">{p.prompt}</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="max-w-3xl mx-auto space-y-6">
              {(() => {
                const latestUserIdx = messages.map((m, i) => m.role === "user" ? i : -1).reduce((a, b) => Math.max(a, b), -1);
                return messages.map((msg, index) => {
                  if (msg.role === "assistant" && msg.is_translation_card && msg.translation_data) {
                    const data = msg.translation_data;
                    return (
                      <div key={index} className="flex gap-4 items-start justify-start group animate-slide-up-fade">
                        <YaarOrb state="idle" size="sm" className="shrink-0 mt-0.5" />
                        <div className="flex flex-col gap-2 max-w-[80%] min-w-[320px]">
                          <div className="p-5 rounded-2xl border bg-slate-900/60 border-slate-800/40 text-slate-200 shadow space-y-4">
                            <div className="flex items-center justify-between border-b border-white/5 pb-2">
                              <span className="text-[10px] font-black uppercase tracking-widest text-amber-500">Translation Engine</span>
                              <span className="text-[9px] text-slate-500 font-mono">Offline Conversion</span>
                            </div>
                            
                            <div className="text-[10px] text-slate-450 italic">
                              Input Phrase: &quot;{data.sourceText}&quot;
                            </div>

                            <div className="space-y-3">
                              {/* English */}
                              <div className="p-3 rounded-xl bg-slate-950/40 border border-slate-900 flex items-center justify-between gap-3">
                                <div>
                                  <span className="text-[8px] font-extrabold uppercase tracking-wider text-slate-500 block">English</span>
                                  <span className="text-xs font-bold text-white">{data.english}</span>
                                </div>
                                <div className="flex items-center gap-1 shrink-0">
                                  <button
                                    onClick={() => handleCopyMessage(data.english)}
                                    className="p-1.5 text-slate-500 hover:text-white rounded hover:bg-slate-900 transition-colors"
                                    title="Copy"
                                  >
                                    <Copy className="w-3.5 h-3.5" />
                                  </button>
                                  <button
                                    onClick={() => toggleSpeakMessage(index + 999, data.english)}
                                    className="p-1.5 text-slate-500 hover:text-white rounded hover:bg-slate-900 transition-colors"
                                    title="Listen"
                                  >
                                    <Volume2 className="w-3.5 h-3.5" />
                                  </button>
                                  <button
                                    onClick={() => handleSaveToVault(`English Translation of "${data.sourceText}": ${data.english}`)}
                                    className="p-1.5 text-slate-500 hover:text-emerald-400 rounded hover:bg-slate-900 transition-colors"
                                    title="Save to Vault"
                                  >
                                    <Bookmark className="w-3.5 h-3.5" />
                                  </button>
                                </div>
                              </div>

                              {/* Hindi */}
                              <div className="p-3 rounded-xl bg-slate-950/40 border border-slate-900 flex items-center justify-between gap-3">
                                <div>
                                  <span className="text-[8px] font-extrabold uppercase tracking-wider text-slate-500 block">Hindi</span>
                                  <span className="text-xs font-bold text-white">{data.hindi}</span>
                                </div>
                                <div className="flex items-center gap-1 shrink-0">
                                  <button
                                    onClick={() => handleCopyMessage(data.hindi)}
                                    className="p-1.5 text-slate-500 hover:text-white rounded hover:bg-slate-900 transition-colors"
                                    title="Copy"
                                  >
                                    <Copy className="w-3.5 h-3.5" />
                                  </button>
                                  <button
                                    onClick={() => toggleSpeakMessage(index + 1000, data.hindi)}
                                    className="p-1.5 text-slate-500 hover:text-white rounded hover:bg-slate-900 transition-colors"
                                    title="Listen"
                                  >
                                    <Volume2 className="w-3.5 h-3.5" />
                                  </button>
                                  <button
                                    onClick={() => handleSaveToVault(`Hindi Translation of "${data.sourceText}": ${data.hindi}`)}
                                    className="p-1.5 text-slate-500 hover:text-emerald-400 rounded hover:bg-slate-900 transition-colors"
                                    title="Save to Vault"
                                  >
                                    <Bookmark className="w-3.5 h-3.5" />
                                  </button>
                                </div>
                              </div>

                              {/* Punjabi */}
                              <div className="p-3 rounded-xl bg-slate-950/40 border border-slate-900 flex items-center justify-between gap-3">
                                <div>
                                  <span className="text-[8px] font-extrabold uppercase tracking-wider text-slate-500 block">Punjabi</span>
                                  <span className="text-xs font-bold text-white">{data.punjabi}</span>
                                </div>
                                <div className="flex items-center gap-1 shrink-0">
                                  <button
                                    onClick={() => handleCopyMessage(data.punjabi)}
                                    className="p-1.5 text-slate-500 hover:text-white rounded hover:bg-slate-900 transition-colors"
                                    title="Copy"
                                  >
                                    <Copy className="w-3.5 h-3.5" />
                                  </button>
                                  <button
                                    onClick={() => toggleSpeakMessage(index + 1001, data.punjabi)}
                                    className="p-1.5 text-slate-500 hover:text-white rounded hover:bg-slate-900 transition-colors"
                                    title="Listen"
                                  >
                                    <Volume2 className="w-3.5 h-3.5" />
                                  </button>
                                  <button
                                    onClick={() => handleSaveToVault(`Punjabi Translation of "${data.sourceText}": ${data.punjabi}`)}
                                    className="p-1.5 text-slate-500 hover:text-emerald-400 rounded hover:bg-slate-900 transition-colors"
                                    title="Save to Vault"
                                  >
                                    <Bookmark className="w-3.5 h-3.5" />
                                  </button>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  }

                  const isUser = msg.role === "user";
                  const versions = msg.versions || [msg.content];
                  const currentIdx = msg.currentVersionIndex ?? 0;
                  const isEditing = editingMsgIndex === index;

                  return (
                    <div
                      key={index}
                      className={`flex gap-4 items-start ${isUser ? "justify-end" : "justify-start"} group animate-slide-up-fade`}
                    >
                      {/* Assistant Avatar */}
                      {!isUser && (
                        <YaarOrb state={chatLoading && index === messages.length - 1 ? "thinking" : "idle"} size="sm" className="shrink-0 mt-0.5" />
                      )}

                      {/* Chat Bubble Body */}
                      <div className="flex flex-col gap-2 max-w-[80%] min-w-[200px]">
                        
                        {/* Version pagination header for regenerated responses */}
                        {!isUser && versions.length > 1 && (
                          <div className="flex items-center gap-1.5 text-[9px] text-slate-500 font-extrabold uppercase tracking-wider pl-1">
                            <button
                              onClick={() => handleToggleVersion(index, "prev")}
                              disabled={currentIdx === 0}
                              className="hover:text-white disabled:opacity-30 cursor-pointer"
                            >
                              &lt;
                            </button>
                            <span>{currentIdx + 1} of {versions.length}</span>
                            <button
                              onClick={() => handleToggleVersion(index, "next")}
                              disabled={currentIdx === versions.length - 1}
                              className="hover:text-white disabled:opacity-30 cursor-pointer"
                            >
                              &gt;
                            </button>
                          </div>
                        )}

                        {/* Content Card Bubble */}
                        <div className={`p-4.5 rounded-2xl border text-xs leading-relaxed font-medium ${
                          isUser
                            ? "bg-amber-950/20 border-amber-900/30 text-slate-100 shadow-sm"
                            : "bg-slate-900/60 border-slate-800/40 text-slate-200 shadow"
                        }`}>
                          
                          {isEditing ? (
                            <div className="flex flex-col gap-2">
                              <textarea
                                value={editingContent}
                                onChange={(e) => setEditingContent(e.target.value)}
                                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-white outline-none min-h-[80px]"
                              />
                              <div className="flex gap-2 justify-end">
                                <button
                                  onClick={() => handleSaveEdit(index)}
                                  className="px-2.5 py-1.5 bg-amber-600 hover:bg-amber-500 text-white rounded-lg text-[10px] font-bold uppercase tracking-wider cursor-pointer"
                                >
                                  Save & Submit
                                </button>
                                <button
                                  onClick={() => setEditingMsgIndex(null)}
                                  className="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-450 hover:text-white rounded-lg text-[10px] font-bold uppercase tracking-wider cursor-pointer"
                                >
                                  Cancel
                                </button>
                              </div>
                            </div>
                          ) : (
                            <>
                              {renderContentFormatted(msg.content, msg.search_results, index)}
                              {!isUser && msg.search_results && msg.search_results.length > 0 && (
                                <div className="mt-3.5 pt-3.5 border-t border-slate-800/60 space-y-2">
                                  <div className="text-[10px] font-black uppercase tracking-wider text-slate-500 flex items-center gap-1.5 pl-0.5">
                                    <Globe className="w-3.5 h-3.5 text-emerald-500" />
                                    <span>Sources ({msg.search_results.length})</span>
                                  </div>
                                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                    {msg.search_results.map((result, rIdx) => (
                                      <div
                                        key={rIdx}
                                        id={`source-card-${index}-${rIdx + 1}`}
                                        onClick={() => window.open(result.link, "_blank", "noopener,noreferrer")}
                                        className="p-3.5 rounded-2xl bg-slate-950/40 border border-slate-850 hover:border-amber-500/30 hover:bg-amber-950/5 transition-premium text-left flex flex-col justify-between gap-2.5 cursor-pointer group"
                                      >
                                        <div className="min-w-0 space-y-1">
                                          <div className="flex items-center justify-between text-[8px] font-extrabold text-slate-500 uppercase tracking-wider">
                                            <span>
                                              [{rIdx + 1}] {result.domain || new URL(result.link).hostname.replace('www.', '')}
                                            </span>
                                            {result.date && (
                                              <span>{result.date}</span>
                                            )}
                                          </div>
                                          <h4 className="text-[11px] font-bold text-slate-300 group-hover:text-white transition-colors truncate">
                                            {result.title}
                                          </h4>
                                          <p className="text-[10px] text-slate-455 leading-relaxed line-clamp-2 font-medium">
                                            {result.snippet}
                                          </p>
                                        </div>
                                        <div className="flex items-center justify-between pt-2 border-t border-white/5 text-[9px] font-extrabold uppercase tracking-wider">
                                          <button
                                            onClick={(e) => {
                                              e.stopPropagation();
                                              navigator.clipboard.writeText(result.link);
                                              alert("Link copied!");
                                            }}
                                            className="text-slate-500 hover:text-white flex items-center gap-1 transition-colors cursor-pointer"
                                            title="Copy Source Link"
                                          >
                                            <Copy className="w-3 h-3" />
                                            <span>Copy Link</span>
                                          </button>
                                          <span className="text-amber-500 group-hover:text-amber-400 flex items-center gap-0.5">
                                            Open ↗
                                          </span>
                                        </div>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </>
                          )}
                        </div>

                        {!isUser && (
                          <div className="flex items-center gap-1.5 mt-1 px-1">
                            {msg.source === "document" || msg.source === "partial_document" ? (
                              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-blue-950/30 border border-blue-900/30 text-[8px] font-black uppercase tracking-wider text-blue-400 animate-fade-in">
                                📄 From Document
                              </span>
                            ) : msg.source === "web" ? (
                              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-emerald-950/30 border border-emerald-900/30 text-[8px] font-black uppercase tracking-wider text-emerald-400 animate-fade-in">
                                🌐 From Web Search
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-purple-950/30 border border-purple-900/30 text-[8px] font-black uppercase tracking-wider text-purple-400 animate-fade-in">
                                🧠 General Knowledge
                              </span>
                            )}
                          </div>
                        )}

                      {/* Bubble Action Controls */}
                      {!isEditing && (
                        <div className="flex flex-wrap items-center gap-3.5 mt-1.5 px-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          
                          {/* Translate control */}
                          {!isUser && (
                            <div className="flex items-center gap-1.5">
                              <select
                                value={msg.selected_translation_lang || "Original"}
                                onChange={(e) => handleTranslateMessage(index, e.target.value)}
                                disabled={translatingMessageIndex !== null}
                                className="bg-slate-950 border border-slate-800 rounded-lg text-[9px] font-bold px-1.5 py-0.5 text-slate-450 outline-none cursor-pointer"
                              >
                                <option value="Original">Original</option>
                                {INDIAN_LANGUAGES.map(lang => (
                                  <option key={lang} value={lang}>{lang}</option>
                                ))}
                              </select>
                              {translatingMessageIndex === index && (
                                <RefreshCw className="w-3.5 h-3.5 animate-spin text-amber-500" />
                              )}
                            </div>
                          )}

                          {/* Speak audio */}
                          <button
                            onClick={() => toggleSpeakMessage(index, msg.content)}
                            className={`text-[10px] font-bold flex items-center gap-1 transition-colors ${speakingMessageIndex === index ? "text-amber-500" : "text-slate-500 hover:text-white"}`}
                          >
                            <Volume2 className="w-3 h-3" />
                            <span>{speakingMessageIndex === index ? "Stop" : "Listen"}</span>
                          </button>

                          {/* Save to Vault second brain */}
                          {!isUser && (
                            <button
                              onClick={() => handleSaveToVault(msg.content)}
                              className="text-[10px] font-bold text-slate-500 hover:text-emerald-400 flex items-center gap-1 transition-colors"
                              title="Save response to Vault second brain"
                            >
                              <Bookmark className="w-3 h-3" />
                              <span>Vault</span>
                            </button>
                          )}

                          {/* Edit / Delete / Copy Actions */}
                          {isUser ? (
                            <>
                              {index === latestUserIdx && (
                                <button
                                  onClick={() => handleStartEdit(index, msg.content)}
                                  className="text-[10px] font-bold text-slate-500 hover:text-amber-500 flex items-center gap-1 transition-colors"
                                >
                                  <Edit2 className="w-3 h-3" /> Edit
                                </button>
                              )}
                              <button
                                onClick={() => handleDeleteMessage(index)}
                                className="text-[10px] font-bold text-slate-500 hover:text-rose-450 flex items-center gap-1 transition-colors"
                              >
                                <Trash2 className="w-3 h-3" /> Delete
                              </button>
                            </>
                          ) : (
                            <>
                              <button
                                onClick={() => handleRegenerate(index)}
                                className="text-[10px] font-bold text-slate-500 hover:text-amber-500 flex items-center gap-1 transition-colors"
                              >
                                <RefreshCw className="w-3 h-3" /> Regenerate
                              </button>
                              <button
                                onClick={() => handleCopyMessage(msg.content)}
                                className="text-[10px] font-bold text-slate-500 hover:text-white flex items-center gap-1 transition-colors"
                              >
                                <Copy className="w-3 h-3" /> Copy
                              </button>
                              <button
                                onClick={() => handleShareMessage(msg.content)}
                                className="text-[10px] font-bold text-slate-500 hover:text-white flex items-center gap-1 transition-colors"
                              >
                                <Share2 className="w-3 h-3" /> Share
                              </button>
                            </>
                          )}

                        </div>
                      )}

                    </div>

                    {/* User Avatar */}
                    {isUser && (
                      <div className="w-8 h-8 rounded-xl bg-amber-950/20 border border-amber-900/30 flex items-center justify-center text-amber-500 shrink-0">
                        <Smile className="w-4.5 h-4.5" />
                      </div>
                    )}
                  </div>
                );
              });
            })()}              {/* Chat generation loader */}
              {chatLoading && (
                <div className="flex items-start gap-4 justify-start animate-pulse">
                  <YaarOrb state="thinking" size="sm" className="shrink-0 mt-0.5" />
                  <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800/40 flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-bounce" style={{ animationDelay: "0ms" }}></span>
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-bounce" style={{ animationDelay: "150ms" }}></span>
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-bounce" style={{ animationDelay: "300ms" }}></span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* INPUT FORM PINS TO BOTTOM */}
        <div className="p-4 bg-[#06070d]/80 backdrop-blur-md border-t border-slate-900 shrink-0">
          <div className="max-w-3xl mx-auto flex flex-col gap-3">
            
            {/* Quick Actions */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2.5 px-1.5">
              <div className="flex items-center gap-2 overflow-x-auto w-full sm:w-auto">
                <button
                  onClick={() => setEnableSearch(!enableSearch)}
                  className={`py-1 px-2.5 rounded-lg border text-[10px] font-black uppercase tracking-wider flex items-center gap-1.5 transition-premium cursor-pointer ${
                    enableSearch
                      ? "bg-amber-950/30 border-amber-500/30 text-amber-500"
                      : "bg-slate-900/40 border-slate-800/60 text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <Search className="w-3 h-3" />
                  <span>Search Web</span>
                  {enableSearch && (
                    <X className="w-3 h-3 ml-1 hover:text-rose-500 transition-colors" />
                  )}
                </button>

                <button
                  onClick={handleFixGrammar}
                  disabled={!inputText.trim() || grammarFixing}
                  className="py-1 px-2.5 rounded-lg border border-slate-800 bg-slate-900/40 text-[10px] font-black uppercase tracking-wider text-slate-400 hover:text-amber-500 hover:border-amber-500/30 transition-premium flex items-center gap-1.5 disabled:opacity-40 cursor-pointer"
                >
                  {grammarFixing ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5 text-amber-500" />}
                  <span>Fix Grammar</span>
                </button>
              </div>

              {/* Upload file triggers */}
              <div className="flex items-center gap-2">
                {selectedDoc ? (
                  <div className="flex items-center gap-1.5 text-[10px] bg-slate-900/80 border border-slate-800 rounded-lg px-2.5 py-1">
                    <span className="text-slate-400 truncate max-w-[100px]">📄 {selectedDoc.filename}</span>
                    <button onClick={handleDetachDoc} className="text-slate-500 hover:text-rose-400 font-bold shrink-0">
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    disabled={uploading}
                    className="py-1 px-2.5 rounded-lg border border-slate-800 bg-slate-900/40 text-[10px] font-black uppercase tracking-wider text-slate-400 hover:text-amber-500 hover:border-amber-500/30 transition-premium flex items-center gap-1.5 disabled:opacity-40 cursor-pointer"
                  >
                    {uploading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Paperclip className="w-3.5 h-3.5" />}
                    <span>Attach PDF</span>
                  </button>
                )}
                <input ref={fileInputRef} type="file" accept=".pdf" onChange={onFileChange} className="hidden" />
              </div>
            </div>

            {/* Main prompt text inputs */}
            <div className="relative flex items-center bg-slate-900/50 border border-slate-800/80 rounded-2xl px-4 py-3 shadow-inner">
              <input
                type="text"
                value={inputText}
                onChange={e => setInputText(e.target.value)}
                onKeyDown={e => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                placeholder="Ask Yaar anything..."
                className="w-full bg-transparent text-white text-xs placeholder-slate-500 outline-none pr-14"
              />
              <div className="absolute right-2 flex items-center gap-1.5">
                <button
                  onClick={toggleListening}
                  className={`p-2 rounded-xl transition-premium cursor-pointer ${isListening ? "bg-rose-950 text-rose-400 border border-rose-800/40" : "text-slate-400 hover:text-white"}`}
                  title="Voice Input"
                >
                  <Mic className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleSend()}
                  disabled={!inputText.trim() || chatLoading}
                  className="p-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white transition-premium cursor-pointer disabled:opacity-40"
                  title="Send Query"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Bottom trust system banner */}
            <div className="text-center pt-1.5">
              <span className="text-[9px] font-black uppercase tracking-widest text-slate-600">
                🔒 Private by Default  •  Training requires explicit user consent.  •  🗑 Delete Anytime
              </span>
            </div>

          </div>
        </div>

      </div>

    </div>
  );
}
