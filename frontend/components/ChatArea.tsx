"use client";

import React, { useState } from "react";
import {
  ArrowUp,
  Paperclip,
  FileText,
  Copy,
  RotateCcw,
  ThumbsUp,
  ThumbsDown,
  Sparkles,
  Check,
  Columns,
  ListFilter,
  Layers,
} from "lucide-react";
import { useDocs } from "@/lib/doc-context";
import { InlineCitation } from "@/lib/types";

export function ChatArea() {
  const {
    messages,
    documents,
    selectedDocNames,
    sendMessage,
    openEvidence,
    uploadRealFiles,
    isUploading,
  } = useDocs();
  const [input, setInput] = useState("");
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const handleFiles = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    uploadRealFiles(Array.from(files));
  };

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim()) return;
    const text = input;
    setInput("");
    sendMessage(text);
  };

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleCitationClick = (citation: InlineCitation) => {
    openEvidence({
      docTitle: citation.docName.replace(/\.[^/.]+$/, ""),
      page: parseInt(citation.pages.replace(/\D/g, "")) || 1,
      heading: `Passage from ${citation.docName}`,
      highlightSnippet: citation.highlightText,
      fullText: citation.fullSnippet || citation.highlightText,
    });
  };

  const promptCards = [
    {
      icon: Layers,
      title: "See the bigger picture",
      desc: "Turn your uploaded documents into clear, concise summaries.",
      query: "Summarize the key findings and goals from the uploaded documents.",
    },
    {
      icon: ListFilter,
      title: "Find the details that matter",
      desc: "Extract key dates, metrics, numbers and action items.",
      query: "What are the most critical dates, figures, and deliverables mentioned?",
    },
    {
      icon: Columns,
      title: "Connect the dots",
      desc: "Compare findings, identify patterns and verify source citations.",
      query: "Compare the key themes and findings across the indexed files.",
    },
  ];

  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden bg-[#F6F8F7] dark:bg-[#10221F] transition-colors duration-200">
      {/* Sub-header meta */}
      <div className="px-8 py-3 flex items-center justify-between border-b border-[#E5EBE8] dark:border-[#22423B] bg-white/70 dark:bg-[#132723]/70 backdrop-blur-sm">
        <div className="flex items-center gap-2">
          <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-[#EAF4EF] dark:bg-[#1A3831] text-[#147D65] dark:text-[#4ADE80]">
            {selectedDocNames.length} {selectedDocNames.length === 1 ? "document" : "documents"} selected
          </span>
        </div>
        <div className="text-xs text-[#6B7C77] dark:text-[#94A7A1]">
          {documents.length > 0 ? "Knowledge Base Connected" : "No documents attached"}
        </div>
      </div>

      {/* Main chat view or empty state */}
      <div className="flex-1 overflow-y-auto px-6 lg:px-16 py-8 space-y-8">
        {messages.length === 0 ? (
          /* Real Empty State */
          <div className="max-w-3xl mx-auto flex flex-col items-center justify-center min-h-[60vh] text-center pt-8">
            <div className="w-12 h-12 rounded-xl bg-[#147D65] flex items-center justify-center text-white mb-6 shadow-sm">
              <FileText className="w-6 h-6 stroke-[2]" />
            </div>

            <div className="text-[11px] font-semibold uppercase tracking-widest text-[#147D65] dark:text-[#4ADE80] mb-3">
              YOUR DOCUMENTS. CONNECTED.
            </div>

            <h1 className="text-3xl lg:text-4xl font-semibold tracking-tight text-[#172B28] dark:text-[#F2F7F5] max-w-xl">
              What would you like to know about your documents?
            </h1>

            {/* 3 Prompt Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full mt-12 text-left">
              {promptCards.map((card) => {
                const Icon = card.icon;
                return (
                  <div
                    key={card.title}
                    onClick={() => {
                      setInput(card.query);
                    }}
                    className="p-5 rounded-2xl bg-white dark:bg-[#162E29] border border-[#E5EBE8] dark:border-[#26483F] shadow-xs hover:border-[#147D65] dark:hover:border-[#4ADE80] cursor-pointer transition-all group"
                  >
                    <div className="w-8 h-8 rounded-lg bg-[#EAF4EF] dark:bg-[#1E3B33] flex items-center justify-center text-[#147D65] dark:text-[#4ADE80] mb-3 group-hover:scale-105 transition-transform">
                      <Icon className="w-4 h-4" />
                    </div>
                    <h3 className="font-semibold text-sm text-[#172B28] dark:text-[#F2F7F5] mb-1">
                      {card.title}
                    </h3>
                    <p className="text-xs text-[#6B7C77] dark:text-[#94A7A1] leading-relaxed">
                      {card.desc}
                    </p>
                  </div>
                );
              })}
            </div>

            {/* Recently added real files pills */}
            {documents.length > 0 && (
              <div className="mt-8 flex flex-wrap items-center justify-center gap-2 text-xs">
                <span className="text-[#8A9C96] text-[11px] uppercase tracking-wider font-semibold mr-1">
                  Indexed sources:
                </span>
                {documents.slice(0, 4).map((d) => (
                  <span
                    key={d.id}
                    className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-white dark:bg-[#162E29] border border-[#E5EBE8] dark:border-[#26483F] text-xs text-[#172B28] dark:text-[#F2F7F5]"
                  >
                    <FileText className="w-3 h-3 text-[#147D65] dark:text-[#4ADE80]" />
                    <span>{d.name}</span>
                  </span>
                ))}
              </div>
            )}
          </div>
        ) : (
          /* Message Stream */
          <div className="max-w-3xl mx-auto space-y-6">
            {messages.map((msg) => (
              <div key={msg.id} className="space-y-4">
                {msg.role === "user" ? (
                  /* User Prompt Card */
                  <div className="p-5 rounded-2xl bg-white dark:bg-[#162E29] border border-[#E5EBE8] dark:border-[#26483F] shadow-xs space-y-3">
                    <h2 className="text-base font-semibold text-[#172B28] dark:text-[#F2F7F5]">
                      {msg.content}
                    </h2>
                    {msg.selectedDocs && msg.selectedDocs.length > 0 && (
                      <div className="flex flex-wrap items-center gap-2 pt-1">
                        {msg.selectedDocs.map((doc) => (
                          <span
                            key={doc}
                            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-[#F6F8F7] dark:bg-[#1E3B33] text-[#4A5D57] dark:text-[#AFC1B9] border border-[#E5EBE8] dark:border-[#2A4C41]"
                          >
                            <FileText className="w-3 h-3 text-[#147D65] dark:text-[#4ADE80]" />
                            {doc}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ) : (
                  /* DocuMind Response Card */
                  <div className="p-6 rounded-2xl bg-white dark:bg-[#162E29] border border-[#E5EBE8] dark:border-[#26483F] shadow-xs space-y-5">
                    {/* Header */}
                    <div className="flex items-center gap-2">
                      <div className="w-6 h-6 rounded-md bg-[#147D65] flex items-center justify-center text-white">
                        <FileText className="w-3.5 h-3.5" />
                      </div>
                      <span className="text-xs font-bold text-[#172B28] dark:text-[#F2F7F5]">
                        DocuMind
                      </span>
                      <span className="text-xs text-[#6B7C77] dark:text-[#94A7A1]">
                        Grounded in your documents
                      </span>
                    </div>

                    {/* Summary intro */}
                    <p className="text-sm font-medium text-[#172B28] dark:text-[#E2EBE7] leading-relaxed whitespace-pre-line">
                      {msg.content}
                    </p>

                    {/* Structured Key Points */}
                    {msg.points && msg.points.length > 0 && (
                      <div className="space-y-4 pt-1">
                        <div className="space-y-3">
                          {msg.points.map((pt) => (
                            <div key={pt.num} className="text-xs space-y-1">
                              <span className="font-bold text-[#147D65] dark:text-[#4ADE80] mr-2">
                                {pt.num}
                              </span>
                              <span className="font-semibold text-[#172B28] dark:text-[#F2F7F5] mr-1.5">
                                {pt.title}
                              </span>
                              <span className="text-[#4A5D57] dark:text-[#AFC1B9] leading-relaxed">
                                {pt.body}
                              </span>
                              {pt.citationId && (
                                <span className="ml-1 px-1.5 py-0.5 rounded text-[10px] font-semibold bg-[#EAF4EF] dark:bg-[#1A3831] text-[#147D65] dark:text-[#4ADE80]">
                                  [{pt.citationId}]
                                </span>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Bottom Citation Pills */}
                    {msg.citations && msg.citations.length > 0 && (
                      <div className="flex flex-wrap items-center gap-2 pt-2">
                        {msg.citations.map((cite) => (
                          <button
                            key={cite.id}
                            onClick={() => handleCitationClick(cite)}
                            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-[#EAF4EF] dark:bg-[#1C3E36] text-[#147D65] dark:text-[#4ADE80] border border-[#C8E2D5] dark:border-[#2A5247] hover:bg-[#D9EFE3] transition-colors"
                          >
                            <FileText className="w-3 h-3" />
                            <span>{cite.label}</span>
                          </button>
                        ))}
                      </div>
                    )}

                    {/* Bottom action row */}
                    <div className="flex items-center justify-between pt-3 border-t border-[#E5EBE8] dark:border-[#22423B] text-xs text-[#6B7C77] dark:text-[#94A7A1]">
                      <div className="flex items-center gap-3">
                        <button
                          onClick={() => handleCopy(msg.id, msg.content)}
                          className="flex items-center gap-1 hover:text-[#172B28] dark:hover:text-white transition-colors"
                        >
                          {copiedId === msg.id ? (
                            <Check className="w-3.5 h-3.5 text-green-600" />
                          ) : (
                            <Copy className="w-3.5 h-3.5" />
                          )}
                          <span>{copiedId === msg.id ? "Copied" : "Copy"}</span>
                        </button>
                        <button
                          onClick={() => sendMessage(msg.content)}
                          className="flex items-center gap-1 hover:text-[#172B28] dark:hover:text-white transition-colors"
                        >
                          <RotateCcw className="w-3.5 h-3.5" />
                          <span>Regenerate</span>
                        </button>
                        <button className="hover:text-[#172B28] dark:hover:text-white transition-colors">
                          <ThumbsUp className="w-3.5 h-3.5" />
                        </button>
                        <button className="hover:text-[#172B28] dark:hover:text-white transition-colors">
                          <ThumbsDown className="w-3.5 h-3.5" />
                        </button>
                      </div>

                      <div>
                        {msg.groundingSources || 0} sources • {msg.latency || "0.8s"}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Bottom Sticky Input Container */}
      <div className="px-6 lg:px-16 pb-6 pt-2 bg-[#F6F8F7] dark:bg-[#10221F]">
        <div className="max-w-3xl mx-auto">
          {/* Main Input Box */}
          <form
            onSubmit={handleSubmit}
            className="rounded-2xl bg-white dark:bg-[#162E29] border border-[#E5EBE8] dark:border-[#26483F] shadow-sm p-3 focus-within:ring-2 focus-within:ring-[#147D65] dark:focus-within:ring-[#4ADE80] transition-all"
          >
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit();
                }
              }}
              rows={2}
              placeholder={
                documents.length > 0
                  ? "Ask anything about your documents..."
                  : "Attach a PDF or ask general document queries..."
              }
              className="w-full bg-transparent resize-none border-0 text-sm text-[#172B28] dark:text-[#F2F7F5] placeholder-[#8A9C96] focus:outline-hidden px-1"
            />

            <div className="flex items-center justify-between pt-2 border-t border-[#F1F5F3] dark:border-[#1E3B33]">
              <input
                type="file"
                ref={fileInputRef}
                onChange={(e) => handleFiles(e.target.files)}
                multiple
                accept=".pdf,.docx,.txt"
                className="hidden"
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={isUploading}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-[#4A5D57] dark:text-[#AFC1B9] hover:bg-[#F6F8F7] dark:hover:bg-[#1E3B33] transition-colors"
              >
                <Paperclip className="w-3.5 h-3.5" />
                <span>{isUploading ? "Indexing into Chroma..." : "+ Attach documents"}</span>
              </button>

              <button
                type="submit"
                disabled={!input.trim()}
                className="w-8 h-8 rounded-lg bg-[#147D65] hover:bg-[#0E634F] disabled:opacity-40 text-white flex items-center justify-center transition-colors shadow-xs"
              >
                <ArrowUp className="w-4 h-4 stroke-[2.5]" />
              </button>
            </div>
          </form>

          {/* Bottom Grounding Subtext */}
          <div className="flex items-center justify-center gap-2 mt-2 text-[11px] text-[#8A9C96] dark:text-[#738C84]">
            <Sparkles className="w-3 h-3 text-[#147D65] dark:text-[#4ADE80]" />
            <span>Answers grounded in your sources. Always verify important information.</span>
          </div>
        </div>
      </div>
    </div>
  );
}
