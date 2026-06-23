"use client";

import React, { useState, useEffect } from "react";
import { Search, Tag, Trash2, Plus, Bookmark, FileText, Quote, Edit, Check, X } from "lucide-react";

interface VaultItem {
  id: string;
  title: string;
  content: string;
  type: "Saved Answer" | "Highlight" | "Note" | "Citation";
  tags: string[];
  created_at: string;
}

export default function VaultPanel() {
  const [items, setItems] = useState<VaultItem[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [selectedType, setSelectedType] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);

  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [type, setType] = useState<VaultItem["type"]>("Note");
  const [tagsInput, setTagsInput] = useState("");

  useEffect(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("yaar_vault");
      if (saved) {
        try {
          setItems(JSON.parse(saved));
        } catch (_) {}
      } else {
        const defaultItems: VaultItem[] = [
          {
            id: "vault-1",
            title: "🇮🇳 Sovereign Data Sovereignty Act",
            content: "The Digital Personal Data Protection (DPDP) Act of India strictly governs that user logs cannot be used for AI model training without explicit consent. YAAR complies fully by auto-purging uploaded PDF buffers locally.",
            type: "Citation",
            tags: ["DPDP", "Privacy", "Legal"],
            created_at: new Date().toISOString()
          },
          {
            id: "vault-2",
            title: "💡 Quantum Computing Mechanics",
            content: "Quantum computing operates on qubits, which leverage superposition and entanglement to solve calculations that would take classical supercomputers thousands of years to compute.",
            type: "Saved Answer",
            tags: ["Science", "Computing", "Research"],
            created_at: new Date().toISOString()
          }
        ];
        localStorage.setItem("yaar_vault", JSON.stringify(defaultItems));
        setItems(defaultItems);
      }
    }
  }, []);

  const saveItems = (updated: VaultItem[]) => {
    setItems(updated);
    localStorage.setItem("yaar_vault", JSON.stringify(updated));
  };

  const handleCreateItem = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) return;

    const tagsList = tagsInput
      .split(",")
      .map(t => t.trim())
      .filter(t => t.length > 0);

    const newItem: VaultItem = {
      id: `vault-${Date.now()}`,
      title: title.trim(),
      content: content.trim(),
      type,
      tags: tagsList,
      created_at: new Date().toISOString()
    };

    const updated = [newItem, ...items];
    saveItems(updated);

    setTitle("");
    setContent("");
    setType("Note");
    setTagsInput("");
    setShowAddForm(false);
  };

  const handleDeleteItem = (id: string) => {
    if (!confirm("Are you sure you want to delete this item from your second brain? This action cannot be undone.")) return;
    const updated = items.filter(item => item.id !== id);
    saveItems(updated);
  };

  const allUniqueTags = Array.from(
    new Set(items.flatMap(item => item.tags || []))
  );

  const filteredItems = items.filter(item => {
    const matchesSearch =
      item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.content.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = !selectedType || item.type === selectedType;
    const matchesTag = !selectedTag || (item.tags || []).includes(selectedTag);

    return matchesSearch && matchesType && matchesTag;
  });

  const getTypeIcon = (type: VaultItem["type"]) => {
    switch (type) {
      case "Saved Answer":
        return <Bookmark className="w-4 h-4 text-emerald-450" />;
      case "Highlight":
        return <Quote className="w-4 h-4 text-pink-400" />;
      case "Citation":
        return <FileText className="w-4 h-4 text-blue-400" />;
      case "Note":
      default:
        return <Edit className="w-4 h-4 text-amber-550" />;
    }
  };

  return (
    <div className="flex-1 overflow-y-auto scroll-smooth-premium p-6 md:p-12 text-slate-150 max-w-5xl mx-auto space-y-8 animate-slide-in-right bg-[#121316]">
      
      {/* Header section */}
      <div className="flex flex-col sm:flex-row items-center sm:items-start justify-between gap-4 border-b border-white/5 pb-6">
        <div className="space-y-1.5 text-center sm:text-left">
          <h2 className="text-3xl font-black text-white tracking-tight font-display">
            The Vault
          </h2>
          <p className="text-slate-400 text-xs font-medium max-w-md">
            YAAR{"'"}s second brain. Securely store your saved responses, quotes, highlights, notes, and research citations.
          </p>
        </div>

        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="px-4 py-2.5 bg-amber-600 hover:bg-amber-500 text-white rounded-xl flex items-center justify-center gap-1.5 text-xs font-bold transition-premium hover:-translate-y-0.5 active:translate-y-0 cursor-pointer shadow-md"
        >
          <Plus className="w-4 h-4" />
          <span>Add Note</span>
        </button>
      </div>

      {/* Add manually form */}
      {showAddForm && (
        <form onSubmit={handleCreateItem} className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/60 shadow-xl flex flex-col gap-4 animate-slide-in-right">
          <h3 className="text-sm font-bold text-white">Save Item to Vault</h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] uppercase tracking-wider font-extrabold text-slate-450">Title</label>
              <input
                type="text"
                required
                value={title}
                onChange={e => setTitle(e.target.value)}
                placeholder="e.g. Quantum Entanglement Definition"
                className="w-full px-4 py-3 rounded-xl bg-[#121316] border border-slate-800/80 text-white text-xs outline-none focus:border-amber-500 transition-premium"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] uppercase tracking-wider font-extrabold text-slate-450">Category Type</label>
              <select
                value={type}
                onChange={e => setType(e.target.value as any)}
                className="w-full px-4 py-3 rounded-xl bg-[#121316] border border-slate-800/80 text-white text-xs outline-none focus:border-amber-500 transition-premium cursor-pointer font-bold"
              >
                <option value="Note">📝 Custom Note</option>
                <option value="Saved Answer">🔖 Saved AI Answer</option>
                <option value="Highlight">💬 Text Highlight</option>
                <option value="Citation">📄 Research Citation</option>
              </select>
            </div>
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-[10px] uppercase tracking-wider font-extrabold text-slate-450">Content Body</label>
            <textarea
              required
              value={content}
              onChange={e => setContent(e.target.value)}
              placeholder="Paste or write the text contents to securely vault..."
              className="w-full p-4 rounded-xl bg-[#121316] border border-slate-800/80 text-white text-xs outline-none min-h-[100px] resize-y"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-[10px] uppercase tracking-wider font-extrabold text-slate-450">Tags (comma separated)</label>
            <input
              type="text"
              value={tagsInput}
              onChange={e => setTagsInput(e.target.value)}
              placeholder="e.g. Physics, Formula, Exam-Prep"
              className="w-full px-4 py-3 rounded-xl bg-[#121316] border border-slate-800/80 text-white text-xs outline-none focus:border-amber-500 transition-premium"
            />
          </div>

          <div className="flex gap-2 justify-end pt-2">
            <button
              type="button"
              onClick={() => setShowAddForm(false)}
              className="px-4 py-2 border border-slate-800 text-slate-400 hover:text-white rounded-xl text-xs font-bold transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2 bg-amber-600 hover:bg-amber-500 text-white rounded-xl text-xs font-bold transition-premium cursor-pointer shadow-md"
            >
              Save to Vault
            </button>
          </div>
        </form>
      )}

      {/* Filter / Search Bar controls */}
      <div className="flex flex-col md:flex-row gap-4 items-center justify-between pb-2">
        {/* Search */}
        <div className="w-full md:max-w-md relative flex items-center">
          <Search className="w-4 h-4 text-slate-500 absolute left-4 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search notes, highlights, and citations..."
            className="w-full pl-11 pr-4 py-3 rounded-xl bg-slate-900/40 border border-white/5 text-xs text-white placeholder-slate-500 outline-none focus:border-amber-500/50 transition-premium"
          />
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-2 self-start md:self-auto">
          {["Note", "Saved Answer", "Highlight", "Citation"].map(t => (
            <button
              key={t}
              onClick={() => setSelectedType(selectedType === t ? null : t)}
              className={`px-3 py-1.5 rounded-lg border text-[10px] font-black uppercase tracking-wider transition-premium cursor-pointer ${
                selectedType === t
                  ? "bg-amber-950/40 border-amber-500 text-amber-500"
                  : "bg-slate-900/30 border-white/5 text-slate-400 hover:text-slate-200"
              }`}
            >
              {t}s
            </button>
          ))}
        </div>
      </div>

      {/* Tags row */}
      {allUniqueTags.length > 0 && (
        <div className="flex flex-wrap items-center gap-1.5 pl-1">
          <span className="text-[9px] font-black uppercase tracking-widest text-slate-500 mr-2 flex items-center gap-1">
            <Tag className="w-3 h-3" /> Filter Tag:
          </span>
          {allUniqueTags.map(tag => (
            <button
              key={tag}
              onClick={() => setSelectedTag(selectedTag === tag ? null : tag)}
              className={`px-2.5 py-1 rounded-md text-[10px] font-semibold transition-premium cursor-pointer ${
                selectedTag === tag
                  ? "bg-amber-900 text-white"
                  : "bg-slate-900/50 text-slate-400 hover:bg-slate-800/60 hover:text-slate-205"
              }`}
            >
              #{tag}
            </button>
          ))}
        </div>
      )}

      {/* Vault Card Grid layout */}
      {filteredItems.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredItems.map((item) => (
            <div
              key={item.id}
              className="p-5.5 rounded-2xl glass-card flex flex-col justify-between gap-5 group relative overflow-hidden"
            >
              <div className="space-y-4">
                {/* Meta Header */}
                <div className="flex items-center justify-between border-b border-white/5 pb-3">
                  <span className="inline-flex items-center gap-1.5 text-[9px] font-black uppercase tracking-wider text-slate-400">
                    {getTypeIcon(item.type)} {item.type}
                  </span>
                  <button
                    onClick={() => handleDeleteItem(item.id)}
                    className="text-slate-600 hover:text-rose-450 p-1 rounded opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer shrink-0"
                    title="Delete item"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>

                {/* Content */}
                <div className="space-y-2">
                  <h4 className="text-xs font-black text-slate-205 group-hover:text-white transition-colors leading-snug">
                    {item.title}
                  </h4>
                  <p className="text-[11px] text-slate-350 leading-relaxed font-medium whitespace-pre-wrap">
                    {item.content}
                  </p>
                </div>
              </div>

              {/* Tags & Date footer */}
              <div className="flex flex-col gap-2.5 pt-2 border-t border-white/5">
                {item.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {item.tags.map(t => (
                      <span key={t} className="text-[9px] font-bold text-amber-500 bg-amber-950/20 px-2 py-0.5 rounded">
                        #{t}
                      </span>
                    ))}
                  </div>
                )}
                <span className="text-[9px] text-slate-500 font-mono">
                  Saved {new Date(item.created_at).toLocaleDateString("en-IN", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" })}
                </span>
              </div>

            </div>
          ))}
        </div>
      ) : (
        <div className="h-60 flex flex-col items-center justify-center text-center p-8 border border-dashed border-slate-800 rounded-3xl">
          <Bookmark className="w-10 h-10 text-slate-500 mb-3 animate-pulse" />
          <h4 className="text-sm font-bold text-slate-300">No Saved Knowledge Yet</h4>
          <p className="text-xs text-slate-500 max-w-md mx-auto mt-1 font-semibold leading-relaxed">
            The Vault is your personal repository of truth. You can save translations, highlights, citations, and key responses directly from your conversation chats to build a reliable local knowledge base.
          </p>
        </div>
      )}

    </div>
  );
}
