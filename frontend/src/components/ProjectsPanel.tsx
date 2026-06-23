"use client";

import React, { useState, useEffect } from "react";
import { Folder, Plus, Trash2, ArrowLeft, MessageSquare, FileText, Clipboard, Tag } from "lucide-react";

interface Project {
  id: string;
  name: string;
  type: "Study" | "Research" | "Work" | "Personal";
  created_at: string;
  notes?: string[];
  chatIds?: number[];
}

interface ProjectsPanelProps {
  token: string | null;
  apiBaseUrl: string;
  onSelectConversation: (id: number | null) => void;
}

export default function ProjectsPanel({ token, apiBaseUrl, onSelectConversation }: ProjectsPanelProps) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjId, setSelectedProjId] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  
  const [name, setName] = useState("");
  const [type, setType] = useState<"Study" | "Research" | "Work" | "Personal">("Study");
  
  const [newNoteText, setNewNoteText] = useState("");
  const [allChats, setAllChats] = useState<any[]>([]);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("yaar_projects");
      if (saved) {
        try {
          setProjects(JSON.parse(saved));
        } catch (_) {}
      } else {
        localStorage.setItem("yaar_projects", JSON.stringify([]));
        setProjects([]);
      }
    }

    const fetchConversations = async () => {
      if (!token) return;
      try {
        const res = await fetch(`${apiBaseUrl}/api/conversations`, {
          headers: { "Authorization": `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setAllChats(data);
        }
      } catch (e) {
        console.error("Failed to load conversations in projects:", e);
      }
    };
    fetchConversations();
  }, [token, apiBaseUrl]);

  const saveProjects = (updated: Project[]) => {
    setProjects(updated);
    localStorage.setItem("yaar_projects", JSON.stringify(updated));
  };

  const handleCreateProject = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    const newProj: Project = {
      id: `proj-${Date.now()}`,
      name: name.trim(),
      type,
      created_at: new Date().toISOString(),
      notes: [],
      chatIds: []
    };

    const updated = [newProj, ...projects];
    saveProjects(updated);
    
    setName("");
    setType("Study");
    setShowCreateForm(false);
    setSelectedProjId(newProj.id);
  };

  const handleDeleteProject = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this project binder? Associated items will not be deleted.")) return;

    const updated = projects.filter(p => p.id !== id);
    saveProjects(updated);
    if (selectedProjId === id) {
      setSelectedProjId(null);
    }
  };

  const handleAddNote = () => {
    if (!newNoteText.trim() || !selectedProjId) return;

    const updated = projects.map(p => {
      if (p.id === selectedProjId) {
        return {
          ...p,
          notes: [...(p.notes || []), newNoteText.trim()]
        };
      }
      return p;
    });

    saveProjects(updated);
    setNewNoteText("");
  };

  const handleDeleteNote = (noteIndex: number) => {
    if (!selectedProjId) return;

    const updated = projects.map(p => {
      if (p.id === selectedProjId) {
        const filteredNotes = (p.notes || []).filter((_, i) => i !== noteIndex);
        return { ...p, notes: filteredNotes };
      }
      return p;
    });

    saveProjects(updated);
  };

  const handleLinkChat = (chatId: number) => {
    if (!selectedProjId) return;

    const updated = projects.map(p => {
      if (p.id === selectedProjId) {
        const currentChats = p.chatIds || [];
        if (currentChats.includes(chatId)) {
          return { ...p, chatIds: currentChats.filter(id => id !== chatId) };
        } else {
          return { ...p, chatIds: [...currentChats, chatId] };
        }
      }
      return p;
    });

    saveProjects(updated);
  };

  const selectedProj = projects.find(p => p.id === selectedProjId);

  if (selectedProj) {
    const linkedChats = allChats.filter(c => (selectedProj.chatIds || []).includes(c.id));
    const unlinkedChats = allChats.filter(c => !(selectedProj.chatIds || []).includes(c.id));

    return (
      <div className="flex-1 overflow-y-auto scroll-smooth-premium p-6 md:p-12 text-slate-150 max-w-4xl mx-auto space-y-8 animate-slide-in-right bg-[#121316]">
        
        {/* Header navigation */}
        <button
          onClick={() => setSelectedProjId(null)}
          className="inline-flex items-center gap-2 text-xs font-bold text-slate-405 hover:text-white transition-colors cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Project Binders
        </button>

        {/* Project Meta */}
        <div className="flex items-center justify-between border-b border-white/5 pb-6">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded bg-amber-950/20 border border-amber-900/30 text-[9px] font-black uppercase text-amber-500">
                {selectedProj.type}
              </span>
              <span className="text-[10px] text-slate-500 font-mono">
                Created {new Date(selectedProj.created_at).toLocaleDateString("en-IN")}
              </span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-black text-white tracking-tight font-display flex items-center gap-2">
              <Folder className="w-7 h-7 text-amber-500 shrink-0" />
              {selectedProj.name}
            </h2>
          </div>

          <button
            onClick={(e) => handleDeleteProject(e, selectedProj.id)}
            className="p-2.5 rounded-xl hover:bg-rose-950/20 border border-transparent hover:border-rose-900/30 text-slate-400 hover:text-rose-450 transition-premium cursor-pointer"
            title="Delete Project"
          >
            <Trash2 className="w-4.5 h-4.5" />
          </button>
        </div>

        {/* Workspace Panels Grid */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
          
          {/* Notes column */}
          <div className="md:col-span-7 space-y-5">
            <div className="flex items-center gap-2">
              <Clipboard className="w-4 h-4 text-amber-500" />
              <h3 className="text-xs font-black uppercase tracking-wider text-slate-450">Project Notes & Outlines</h3>
            </div>

            {/* Notes List */}
            <div className="flex flex-col gap-3">
              {(selectedProj.notes || []).map((note, index) => (
                <div
                  key={index}
                  className="p-4 rounded-2xl glass-card flex items-start justify-between gap-4 text-xs font-medium text-slate-200"
                >
                  <p className="leading-relaxed whitespace-pre-wrap">{note}</p>
                  <button
                    onClick={() => handleDeleteNote(index)}
                    className="text-slate-500 hover:text-rose-450 p-1 rounded transition-colors shrink-0"
                    title="Remove Note"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}

              {/* Add Note Input */}
              <div className="flex flex-col gap-2 mt-2">
                <textarea
                  value={newNoteText}
                  onChange={(e) => setNewNoteText(e.target.value)}
                  placeholder="Write a new note, research highlight or study task..."
                  className="w-full p-4 rounded-2xl glass-input text-xs text-white placeholder-slate-500 outline-none min-h-[90px] resize-y"
                />
                <button
                  onClick={handleAddNote}
                  disabled={!newNoteText.trim()}
                  className="self-end px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white text-xs font-bold rounded-xl transition-premium cursor-pointer disabled:opacity-40"
                >
                  Add Project Note
                </button>
              </div>
            </div>
          </div>

          {/* Linked elements column */}
          <div className="md:col-span-5 space-y-6">
            
            {/* Chats list */}
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-amber-550" />
                <h3 className="text-xs font-black uppercase tracking-wider text-slate-450">Linked Conversations</h3>
              </div>

              {linkedChats.length > 0 ? (
                <div className="flex flex-col gap-2.5">
                  {linkedChats.map((c) => (
                    <div
                      key={c.id}
                      onClick={() => onSelectConversation(c.id)}
                      className="p-3.5 rounded-xl bg-slate-900/40 border border-slate-800/40 flex items-center justify-between text-xs text-slate-250 cursor-pointer hover:border-amber-500/35 transition-premium group"
                    >
                      <span className="truncate pr-2 font-bold group-hover:text-white transition-colors">{c.title}</span>
                      <ArrowLeft className="w-3.5 h-3.5 text-slate-500 group-hover:text-amber-500 transition-colors rotate-180 shrink-0" />
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-500 font-medium pl-1">No chats linked to this project yet.</p>
              )}
            </div>

            {/* Associate chats form */}
            {unlinkedChats.length > 0 && (
              <div className="pt-4 border-t border-white/5 space-y-3">
                <span className="text-[10px] font-black uppercase tracking-wider text-slate-500 block">Link Existing Conversations</span>
                <div className="flex flex-col gap-2 max-h-[220px] overflow-y-auto pr-1">
                  {unlinkedChats.map((c) => (
                    <button
                      key={c.id}
                      onClick={() => handleLinkChat(c.id)}
                      className="w-full p-2.5 rounded-lg bg-slate-950/40 border border-slate-900 text-left text-xs text-slate-400 hover:text-slate-200 hover:border-slate-800 transition-premium cursor-pointer truncate font-medium"
                    >
                      + {c.title}
                    </button>
                  ))}
                </div>
              </div>
            )}

          </div>

        </div>

      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto scroll-smooth-premium p-6 md:p-12 text-slate-150 max-w-4xl mx-auto space-y-8 animate-slide-in-right bg-[#121316]">
      
      {/* Intro Header */}
      <div className="flex flex-col sm:flex-row items-center sm:items-start justify-between gap-4 border-b border-white/5 pb-6">
        <div className="space-y-1.5 text-center sm:text-left">
          <h2 className="text-3xl font-black text-white tracking-tight font-display">
            Project Binders
          </h2>
          <p className="text-slate-400 text-xs font-medium max-w-md">
            Group chats, study notes, and research highlights into dedicated personal workspaces.
          </p>
        </div>

        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="px-4 py-2.5 bg-amber-605 hover:bg-amber-600 text-white rounded-xl flex items-center justify-center gap-1.5 text-xs font-bold transition-premium hover:-translate-y-0.5 active:translate-y-0 cursor-pointer shadow-md"
        >
          <Plus className="w-4 h-4" />
          <span>New Project</span>
        </button>
      </div>

      {/* New Project Form Card */}
      {showCreateForm && (
        <form onSubmit={handleCreateProject} className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/60 shadow-xl flex flex-col gap-4 animate-slide-in-right">
          <h3 className="text-sm font-bold text-white">Create New Project Binder</h3>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] uppercase tracking-wider font-extrabold text-slate-450">Project Name</label>
              <input
                type="text"
                required
                value={name}
                onChange={e => setName(e.target.value)}
                placeholder="e.g. Mechanical Physics Prep"
                className="w-full px-4.5 py-3 rounded-xl bg-slate-950 border border-slate-800/80 text-white text-xs placeholder-slate-550 outline-none focus:border-amber-500 transition-premium"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] uppercase tracking-wider font-extrabold text-slate-450">Project Type</label>
              <select
                value={type}
                onChange={e => setType(e.target.value as any)}
                className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800/80 text-white text-xs outline-none focus:border-amber-500 transition-premium cursor-pointer font-bold"
              >
                <option value="Study">🎓 Study Project</option>
                <option value="Research">🔬 Research Project</option>
                <option value="Work">💼 Work / Career Project</option>
                <option value="Personal">🏠 Personal Project</option>
              </select>
            </div>
          </div>

          <div className="flex gap-2 justify-end pt-2">
            <button
              type="button"
              onClick={() => setShowCreateForm(false)}
              className="px-4 py-2 border border-slate-800 text-slate-400 hover:text-white rounded-xl text-xs font-bold transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2 bg-amber-600 hover:bg-amber-500 text-white rounded-xl text-xs font-bold transition-premium cursor-pointer shadow-md"
            >
              Create Project
            </button>
          </div>
        </form>
      )}

      {/* Projects Grid List */}
      {projects.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {projects.map((proj) => {
            const notesCount = proj.notes?.length || 0;
            const chatsCount = proj.chatIds?.length || 0;

            return (
              <div
                key={proj.id}
                onClick={() => setSelectedProjId(proj.id)}
                className="p-5.5 rounded-2xl glass-card flex flex-col justify-between gap-6"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="p-3 rounded-2xl bg-amber-950/20 text-amber-500 border border-amber-900/30 shrink-0">
                    <Folder className="w-5 h-5" />
                  </div>
                  <span className="px-2 py-0.5 rounded bg-slate-800/40 text-[9px] font-black uppercase text-slate-400 tracking-wider">
                    {proj.type}
                  </span>
                </div>

                <div className="space-y-1">
                  <h4 className="text-sm font-bold text-slate-200 group-hover:text-white transition-colors truncate">
                    {proj.name}
                  </h4>
                  <p className="text-[10px] text-slate-450 font-medium">
                    Created {new Date(proj.created_at).toLocaleDateString("en-IN", { day: "numeric", month: "long" })}
                  </p>
                </div>

                <div className="flex items-center gap-4 pt-3 border-t border-white/5 text-[10px] text-slate-450 font-extrabold uppercase tracking-wider">
                  <span className="flex items-center gap-1">
                    <MessageSquare className="w-3.5 h-3.5 text-blue-400/80" /> {chatsCount} Chats
                  </span>
                  <span className="flex items-center gap-1">
                    <Clipboard className="w-3.5 h-3.5 text-amber-550" /> {notesCount} Notes
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="h-64 flex flex-col items-center justify-center text-center p-8 border border-dashed border-slate-800/80 rounded-3xl bg-[#0b0c16]/30 space-y-4">
          <Folder className="w-10 h-10 text-slate-555 animate-pulse" />
          <div className="space-y-1">
            <h4 className="text-sm font-black text-slate-200">No Projects Yet</h4>
            <p className="text-xs text-slate-500 max-w-md mx-auto leading-relaxed font-semibold">
              Projects are dedicated workspace binders where you can group related chats, uploaded documents, summaries, and regulatory compliance reports to work on specific topics, studies, or ventures.
            </p>
          </div>
          <button
            onClick={() => setShowCreateForm(true)}
            className="px-4.5 py-2 bg-amber-600/10 hover:bg-amber-600/20 border border-amber-500/20 text-amber-500 hover:text-amber-400 text-xs font-black uppercase tracking-wider rounded-xl transition-premium cursor-pointer shadow-md"
          >
            Create Your First Binder
          </button>
        </div>
      )}
    </div>
  );
}
