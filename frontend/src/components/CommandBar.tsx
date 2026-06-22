"use client";

import React, { useEffect, useState, useRef } from "react";
import { Search, Plus, Bookmark, Folder, FileText, Globe, X, Terminal } from "lucide-react";

interface CommandBarProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectAction: (action: string) => void;
}

export default function CommandBar({ isOpen, onClose, onSelectAction }: CommandBarProps) {
  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  const commands = [
    { id: "new-chat", label: "New Chat", desc: "Start a fresh companion conversation", icon: Plus, category: "Chat" },
    { id: "ask-yaar", label: "Ask Yaar", desc: "Instantly ask a query", icon: Search, category: "Search" },
    { id: "search-vault", label: "Search Vault", desc: "Browse your second brain snippets", icon: Bookmark, category: "Vault" },
    { id: "open-project", label: "Open Project Binder", desc: "Manage study and research projects", icon: Folder, category: "Projects" },
    { id: "upload-doc", label: "Upload Document", desc: "Analyze and query a PDF file", icon: FileText, category: "Documents" },
    { id: "translate", label: "Translate Text", desc: "Convert text to Indian languages", icon: Globe, category: "Tools" }
  ];

  const filteredCommands = commands.filter(cmd =>
    cmd.label.toLowerCase().includes(query.toLowerCase()) ||
    cmd.desc.toLowerCase().includes(query.toLowerCase()) ||
    cmd.category.toLowerCase().includes(query.toLowerCase())
  );

  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
      setSelectedIndex(0);
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;

      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex(prev => (prev + 1) % filteredCommands.length);
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex(prev => (prev - 1 + filteredCommands.length) % filteredCommands.length);
      } else if (e.key === "Enter") {
        e.preventDefault();
        if (filteredCommands[selectedIndex]) {
          onSelectAction(filteredCommands[selectedIndex].id);
          onClose();
        }
      } else if (e.key === "Escape") {
        e.preventDefault();
        onClose();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, selectedIndex, filteredCommands, onClose, onSelectAction]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        onClose();
      }
    };
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/60 backdrop-blur-sm pt-[15vh] p-4 animate-fade-in">
      <div
        ref={containerRef}
        className="w-full max-w-xl rounded-2xl bg-[#1e1f24] border border-white/5 shadow-2xl overflow-hidden flex flex-col animate-slide-in-right"
      >
        {/* Search header */}
        <div className="flex items-center gap-3 px-4 py-3.5 border-b border-white/5">
          <Terminal className="w-4 h-4 text-amber-500 shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            placeholder="Type a command or search action..."
            className="w-full bg-transparent text-slate-100 placeholder-slate-500 text-xs outline-none"
          />
          <kbd className="hidden sm:inline-block px-1.5 py-0.5 rounded bg-slate-800 text-[10px] text-slate-400 border border-slate-700/60 font-mono">
            ESC
          </kbd>
          <button onClick={onClose} className="p-1 hover:bg-slate-800 rounded-md text-slate-400 hover:text-white shrink-0">
            <X className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Command list */}
        <div className="max-h-[320px] overflow-y-auto p-2 space-y-1">
          {filteredCommands.length > 0 ? (
            filteredCommands.map((cmd, index) => {
              const Icon = cmd.icon;
              const isSelected = index === selectedIndex;

              return (
                <button
                  key={cmd.id}
                  onClick={() => {
                    onSelectAction(cmd.id);
                    onClose();
                  }}
                  className={`w-full p-3 rounded-xl flex items-center justify-between text-left transition-premium cursor-pointer ${
                    isSelected
                      ? "bg-amber-950/30 text-amber-500"
                      : "bg-transparent text-slate-350 hover:bg-slate-850/40 hover:text-slate-105"
                  }`}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <Icon className={`w-4 h-4 shrink-0 ${isSelected ? "text-amber-550" : "text-slate-505"}`} />
                    <div className="min-w-0">
                      <h4 className="text-xs font-bold leading-normal">{cmd.label}</h4>
                      <p className="text-[10px] text-slate-500 font-medium leading-normal mt-0.5">{cmd.desc}</p>
                    </div>
                  </div>
                  <span className="text-[9px] font-black uppercase text-slate-500 bg-slate-950/40 border border-slate-900 px-1.5 py-0.5 rounded shrink-0">
                    {cmd.category}
                  </span>
                </button>
              );
            })
          ) : (
            <div className="p-6 text-center text-xs text-slate-500 font-medium">
              No actions found matching "{query}"
            </div>
          )}
        </div>

        {/* Footer shortcuts helper */}
        <div className="px-4 py-2 border-t border-white/5 bg-slate-950/20 text-[9px] text-slate-500 font-bold uppercase tracking-wider flex items-center justify-between">
          <span>Use arrows to navigate</span>
          <span>Enter to trigger</span>
        </div>

      </div>
    </div>
  );
}
