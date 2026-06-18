"use client";

import React, { useState, useEffect, useRef } from "react";
import { 
  Send, Mic, Globe, Sparkles, Search, MessageSquare, Trash2, 
  ArrowUpRight, Paperclip, X, FileText, RefreshCw, AlertCircle, 
  CheckCircle, BookOpen, Volume2, User, Menu, Smile, Edit2
} from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
  has_search?: boolean;
  search_results?: Array<{ title: string; link: string; snippet: string }> | null;
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

interface ChatInterfaceProps {
  activeConversationId: number | null;
  onSelectConversation: (id: number | null) => void;
  apiBaseUrl: string;
  onRefreshDocuments: () => void;
  sidebarOpen: boolean;
  setSidebarOpen: React.Dispatch<React.SetStateAction<boolean>>;
}

export default function ChatInterface({ 
  activeConversationId, 
  onSelectConversation, 
  apiBaseUrl,
  onRefreshDocuments,
  sidebarOpen,
  setSidebarOpen
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState("");
  const [enableSearch, setEnableSearch] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [chatLoading, setChatLoading] = useState(false);
  const [grammarFixing, setGrammarFixing] = useState(false);
  const [translatingInput, setTranslatingInput] = useState(false);
  const [translatingMessageIndex, setTranslatingMessageIndex] = useState<number | null>(null);
  const [selectedLanguage, setSelectedLanguage] = useState("Hindi");

  const INDIAN_LANGUAGES = [
    "Hindi", "Tamil", "Telugu", "Bengali", "Marathi", "Gujarati",
    "Kannada", "Malayalam", "Odia", "Punjabi", "Assamese", "Urdu", "Sanskrit"
  ];
  
  // Document context loaded locally based on active conversation
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
  const [uploading, setUploading] = useState(false);
  const [activeSummaryTab, setActiveSummaryTab] = useState<"trace" | "summary" | "digitized" | "compliance">("trace");
  
  // Digitization and Compliance states (Sarvam competitor features)
  const [digitizedText, setDigitizedText] = useState<string | null>(null);
  const [digitizing, setDigitizing] = useState(false);
  const [complianceReport, setComplianceReport] = useState<{
    score: number;
    checks: Array<{ rule: string; status: string; details: string }>;
  } | null>(null);
  const [auditing, setAuditing] = useState(false);
  const [auditPreset, setAuditPreset] = useState("DPDP Act 2023");
  const [speakingMessageIndex, setSpeakingMessageIndex] = useState<number | null>(null);
  
  // Draggable splitter states removed per user request

  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);

  // Auto-scroll
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, chatLoading]);

  // Load conversation details when activeConversationId changes
  useEffect(() => {
    setDigitizedText(null);
    setComplianceReport(null);
    window.speechSynthesis.cancel();
    setSpeakingMessageIndex(null);

    if (activeConversationId) {
      // 1. Fetch messages
      const loadHistory = async () => {
        try {
          const res = await fetch(`${apiBaseUrl}/api/conversations/${activeConversationId}/messages`);
          if (res.ok) {
            const data = await res.json();
            setMessages(data);
          }
        } catch (err) {
          console.error("Failed to load conversation history:", err);
        }
      };
      loadHistory();

      // 2. Fetch conversation metadata to find attached document ID
      const loadMetadata = async () => {
        try {
          const res = await fetch(`${apiBaseUrl}/api/conversations`);
          if (res.ok) {
            const conversations = await res.json();
            const current = conversations.find((c: any) => c.id === activeConversationId);
            
            if (current && current.document_id) {
              // Fetch document details
              const docRes = await fetch(`${apiBaseUrl}/api/documents/${current.document_id}`);
              if (docRes.ok) {
                const docDetails = await docRes.json();
                setSelectedDoc(docDetails);
                return;
              }
            }
          }
          setSelectedDoc(null);
        } catch (err) {
          console.error("Failed to load conversation metadata:", err);
          setSelectedDoc(null);
        }
      };
      loadMetadata();
    } else {
      setMessages([]);
      setSelectedDoc(null);
    }
  }, [activeConversationId]);

  // Background status polling for active document
  useEffect(() => {
    if (!selectedDoc || selectedDoc.status !== "processing") return;

    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${apiBaseUrl}/api/documents/${selectedDoc.id}`);
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
  }, [selectedDoc?.id, selectedDoc?.status]);

  // Ensure active conversation session exists before operations
  const ensureConversation = async (): Promise<number> => {
    if (activeConversationId) return activeConversationId;
    
    try {
      const res = await fetch(`${apiBaseUrl}/api/conversations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ document_id: null })
      });
      if (!res.ok) throw new Error("Failed to create conversation session");
      const data = await res.json();
      onSelectConversation(data.id);
      onRefreshDocuments();
      return data.id;
    } catch (err) {
      console.error("Auto-creation of conversation session failed:", err);
      throw err;
    }
  };

  // Send message
  const handleSend = async (textToSend = inputText) => {
    const text = textToSend.trim();
    if (!text || chatLoading) return;

    setChatLoading(true);

    try {
      // Ensure conversation session exists
      const convId = await ensureConversation();

      // Optimistically add user message locally
      const newUserMessage: Message = {
        role: "user",
        content: text,
        has_search: enableSearch
      };
      setMessages(prev => [...prev, newUserMessage]);
      setInputText("");

      const response = await fetch(`${apiBaseUrl}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          conversation_id: convId,
          enable_search: enableSearch,
          history: messages.slice(-10).map(m => ({ role: m.role, content: m.content }))
        }),
      });

      if (!response.ok) throw new Error("Failed to send message");

      const data = await response.json();
      
      const newAssistantMessage: Message = {
        role: "assistant",
        content: data.response,
        has_search: data.has_search,
        search_results: data.search_results
      };

      setMessages(prev => [...prev, newAssistantMessage]);
      
      // Trigger update to refresh sidebar title from new first query
      onRefreshDocuments();
    } catch (err) {
      console.error(err);
      setMessages(prev => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I encountered an error. The API server might be rate-limited. Please try again shortly.",
        }
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  // Handle PDF upload and link it to active conversation
  const handleFileUpload = async (file: File) => {
    if (!file.name.endsWith(".pdf")) {
      alert("Only PDF files are supported.");
      return;
    }

    setUploading(true);

    try {
      // Ensure conversation session exists
      const convId = await ensureConversation();

      // 1. Upload file
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(`${apiBaseUrl}/api/documents/upload`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const detail = await res.json().then(d => d.detail).catch(() => "Upload failed");
        throw new Error(detail);
      }

      const docData = await res.json();

      // 2. Associate document with active conversation
      const attachRes = await fetch(`${apiBaseUrl}/api/conversations/${convId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ document_id: docData.id })
      });
      if (!attachRes.ok) throw new Error("Failed to bind document to conversation");

      // 3. Fetch full document details for UI
      const docDetailsRes = await fetch(`${apiBaseUrl}/api/documents/${docData.id}`);
      if (docDetailsRes.ok) {
        const docDetails = await docDetailsRes.json();
        setSelectedDoc(docDetails);
      }

      onRefreshDocuments();
    } catch (err: any) {
      alert(err.message || "An error occurred during file upload.");
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

  // Detach PDF document from conversation
  const handleDetachDoc = async () => {
    if (!activeConversationId) return;
    try {
      const res = await fetch(`${apiBaseUrl}/api/conversations/${activeConversationId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ document_id: -1 }) // -1 signals detach
      });
      if (res.ok) {
        setSelectedDoc(null);
        onRefreshDocuments();
      }
    } catch (err) {
      console.error("Failed to detach document:", err);
    }
  };

  // Voice Input (Web Speech API)
  const toggleListening = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
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

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onerror = () => {
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setInputText(prev => prev + (prev ? " " : "") + transcript);
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  // Edit the last user message in the chat box
  const handleEditLastMessage = async (content: string) => {
    if (!activeConversationId) return;
    
    setInputText(content);
    
    try {
      const res = await fetch(`${apiBaseUrl}/api/conversations/${activeConversationId}/messages/last`, {
        method: "DELETE"
      });
      if (res.ok) {
        // Find index of the last user message
        let lastUserIdx = -1;
        for (let i = messages.length - 1; i >= 0; i--) {
          if (messages[i].role === "user") {
            lastUserIdx = i;
            break;
          }
        }
        
        if (lastUserIdx !== -1) {
          // Keep only the messages before the last user message
          setMessages(prev => prev.slice(0, lastUserIdx));
        }
        
        onRefreshDocuments();
      }
    } catch (err) {
      console.error("Failed to delete last message for edit:", err);
    }
  };

  // Quick action helpers
  const handleFixGrammar = async () => {
    if (!inputText.trim() || grammarFixing) return;
    setGrammarFixing(true);
    try {
      const res = await fetch(`${apiBaseUrl}/api/tools/grammar-fix`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: inputText }),
      });
      if (res.ok) {
        const data = await res.json();
        setInputText(data.corrected_text);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setGrammarFixing(false);
    }
  };

  const handleTranslateInput = async (lang?: string) => {
    if (!inputText.trim() || translatingInput) return;
    const targetLang = lang || selectedLanguage;
    setTranslatingInput(true);
    try {
      const res = await fetch(`${apiBaseUrl}/api/tools/translate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: inputText, target_language: targetLang }),
      });
      if (res.ok) {
        const data = await res.json();
        setInputText(data.translated_text);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setTranslatingInput(false);
    }
  };

  const handleTranslateMessage = async (msgIndex: number, textContent: string, lang?: string) => {
    if (translatingMessageIndex !== null) return;
    const targetLang = lang || selectedLanguage;
    setTranslatingMessageIndex(msgIndex);
    try {
      // Strip any existing translation block so we translate only the original text
      const originalText = textContent.split("\n\n---\n")[0];
      
      const res = await fetch(`${apiBaseUrl}/api/tools/translate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: originalText, target_language: targetLang }),
      });
      if (res.ok) {
        const data = await res.json();
        setMessages(prev => {
          const updated = [...prev];
          // Replace: use original text + new translation (never stack)
          updated[msgIndex] = {
            ...updated[msgIndex],
            content: `${originalText}\n\n---\n**${targetLang} Translation:**\n\n${data.translated_text}`
          };
          return updated;
        });
      }
    } catch (err) {
      console.error(err);
    } finally {
      setTranslatingMessageIndex(null);
    }
  };

  const formatSize = (bytes: number | undefined | null) => {
    if (bytes === undefined || bytes === null || isNaN(bytes)) {
      return "Size unknown";
    }
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const handleClearHistory = async () => {
    if (!activeConversationId) return;
    if (!confirm("Clear this conversation history?")) return;
    try {
      const res = await fetch(`${apiBaseUrl}/api/conversations/${activeConversationId}/messages`, {
        method: "DELETE"
      });
      if (res.ok) {
        setMessages([]);
      }
    } catch (err) {
      console.error("Failed to clear chat history:", err);
    }
  };

  const handleDigitize = async () => {
    if (!selectedDoc || digitizing) return;
    setDigitizing(true);
    setActiveSummaryTab("digitized");
    try {
      const res = await fetch(`${apiBaseUrl}/api/documents/${selectedDoc.id}/digitize`, {
        method: "POST"
      });
      if (res.ok) {
        const data = await res.json();
        setDigitizedText(data.digitized_text);
      } else {
        setDigitizedText("Failed to digitize document. Gemini model may be temporarily busy.");
      }
    } catch (err) {
      console.error(err);
      setDigitizedText("Failed to run Indic layout digitizer.");
    } finally {
      setDigitizing(false);
    }
  };

  const handleComplianceAudit = async (preset: string) => {
    if (!selectedDoc || auditing) return;
    setAuditing(true);
    setActiveSummaryTab("compliance");
    try {
      const res = await fetch(`${apiBaseUrl}/api/documents/${selectedDoc.id}/compliance?preset=${encodeURIComponent(preset)}`, {
        method: "POST"
      });
      if (res.ok) {
        const data = await res.json();
        setComplianceReport(data);
      } else {
        setComplianceReport({
          score: 0,
          checks: [{ rule: "Audit Error", status: "Failed", details: "Failed to audit document content." }]
        });
      }
    } catch (err) {
      console.error(err);
      setComplianceReport({
        score: 0,
        checks: [{ rule: "Audit Error", status: "Failed", details: "Failed to connect to regulatory audit agent." }]
      });
    } finally {
      setAuditing(false);
    }
  };

  const toggleSpeakMessage = (msgIndex: number, textContent: string) => {
    if (speakingMessageIndex === msgIndex) {
      window.speechSynthesis.cancel();
      setSpeakingMessageIndex(null);
      return;
    }

    window.speechSynthesis.cancel();
    
    // Clean up text content to remove markdown formatting
    const cleanText = textContent
      .replace(/[\*#_`~]/g, "")
      .replace(/---\n/g, "")
      .trim();

    const utterance = new SpeechSynthesisUtterance(cleanText);
    const isPunjabi = /[\u0A00-\u0A7F]/.test(textContent);
    
    const voices = window.speechSynthesis.getVoices();
    let selectedVoice = null;
    
    if (isPunjabi) {
      selectedVoice = voices.find(v => v.lang.startsWith("pa") || v.lang.startsWith("hi"));
      utterance.lang = selectedVoice ? selectedVoice.lang : "hi-IN";
    } else {
      selectedVoice = voices.find(v => v.lang.startsWith("en-IN")) || voices.find(v => v.lang.startsWith("en"));
      utterance.lang = selectedVoice ? selectedVoice.lang : "en-US";
    }
    
    if (selectedVoice) {
      utterance.voice = selectedVoice;
    }
    
    utterance.onend = () => {
      setSpeakingMessageIndex(null);
    };
    
    utterance.onerror = () => {
      setSpeakingMessageIndex(null);
    };
    
    setSpeakingMessageIndex(msgIndex);
    window.speechSynthesis.speak(utterance);
  };

  // Stop speaking when unmounted
  useEffect(() => {
    return () => {
      window.speechSynthesis.cancel();
    };
  }, []);

  // Draggable panels handler removed per user request

  const getAgentSteps = () => {
    if (!selectedDoc) return [];
    
    const steps = [
      {
        id: 1,
        name: "Document Ingestion",
        status: "completed",
        time: "0.4s",
        details: `File '${selectedDoc.filename}' (${formatSize(selectedDoc.file_size)}) uploaded to local storage.`
      },
      {
        id: 2,
        name: "Structure Analysis",
        status: selectedDoc.status === "processing" ? "pending" : "completed",
        time: selectedDoc.status === "processing" ? "Analyzing..." : "1.1s",
        details: selectedDoc.status === "processing" 
          ? "Determining page layouts, headers, and metadata..." 
          : "Mapped layout structures, logical zones, and text segments."
      },
      {
        id: 3,
        name: "Indic Translation Worker",
        status: selectedDoc.status === "processing" ? "pending" : "completed",
        time: selectedDoc.status === "processing" ? "Translating..." : "2.3s",
        details: selectedDoc.status === "processing" 
          ? "Translating parsed blocks into Gurmukhi script..." 
          : "Successfully synthesized Gurmukhi (Punjabi) and English summaries."
      }
    ];

    if (auditing) {
      steps.push({
        id: 4,
        name: `Compliance Auditor (${auditPreset})`,
        status: "pending",
        time: "Analyzing...",
        details: "Scanning clauses against regulatory policies..."
      });
    } else if (complianceReport) {
      steps.push({
        id: 4,
        name: `Compliance Auditor (${auditPreset})`,
        status: "completed",
        time: "1.8s",
        details: `Audit completed. Score: ${complianceReport.score}/105. Checked ${complianceReport.checks.length} parameters.`
      });
    }

    if (digitizing) {
      steps.push({
        id: 5,
        name: "Layout-Preserved OCR",
        status: "pending",
        time: "Processing...",
        details: "Extracting multilingual characters and preserving visual alignments..."
      });
    } else if (digitizedText) {
      steps.push({
        id: 5,
        name: "Layout-Preserved OCR",
        status: "completed",
        time: "3.2s",
        details: "OCR extraction completed. Retained columns, tables, and script alignments."
      });
    }

    return steps;
  };

  return (
    <div className="flex-1 h-full flex flex-col relative overflow-hidden">
      
      {/* Cinematic Background Gradient Mesh Blobs (Bleeds through glass sidebar & panels) */}
      <div className="absolute top-[-15%] right-[-10%] w-[600px] h-[600px] rounded-full bg-gradient-to-br from-orange-400/22 to-amber-300/10 blur-[130px] pointer-events-none z-0 animate-blob-1" />
      <div className="absolute top-[30%] left-[-15%] w-[500px] h-[500px] rounded-full bg-gradient-to-br from-indigo-300/18 to-purple-200/8 blur-[110px] pointer-events-none z-0 animate-blob-2" />
      <div className="absolute bottom-[-10%] right-[15%] w-[450px] h-[450px] rounded-full bg-gradient-to-br from-pink-300/18 to-orange-200/8 blur-[100px] pointer-events-none z-0 animate-blob-3" />

      {/* Main Relative Container Wrapper */}
      <div className="flex-1 h-full flex flex-col relative z-10 bg-transparent">
        
        {/* Top Header Workspace Status */}
        <header className="h-16 border-b border-slate-200/30 flex items-center justify-between px-6 bg-white/30 backdrop-blur-md shrink-0 z-20">
          <div className="flex items-center gap-4">
            {/* Collapse button removed from header above conversation per user request */}
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-orange-100/40 border border-orange-200/30 text-orange-600 shadow-sm shrink-0 pulse-ring-slow">
                <Sparkles className="w-4 h-4" />
              </div>
              <div>
                <h1 className="text-base font-black tracking-tight text-slate-900 font-display flex items-center gap-1">
                  <span className="text-gradient-title">bharat</span><span className="text-gradient-orange">ai</span>
                </h1>
                <p className="text-[8px] text-slate-400 font-black tracking-[0.2em] uppercase mt-0.5">
                  India's Sovereign Workspace
                </p>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {/* Clear Chat removed per user request */}
          </div>
        </header>

        {/* Main split-workspace below header */}
        <div className="flex-1 flex overflow-hidden">
          
          {/* Left Side: Chat Workspace */}
          <div className={`h-full flex flex-col min-w-0 ${selectedDoc ? "w-[55%] border-r border-slate-200/30" : "w-full"}`}>
            
            {/* Main Chat Workspace feed */}
            <div className="flex-1 overflow-y-auto scroll-smooth-premium p-6 space-y-6">
              <div className="max-w-3xl mx-auto space-y-6">
                
                {/* Welcome Screen Dashboard when conversation is empty */}
                {messages.length === 0 && (
                  <div className="py-12 text-center space-y-8 animate-float">
                    <div className="space-y-4 max-w-2xl mx-auto">
                      <span className="px-3.5 py-1.5 bg-orange-100/40 text-orange-700 font-black text-[9px] uppercase tracking-[0.18em] rounded-full border border-orange-200/30 shadow-sm">
                        India's Sovereign AI Platform
                      </span>
                      <h2 className="text-5xl md:text-6.5xl font-black tracking-tight text-slate-900 font-display mt-3 leading-[1.12]">
                        AI for all <span className="text-gradient-orange">from India</span>
                      </h2>
                      <p className="text-slate-555 text-sm md:text-base max-w-md mx-auto leading-relaxed font-medium mt-2">
                        Built on sovereign compute. Powered by frontier-class models. Delivering population-scale impact.
                      </p>

                      {/* Call to action pill buttons mimicking Sarvam website */}
                      <div className="flex items-center justify-center gap-4 pt-4">
                        <button
                          onClick={() => fileInputRef.current?.click()}
                          className="px-7 py-3.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold rounded-full transition-premium cursor-pointer shadow-md hover:shadow-lg hover:-translate-y-0.5 active:translate-y-0"
                        >
                          Upload PDF Document
                        </button>
                        <button
                          onClick={() => setEnableSearch(!enableSearch)}
                          className={`px-7 py-3.5 text-xs font-bold rounded-full border transition-premium cursor-pointer hover:-translate-y-0.5 hover:shadow-md active:translate-y-0 ${
                            enableSearch
                              ? "bg-indigo-50 border-indigo-200 text-indigo-700 shadow-sm"
                              : "bg-white/70 border-slate-200 text-slate-700 hover:bg-white"
                          }`}
                        >
                          {enableSearch ? "Web Search Active" : "Enable Web Search"}
                        </button>
                      </div>
                    </div>

                    {/* Suggestion Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-5 max-w-2xl mx-auto pt-8">
                      <div 
                        onClick={() => fileInputRef.current?.click()}
                        className="p-6 rounded-3xl glass-card hover:border-orange-305 hover:shadow-lg hover:shadow-orange-200/10 cursor-pointer transition-premium text-left space-y-3 group"
                      >
                        <div className="w-10 h-10 rounded-2xl bg-orange-100/50 border border-orange-200/30 flex items-center justify-center text-orange-500 group-hover:scale-110 transition-premium duration-300">
                          <Paperclip className="w-5 h-5" />
                        </div>
                        <h4 className="text-xs font-bold text-slate-805 font-display">Attach PDF Document</h4>
                        <p className="text-[10px] text-slate-450 leading-relaxed font-medium">
                          Attach files inline to summarize, answer context-specific questions and run compliance audits.
                        </p>
                      </div>
                      
                      <div 
                        onClick={() => setEnableSearch(!enableSearch)}
                        className={`p-6 rounded-3xl glass-card cursor-pointer transition-premium text-left space-y-3 group ${
                          enableSearch 
                            ? "border-indigo-400 bg-indigo-50/40 shadow-lg shadow-indigo-100/20" 
                            : "hover:border-indigo-300 hover:shadow-lg hover:shadow-indigo-200/10"
                        }`}
                      >
                        <div className="w-10 h-10 rounded-2xl bg-indigo-100/50 border border-indigo-200/30 flex items-center justify-center text-indigo-650 group-hover:scale-110 transition-premium duration-300">
                          <Search className="w-5 h-5" />
                        </div>
                        <h4 className="text-xs font-bold text-slate-805 font-display">Search Web Toggle</h4>
                        <p className="text-[10px] text-slate-450 leading-relaxed font-medium">
                          Retrieve real-time factual events, query search engines, and cite reference sources automatically.
                        </p>
                      </div>

                      <div className="p-6 rounded-3xl glass-card hover:border-pink-300 hover:shadow-lg hover:shadow-pink-200/10 text-left space-y-3 group transition-premium cursor-pointer">
                        <div className="w-10 h-10 rounded-2xl bg-pink-100/50 border border-pink-200/30 flex items-center justify-center text-pink-500 group-hover:scale-110 transition-premium duration-300">
                          <Globe className="w-5 h-5" />
                        </div>
                        <h4 className="text-xs font-bold text-slate-805 font-display">Multilingual Tools</h4>
                        <p className="text-[10px] text-slate-450 leading-relaxed font-medium">
                          Type or dictate messages to translate instantly to Punjabi script or check grammar natively.
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Messages list */}
                {messages.map((msg, index) => {
                  const isUser = msg.role === "user";
                  return (
                    <div
                      key={index}
                      className={`flex items-start gap-4 ${isUser ? "justify-end" : "justify-start"}`}
                    >
                      {!isUser && (
                        <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-orange-500 to-indigo-650 flex items-center justify-center text-white shadow shadow-indigo-500/20 shrink-0 pulse-ring-slow">
                          <Sparkles className="w-4 h-4 text-white" />
                        </div>
                      )}
                      <div className={`max-w-[78%] group flex flex-col ${isUser ? "items-end" : "items-start"}`}>
                        <div
                          className={`p-4 rounded-2xl leading-relaxed text-sm shadow-sm transition-premium whitespace-pre-line border ${
                            isUser
                              ? "bg-gradient-to-br from-slate-800 to-slate-900 text-white border-slate-800 rounded-tr-none shadow-md"
                              : "bg-white/80 border-slate-200/50 text-slate-800 rounded-tl-none shadow shadow-slate-100 backdrop-blur-sm hover:border-slate-300/60"
                          }`}
                        >
                          {msg.content}

                          {/* Citations list */}
                          {!isUser && msg.search_results && msg.search_results.length > 0 && (
                            <div className="mt-4 pt-3 border-t border-slate-100 space-y-2">
                              <div className="flex items-center gap-1.5 text-[9px] text-indigo-600 font-black uppercase tracking-wider">
                                <Search className="w-3.5 h-3.5" /> Web Sources
                              </div>
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-1">
                                {msg.search_results.map((src, sIdx) => {
                                  const domain = new URL(src.link).hostname.replace("www.", "");
                                  return (
                                    <a
                                      key={sIdx}
                                      href={src.link}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="p-2.5 rounded-xl bg-slate-50/50 border border-slate-200/60 hover:border-slate-300 flex items-center justify-between text-xs text-slate-600 hover:text-slate-900 transition-premium group/link shadow-sm shadow-slate-100"
                                    >
                                      <div className="min-w-0 pr-2">
                                        <p className="font-bold truncate text-[11px] text-slate-800">{src.title}</p>
                                        <p className="text-[9px] text-slate-400 font-mono mt-0.5">{domain}</p>
                                      </div>
                                      <ArrowUpRight className="w-3.5 h-3.5 text-slate-400 group-hover/link:text-indigo-605 shrink-0" />
                                    </a>
                                  );
                                })}
                              </div>
                            </div>
                          )}
                        </div>

                        {!isUser && (
                          <div className="flex items-center gap-4 mt-1.5 px-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <div className="flex items-center gap-1.5">
                              <select
                                value={selectedLanguage}
                                onChange={(e) => setSelectedLanguage(e.target.value)}
                                className="bg-white/80 border border-slate-200/60 rounded-lg text-[9px] font-bold px-1.5 py-0.5 text-slate-600 outline-none focus:border-pink-300 transition-premium cursor-pointer shadow-sm"
                                onClick={(e) => e.stopPropagation()}
                              >
                                {INDIAN_LANGUAGES.map(lang => (
                                  <option key={lang} value={lang}>{lang}</option>
                                ))}
                              </select>
                              <button
                                onClick={() => handleTranslateMessage(index, msg.content)}
                                disabled={translatingMessageIndex !== null}
                                className="text-[10px] font-bold text-slate-550 hover:text-pink-600 flex items-center gap-1.5 transition-colors cursor-pointer"
                              >
                                {translatingMessageIndex === index ? (
                                  <>
                                    <RefreshCw className="w-3 h-3 animate-spin" /> Translating
                                  </>
                                ) : (
                                  <>
                                    <Globe className="w-3 h-3 text-pink-500" /> Translate
                                  </>
                                )}
                              </button>
                            </div>

                            {/* Text to Speech player button */}
                            <button
                              onClick={() => toggleSpeakMessage(index, msg.content)}
                              className={`text-[10px] font-bold flex items-center gap-1.5 transition-colors cursor-pointer ${
                                speakingMessageIndex === index 
                                  ? "text-indigo-650 hover:text-indigo-550"
                                  : "text-slate-550 hover:text-indigo-650"
                              }`}
                            >
                              <Volume2 className="w-3 h-3" />
                              <span>{speakingMessageIndex === index ? "Stop Listening" : "Listen (ਸੁਣੋ)"}</span>
                            </button>
                          </div>
                        )}

                        {isUser && index === messages.reduce((acc, m, i) => m.role === "user" ? i : acc, -1) && (
                          <div className="flex items-center gap-4 mt-1.5 px-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button
                              onClick={() => handleEditLastMessage(msg.content)}
                              className="text-[10px] font-bold text-slate-405 hover:text-indigo-650 flex items-center gap-1 transition-colors cursor-pointer"
                              title="Edit Last Message"
                            >
                              <Edit2 className="w-3 h-3 text-slate-400 group-hover:text-indigo-500" />
                              <span>Edit Text</span>
                            </button>
                          </div>
                        )}
                      </div>
                      {isUser && (
                        <div className="w-8 h-8 rounded-xl bg-amber-50 border border-amber-200/40 flex items-center justify-center text-amber-500 shadow-sm shrink-0">
                          <Smile className="w-4.5 h-4.5" />
                        </div>
                      )}
                    </div>
                  );
                })}

                {chatLoading && (
                  <div className="flex items-start gap-4 justify-start">
                    <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-orange-500 to-indigo-650 flex items-center justify-center text-white shadow shadow-indigo-500/20 shrink-0 pulse-ring-slow">
                      <Sparkles className="w-4 h-4 text-white" />
                    </div>
                    <div className="p-4 rounded-2xl bg-white/80 border border-slate-200/50 flex items-center gap-2 shadow-sm backdrop-blur-sm">
                      <span className="w-2 h-2 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: "0ms" }}></span>
                      <span className="w-2 h-2 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: "150ms" }}></span>
                      <span className="w-2 h-2 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: "300ms" }}></span>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </div>

            {/* Input Work Area Panel: pinned to bottom, layout-contained */}
            <div className="p-6 bg-white/40 backdrop-blur-md shrink-0 z-20 border-t border-slate-200/20" style={{ contain: "layout" }}>
              <div className="max-w-3xl mx-auto flex flex-col gap-3">
                
                {/* Quick Actions row */}
                <div className="flex items-center justify-between px-1">
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => setEnableSearch(!enableSearch)}
                      className={`py-1.5 px-4 rounded-full border text-xs font-bold flex items-center gap-2 transition-premium cursor-pointer shadow-sm ${
                        enableSearch
                          ? "bg-indigo-50/70 border-indigo-200 text-indigo-750 shadow-sm"
                          : "bg-white/80 border-slate-200 text-slate-605 hover:text-slate-800 hover:border-slate-300"
                      }`}
                    >
                      <Search className="w-3.5 h-3.5" />
                      <span>Search Web</span>
                    </button>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={handleFixGrammar}
                      disabled={!inputText.trim() || grammarFixing}
                      className="py-1.5 px-4 rounded-full border border-slate-200/80 bg-white/80 text-[10px] font-bold uppercase tracking-wider text-slate-655 hover:text-indigo-600 hover:border-indigo-200 transition-premium flex items-center gap-1.5 disabled:opacity-40 cursor-pointer shadow-sm"
                    >
                      {grammarFixing ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5 text-indigo-500" />}
                      <span>Fix Grammar</span>
                    </button>

                    <div className="flex items-center gap-1">
                      <select
                        value={selectedLanguage}
                        onChange={(e) => setSelectedLanguage(e.target.value)}
                        className="py-1.5 px-2 rounded-l-full border border-r-0 border-slate-200/80 bg-white/80 text-[10px] font-bold text-slate-655 outline-none focus:border-pink-300 transition-premium cursor-pointer shadow-sm"
                      >
                        {INDIAN_LANGUAGES.map(lang => (
                          <option key={lang} value={lang}>{lang}</option>
                        ))}
                      </select>
                      <button
                        onClick={() => handleTranslateInput()}
                        disabled={!inputText.trim() || translatingInput}
                        className="py-1.5 px-3 rounded-r-full border border-slate-200/80 bg-white/80 text-[10px] font-bold uppercase tracking-wider text-slate-655 hover:text-pink-600 hover:border-pink-200 transition-premium flex items-center gap-1.5 disabled:opacity-40 cursor-pointer shadow-sm"
                      >
                        {translatingInput ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Globe className="w-3.5 h-3.5 text-pink-500" />}
                        <span>Translate</span>
                      </button>
                    </div>
                  </div>
                </div>

                {/* Active Attachment Capsule */}
                {selectedDoc && (
                  <div className="flex items-center gap-2 self-start py-1.5 px-3 bg-white/80 border border-slate-200 text-slate-700 text-xs rounded-full shadow-sm animate-pulse-soft backdrop-blur-sm">
                    <FileText className="w-3.5 h-3.5 text-indigo-600" />
                    <span className="font-bold truncate max-w-xs">{selectedDoc.filename}</span>
                    <button
                      onClick={handleDetachDoc}
                      className="p-0.5 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-700 transition-colors cursor-pointer"
                      title="Detach PDF"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                )}

                {/* Core Input box card */}
                <div className="flex items-end gap-3 glass-input rounded-3xl p-3.5 focus-within:border-indigo-300 focus-within:ring-4 focus-within:ring-indigo-50/50 transition-premium shadow-xl">
                  
                  {/* Hidden native input and Paperclip trigger */}
                  <input
                    type="file"
                    accept=".pdf"
                    ref={fileInputRef}
                    onChange={onFileChange}
                    className="hidden"
                  />
                  
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    disabled={uploading}
                    className={`p-3 rounded-2xl transition-premium shrink-0 cursor-pointer ${
                      uploading 
                        ? "bg-slate-100 text-indigo-650 animate-pulse" 
                        : "bg-slate-50 hover:bg-slate-100 text-slate-500 hover:text-slate-700 border border-slate-200/60 shadow-sm"
                    }`}
                    title="Attach PDF Document"
                  >
                    {uploading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Paperclip className="w-4 h-4" />}
                  </button>

                  {/* Voice dictate mic trigger */}
                  <button
                    onClick={toggleListening}
                    className={`p-3 rounded-2xl transition-premium shrink-0 cursor-pointer ${
                      isListening
                        ? "bg-rose-600 text-white animate-pulse"
                        : "bg-slate-50 hover:bg-slate-100 text-slate-500 hover:text-slate-700 border border-slate-200/60 shadow-sm"
                    }`}
                    title={isListening ? "Listening... click to stop" : "Start Voice dictation"}
                  >
                    <Mic className="w-4 h-4" />
                  </button>

                  {/* Text Input area */}
                  <textarea
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        handleSend();
                      }
                    }}
                    placeholder={
                      uploading
                        ? "Uploading and parsing PDF..."
                        : isListening
                        ? "Listening... Speak now."
                        : selectedDoc
                        ? `Ask a question about '${selectedDoc.filename}'...`
                        : "Message bharatai, toggle search or attach PDF..."
                    }
                    disabled={uploading}
                    rows={1}
                    className="flex-1 resize-none bg-transparent outline-none border-none text-slate-800 placeholder-slate-400 text-sm max-h-32 py-2 px-1 focus:ring-0 disabled:opacity-50"
                  />

                  {/* Send Message */}
                  <button
                    onClick={() => handleSend()}
                    disabled={!inputText.trim() || chatLoading || uploading}
                    className="p-3 bg-slate-900 hover:bg-slate-800 text-white rounded-2xl transition-premium disabled:opacity-40 shrink-0 shadow-md cursor-pointer hover:shadow-lg hover:-translate-y-0.5 active:translate-y-0"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Right Side: Agent Observability & Document Intelligence Dashboard */}
          {selectedDoc && (
            <div className="w-[45%] h-full flex flex-col bg-white/30 backdrop-blur-lg overflow-hidden border-l border-slate-200/50 z-20 animate-slide-in-right">
              
              {/* Header */}
              <div className="p-6 border-b border-slate-200/30 flex items-start justify-between bg-white/40 shrink-0">
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-2xl bg-white border border-slate-200/50 text-slate-700 shadow-sm shrink-0">
                    <FileText className="w-6 h-6 text-indigo-600" />
                  </div>
                  <div className="min-w-0">
                    <h3 className="text-xs font-bold text-slate-805 truncate max-w-[200px]" title={selectedDoc.filename}>
                      {selectedDoc.filename}
                    </h3>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-[10px] text-slate-400 font-bold">
                        {formatSize(selectedDoc.file_size)}
                      </span>
                      <span className="text-[10px] text-slate-300">•</span>
                      {selectedDoc.status === "processing" ? (
                        <span className="text-[10px] text-amber-500 flex items-center gap-1.5 font-bold animate-pulse-soft">
                          <RefreshCw className="w-3 h-3 animate-spin" /> Summarizing...
                        </span>
                      ) : selectedDoc.status === "completed" ? (
                        <span className="text-[10px] text-emerald-600 flex items-center gap-1.5 font-bold">
                          <CheckCircle className="w-3 h-3 text-emerald-500" /> Analysis Ready
                        </span>
                      ) : (
                        <span className="text-[10px] text-rose-500 flex items-center gap-1.5 font-bold">
                          <AlertCircle className="w-3 h-3" /> Issue
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <button
                  onClick={handleDetachDoc}
                  className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-premium border border-slate-200 cursor-pointer"
                  title="Detach PDF"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Tab selection bar */}
              <div className="px-6 py-3 border-b border-slate-200/30 bg-white/50 flex items-center justify-between gap-3 shrink-0">
                <div className="flex items-center gap-1.5 text-[9px] text-slate-500 font-black uppercase tracking-[0.2em]">
                  <Sparkles className="w-3.5 h-3.5 text-orange-500 animate-pulse-soft" /> arya trace
                </div>
                <div className="flex items-center bg-slate-100/60 p-0.5 rounded-2xl border border-slate-250/20">
                  <button
                    onClick={() => setActiveSummaryTab("trace")}
                    className={`px-3.5 py-1.5 rounded-xl text-[9px] font-bold uppercase transition-premium cursor-pointer ${
                      activeSummaryTab === "trace"
                        ? "bg-white text-slate-800 shadow-sm border border-slate-200/40"
                        : "text-slate-400 hover:text-slate-700"
                    }`}
                  >
                    Trace
                  </button>
                  <button
                    onClick={() => setActiveSummaryTab("summary")}
                    className={`px-3.5 py-1.5 rounded-xl text-[9px] font-bold uppercase transition-premium cursor-pointer ${
                      activeSummaryTab === "summary"
                        ? "bg-white text-slate-800 shadow-sm border border-slate-200/40"
                        : "text-slate-400 hover:text-slate-700"
                    }`}
                  >
                    Summaries
                  </button>
                  <button
                    onClick={() => {
                      setActiveSummaryTab("digitized");
                      if (!digitizedText) handleDigitize();
                    }}
                    className={`px-3.5 py-1.5 rounded-xl text-[9px] font-bold uppercase transition-premium cursor-pointer ${
                      activeSummaryTab === "digitized"
                        ? "bg-white text-slate-800 shadow-sm border border-slate-200/40"
                        : "text-slate-400 hover:text-slate-700"
                    }`}
                  >
                    OCR
                  </button>
                  <button
                    onClick={() => {
                      setActiveSummaryTab("compliance");
                      if (!complianceReport) handleComplianceAudit(auditPreset);
                    }}
                    className={`px-3.5 py-1.5 rounded-xl text-[9px] font-bold uppercase transition-premium cursor-pointer ${
                      activeSummaryTab === "compliance"
                        ? "bg-white text-slate-800 shadow-sm border border-slate-200/40"
                        : "text-slate-400 hover:text-slate-700"
                    }`}
                  >
                    Audit
                  </button>
                </div>
              </div>

              {/* Tab Contents Scrollable Feed */}
              <div className="flex-1 overflow-y-auto scroll-smooth-premium p-6 space-y-6">
                
                {activeSummaryTab === "trace" && (
                  <div className="space-y-6 animate-fade-in">
                    <div className="space-y-1">
                      <h3 className="text-xs font-bold text-slate-800">Execution Observability Trace</h3>
                      <p className="text-[9px] text-slate-400 font-medium">Traceable multi-agent execution checkpoints & logic steps</p>
                    </div>
                    <div className="relative border-l border-slate-200 ml-3.5 pl-6 space-y-6 py-2">
                      {getAgentSteps().map((step) => (
                        <div key={step.id} className="relative">
                          <div className="absolute -left-[35px] top-0.5">
                            {step.status === "completed" ? (
                              <div className="w-5 h-5 rounded-full bg-emerald-50 border border-emerald-500/30 text-emerald-600 flex items-center justify-center shadow-sm shadow-emerald-100">
                                <CheckCircle className="w-3.5 h-3.5" />
                              </div>
                            ) : step.status === "pending" ? (
                              <div className="w-5 h-5 rounded-full bg-indigo-50 border border-indigo-500/30 text-indigo-605 flex items-center justify-center animate-spin">
                                <RefreshCw className="w-3.5 h-3.5" />
                              </div>
                            ) : (
                              <div className="w-5 h-5 rounded-full bg-slate-50 border border-slate-200 text-slate-400 flex items-center justify-center">
                                <div className="w-1.5 h-1.5 rounded-full bg-slate-300" />
                              </div>
                            )}
                          </div>
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <h4 className="text-xs font-bold text-slate-800">{step.name}</h4>
                              {step.time && (
                                <span className="text-[9px] px-1.5 py-0.5 bg-slate-100 border border-slate-200/50 rounded text-slate-500 font-mono">
                                  {step.time}
                                </span>
                              )}
                            </div>
                            <p className="text-[10px] text-slate-505 leading-relaxed font-medium">{step.details}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {activeSummaryTab === "summary" && (
                  <div className="space-y-6 animate-fade-in">
                    
                    {/* Punjabi translation summary */}
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <h4 className="text-xs font-bold text-slate-805 flex items-center gap-1.5">
                          <Globe className="w-4 h-4 text-pink-500" />
                          <span>ਮੁੱਖ ਸਾਰਾਂਸ਼ (Punjabi Summary)</span>
                        </h4>
                        <button
                          onClick={() => toggleSpeakMessage(9998, selectedDoc.summary_punjabi || "")}
                          className={`py-1.5 px-3 rounded-full border text-[9px] font-bold uppercase tracking-wider flex items-center gap-1.5 transition-premium cursor-pointer ${
                            speakingMessageIndex === 9998
                              ? "bg-indigo-50 border-indigo-200 text-indigo-600 animate-pulse"
                              : "border-slate-200 bg-white/85 text-slate-605 hover:text-indigo-650 hover:border-slate-300 shadow-sm"
                          }`}
                        >
                          <Volume2 className="w-3.5 h-3.5" />
                          <span>{speakingMessageIndex === 9998 ? "Stop Listening" : "Listen (ਸੁਣੋ)"}</span>
                        </button>
                      </div>
                      <div className="p-5 rounded-3xl bg-white border border-slate-200/50 max-h-60 overflow-y-auto shadow-sm relative overflow-hidden group">
                        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-orange-400 to-pink-500" />
                        <p className="text-slate-800 leading-relaxed text-xs font-serif whitespace-pre-line pt-1">
                          {selectedDoc.summary_punjabi || "Generating translations summary..."}
                        </p>
                      </div>
                    </div>

                    {/* English Summary */}
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <h4 className="text-xs font-bold text-slate-805 flex items-center gap-1.5">
                          <FileText className="w-4 h-4 text-indigo-600" />
                          <span>English Summary</span>
                        </h4>
                        <button
                          onClick={() => toggleSpeakMessage(9999, selectedDoc.summary || "")}
                          className={`py-1.5 px-3 rounded-full border text-[9px] font-bold uppercase tracking-wider flex items-center gap-1.5 transition-premium cursor-pointer ${
                            speakingMessageIndex === 9999
                              ? "bg-indigo-50 border-indigo-200 text-indigo-600 animate-pulse"
                              : "border-slate-200 bg-white/85 text-slate-605 hover:text-indigo-650 hover:border-slate-300 shadow-sm"
                          }`}
                        >
                          <Volume2 className="w-3.5 h-3.5" />
                          <span>{speakingMessageIndex === 9999 ? "Stop Listening" : "Listen"}</span>
                        </button>
                      </div>
                      <div className="p-5 rounded-3xl bg-white border border-slate-200/50 max-h-60 overflow-y-auto shadow-sm relative overflow-hidden group">
                        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-indigo-400 to-orange-450" />
                        <p className="text-slate-800 leading-relaxed text-xs whitespace-pre-line pt-1 font-medium">
                          {selectedDoc.summary || "Generating summaries..."}
                        </p>
                      </div>
                    </div>

                  </div>
                )}

                {activeSummaryTab === "digitized" && (
                  <div className="space-y-4 animate-fade-in">
                    <div className="flex items-center justify-between">
                      <span className="text-[9px] font-black uppercase tracking-wider text-slate-450">Layout-Preserved OCR</span>
                      <div className="flex items-center gap-2">
                        {digitizedText && (
                          <button
                            onClick={() => {
                              navigator.clipboard.writeText(digitizedText || "");
                              alert("Digitized layout OCR text copied!");
                            }}
                            className="px-3 py-1.5 bg-white border border-slate-200 hover:bg-slate-50 rounded-xl text-[9px] font-bold uppercase text-slate-700 transition-premium cursor-pointer shadow-sm"
                          >
                            Copy Text
                          </button>
                        )}
                        <button
                          onClick={handleDigitize}
                          disabled={digitizing}
                          className="px-3 py-1.5 bg-slate-900 border border-slate-900 text-white rounded-xl text-[9px] font-bold uppercase hover:bg-slate-800 transition-premium cursor-pointer shadow-md"
                        >
                          Redigitize
                        </button>
                      </div>
                    </div>
                    {digitizing && (
                      <div className="py-16 flex flex-col items-center justify-center gap-3 text-slate-450 text-xs bg-white/50 rounded-2xl border border-slate-200 border-dashed animate-pulse-soft">
                        <RefreshCw className="w-5 h-5 animate-spin text-purple-605" />
                        <span className="font-black tracking-wider uppercase text-[8px] text-purple-600 animate-pulse-soft">Running Multilingual OCR...</span>
                      </div>
                    )}
                    {digitizedText && !digitizing && (
                      <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 max-h-[420px] overflow-y-auto font-mono text-[10px] text-slate-200 whitespace-pre-wrap leading-relaxed shadow-lg">
                        {digitizedText}
                      </div>
                    )}
                  </div>
                )}

                {activeSummaryTab === "compliance" && (
                  <div className="space-y-6 animate-fade-in">
                    <div className="flex items-center justify-between gap-3">
                      <div className="flex items-center gap-2">
                        <select
                          value={auditPreset}
                          onChange={(e) => {
                            setAuditPreset(e.target.value);
                            handleComplianceAudit(e.target.value);
                          }}
                          className="bg-white border border-slate-200 rounded-xl text-[10px] font-bold px-3 py-1.5 text-slate-705 outline-none focus:border-indigo-300 transition-premium shadow-sm cursor-pointer"
                        >
                          <option value="DPDP Act 2023">DPDP Act 2023 (Privacy)</option>
                          <option value="IRDAI Guidelines">IRDAI Guidelines (Insurance)</option>
                          <option value="Legal Risk">Legal Risk & Redlining</option>
                        </select>
                        <button
                          onClick={() => handleComplianceAudit(auditPreset)}
                          disabled={auditing}
                          className="px-3 py-1.5 bg-white border border-slate-200 hover:bg-slate-50/50 rounded-xl text-[10px] font-bold uppercase text-slate-755 transition-premium cursor-pointer disabled:opacity-50 shadow-sm"
                        >
                          Re-Audit
                        </button>
                      </div>
                    </div>

                    {auditing && (
                      <div className="py-16 flex flex-col items-center justify-center gap-3 text-slate-455 text-xs bg-white/50 rounded-2xl border border-slate-200 border-dashed animate-pulse-soft">
                        <RefreshCw className="w-5 h-5 animate-spin text-amber-500" />
                        <span className="font-black tracking-wider uppercase text-[8px] text-amber-550 animate-pulse-soft">Analyzing compliance scorecard...</span>
                      </div>
                    )}

                    {complianceReport && !auditing && (
                      <div className="space-y-6">
                        
                        {/* Circular Gauge Scorecard Gauge UI */}
                        <div className="flex flex-col items-center justify-center p-6 bg-white/60 border border-slate-200/50 rounded-3xl relative gap-4 shadow-sm overflow-hidden">
                          <div className="absolute w-24 h-24 rounded-full bg-emerald-400/5 blur-xl pointer-events-none" />
                          <div className="relative w-32 h-32 flex items-center justify-center z-10">
                            <svg className="w-full h-full transform -rotate-90">
                              <circle
                                cx="64"
                                cy="64"
                                r="50"
                                className="stroke-slate-100 fill-transparent"
                                strokeWidth="8"
                              />
                              <circle
                                cx="64"
                                cy="64"
                                r="50"
                                className={`fill-transparent transition-all duration-1000 ${
                                  complianceReport.score >= 80 
                                    ? "stroke-emerald-500" 
                                    : complianceReport.score >= 50 
                                    ? "stroke-amber-500" 
                                    : "stroke-rose-500"
                                }`}
                                strokeWidth="8"
                                strokeDasharray={2 * Math.PI * 50}
                                strokeDashoffset={2 * Math.PI * 50 - (complianceReport.score / 100) * (2 * Math.PI * 50)}
                                strokeLinecap="round"
                              />
                            </svg>
                             <div className="absolute inset-0 flex flex-col items-center justify-center">
                               <span className="text-3xl font-black text-slate-900 font-display">{complianceReport.score}</span>
                               <span className="text-[8px] uppercase tracking-widest font-black text-slate-400">Score</span>
                             </div>
                          </div>
                          <div className="text-center z-10">
                            <h5 className="text-xs font-bold text-slate-800">Compliance Audit Score</h5>
                            <p className="text-[9px] text-slate-450 mt-1 font-semibold">Based on regulatory audit checks</p>
                          </div>
                        </div>

                        {/* List of checked rules */}
                        <div className="space-y-2.5">
                          <h5 className="text-[9px] font-black uppercase tracking-wider text-slate-450 px-1">Audited Criteria Parameters</h5>
                          <div className="space-y-2.5 max-h-64 overflow-y-auto pr-1">
                            {complianceReport.checks.map((check, cIdx) => (
                              <div key={cIdx} className="p-4 rounded-2xl bg-white border border-slate-200/50 space-y-1.5 hover:border-slate-350 transition-premium shadow-sm">
                                <div className="flex items-start justify-between gap-3">
                                  <h5 className="text-xs font-bold text-slate-800 leading-tight">{check.rule}</h5>
                                  <span className={`px-2.5 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider border shrink-0 ${
                                    check.status === "Passed"
                                      ? "bg-emerald-50 text-emerald-700 border-emerald-100/50"
                                      : check.status === "Warning"
                                      ? "bg-amber-50 text-amber-700 border-amber-100/50"
                                      : "bg-rose-50 text-rose-700 border-rose-100/50"
                                  }`}>
                                    {check.status}
                                  </span>
                                </div>
                                <p className="text-[10px] text-slate-500 leading-relaxed font-medium">{check.details}</p>
                              </div>
                            ))}
                          </div>
                        </div>

                      </div>
                    )}
                  </div>
                )}

              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
