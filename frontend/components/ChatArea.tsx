"use client";

import React, { useState } from "react";
import {
  AlertCircle,
  AlertTriangle,
  ArrowUp,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Copy,
  Download,
  Eraser,
  FileText,
  Save,
  X,
} from "lucide-react";
import { useDocs } from "@/lib/doc-context";

export function ChatArea() {
  const {
    documents,
    totalPages,
    passageCount,
    previewPages,
    messages,
    consent,
    indexed,
    providerChanged,
    cleanupBlocked,
    savedWorkspaceId,
    chatSaveError,
    workspaceNotice,
    statusError,
    isAsking,
    isWorkspaceBusy,
    sendQuestion,
    clearChatOnly,
    downloadChat,
    retrySaveChat,
    openEvidence,
    clearNotices,
  } = useDocs();

  const [input, setInput] = useState("");
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [previewExpanded, setPreviewExpanded] = useState(true);

  const blocked = cleanupBlocked || providerChanged;
  const chatEnabled = indexed && consent && !blocked;

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!chatEnabled || isAsking || !input.trim()) return;
    const text = input;
    setInput("");
    await sendQuestion(text);
  };

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const renderStatusBanner = () => {
    if (cleanupBlocked) {
      return (
        <div className="p-3 rounded-xl bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900/40 text-red-700 dark:text-red-400 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>Session paused: reset or restart the server to finish cleanup.</span>
        </div>
      );
    }
    if (providerChanged) {
      return (
        <div className="p-3 rounded-xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/40 text-amber-800 dark:text-amber-300 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>AI configuration changed. Reset and re-index your documents before continuing.</span>
        </div>
      );
    }
    if (indexed && consent) {
      return (
        <div className="p-3 rounded-xl bg-[#EAF4EF] dark:bg-[#1A3831] border border-[#C8E2D5] dark:border-[#274F44] text-[#147D65] dark:text-[#4ADE80] text-xs flex items-center gap-2 font-medium">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>Documents indexed. You can ask questions below.</span>
        </div>
      );
    }
    if (indexed && !consent) {
      return (
        <div className="p-3 rounded-xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/40 text-amber-800 dark:text-amber-300 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>Chat paused. Enable processing consent in the sidebar to continue.</span>
        </div>
      );
    }
    return (
      <div className="p-3 rounded-xl bg-white dark:bg-[#162E29] border border-[#E5EBE8] dark:border-[#26483F] text-[#5C7069] dark:text-[#9FB1AA] text-xs">
        {savedWorkspaceId
          ? "Saved workspace opened. Review restored answers below or enable consent and select Index documents to ask new questions."
          : "Start in the sidebar: upload PDFs, preview their pages locally, then index when API access is available."}
      </div>
    );
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-[#F6F8F7] dark:bg-[#10221F] transition-colors duration-200">
      {/* Main Scroll Area */}
      <div className="flex-1 overflow-y-auto px-4 sm:px-8 lg:px-12 py-6 space-y-5">
        <div className="max-w-3xl mx-auto space-y-4">
          {/* Top Metrics Strip on smaller viewports + primary status */}
          <div className="grid grid-cols-3 gap-3 lg:hidden">
            <div className="p-3 rounded-xl bg-white dark:bg-[#162E29] border border-[#E5EBE8] dark:border-[#26483F]">
              <div className="text-[11px] text-[#6B7C77] dark:text-[#94A7A1]">Indexed docs</div>
              <div className="text-base font-bold text-[#172B28] dark:text-[#F2F7F5]">
                {indexed ? documents.length : 0}
              </div>
            </div>
            <div className="p-3 rounded-xl bg-white dark:bg-[#162E29] border border-[#E5EBE8] dark:border-[#26483F]">
              <div className="text-[11px] text-[#6B7C77] dark:text-[#94A7A1]">Passages</div>
              <div className="text-base font-bold text-[#172B28] dark:text-[#F2F7F5]">
                {passageCount}
              </div>
            </div>
            <div className="p-3 rounded-xl bg-white dark:bg-[#162E29] border border-[#E5EBE8] dark:border-[#26483F]">
              <div className="text-[11px] text-[#6B7C77] dark:text-[#94A7A1]">Responses</div>
              <div className="text-base font-bold text-[#172B28] dark:text-[#F2F7F5]">
                {messages.filter((m) => m.role === "assistant").length}
              </div>
            </div>
          </div>

          {renderStatusBanner()}

          {/* Chat-save warning + retry */}
          {chatSaveError && (
            <div className="p-3 rounded-xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/40 text-amber-800 dark:text-amber-300 text-xs flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                <span>{chatSaveError} Use Save chat now to retry before leaving.</span>
              </div>
              <button
                type="button"
                onClick={retrySaveChat}
                disabled={blocked || isWorkspaceBusy}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-amber-600 text-white font-medium text-[11px] hover:bg-amber-700 disabled:opacity-50"
              >
                <Save className="w-3 h-3" />
                <span>Save chat now</span>
              </button>
            </div>
          )}

          {/* Error or notice alerts */}
          {statusError && (
            <div className="p-3 rounded-xl bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900/40 text-red-700 dark:text-red-400 text-xs flex items-start justify-between gap-2">
              <div className="flex items-start gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{statusError}</span>
              </div>
              <button type="button" onClick={clearNotices} aria-label="Dismiss error">
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          {workspaceNotice && (
            <div className="p-3 rounded-xl bg-[#EAF4EF] dark:bg-[#1A3831] border border-[#C8E2D5] dark:border-[#274F44] text-[#147D65] dark:text-[#4ADE80] text-xs flex items-start justify-between gap-2">
              <div className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{workspaceNotice}</span>
              </div>
              <button type="button" onClick={clearNotices} aria-label="Dismiss notice">
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          {/* Local Page Preview (Zero AI Calls) */}
          {previewPages.length > 0 && (
            <div className="rounded-2xl bg-white dark:bg-[#162E29] border border-[#E5EBE8] dark:border-[#26483F] shadow-xs overflow-hidden">
              <button
                type="button"
                onClick={() => setPreviewExpanded(!previewExpanded)}
                className="w-full px-5 py-3.5 flex items-center justify-between text-left border-b border-[#E5EBE8] dark:border-[#22423B]"
              >
                <div>
                  <div className="text-xs font-bold text-[#172B28] dark:text-[#F2F7F5]">
                    Local page preview — not indexed ({previewPages.length} pages · {totalPages} total)
                  </div>
                  <div className="text-[11px] text-[#6B7C77] dark:text-[#94A7A1] mt-0.5">
                    Text is limited to 1,500 characters per page. Changing selected files clears this preview.
                  </div>
                </div>
                {previewExpanded ? <ChevronUp className="w-4 h-4 text-[#6B7C77]" /> : <ChevronDown className="w-4 h-4 text-[#6B7C77]" />}
              </button>

              {previewExpanded && (
                <div className="p-4 max-h-96 overflow-y-auto space-y-4">
                  {previewPages.map((p) => (
                    <div
                      key={`${p.filename}-${p.page}`}
                      className="p-3.5 rounded-xl bg-[#F6F8F7] dark:bg-[#122420] border border-[#E5EBE8] dark:border-[#25463D] space-y-1.5"
                    >
                      <div className="text-[11px] font-semibold text-[#147D65] dark:text-[#4ADE80]">
                        {p.filename} · PDF page {p.page}
                      </div>
                      <pre className="text-xs text-[#172B28] dark:text-[#E2EBE7] whitespace-pre-wrap font-sans leading-relaxed">
                        {p.text}
                      </pre>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Chat Controls (Clear / Download) */}
          {messages.length > 0 && (
            <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={clearChatOnly}
                  disabled={blocked}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-[#E5EBE8] dark:border-[#26483F] bg-white dark:bg-[#162E29] hover:bg-[#F6F8F7] dark:hover:bg-[#1C3831] disabled:opacity-45 text-xs font-medium text-[#172B28] dark:text-[#F2F7F5]"
                >
                  <Eraser className="w-3.5 h-3.5" />
                  <span>Clear chat only</span>
                </button>
                <button
                  type="button"
                  onClick={downloadChat}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-[#E5EBE8] dark:border-[#26483F] bg-white dark:bg-[#162E29] hover:bg-[#F6F8F7] dark:hover:bg-[#1C3831] text-xs font-medium text-[#172B28] dark:text-[#F2F7F5]"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download chat and sources</span>
                </button>
              </div>
              <span className="text-[11px] text-[#6B7C77] dark:text-[#94A7A1]">
                Clear chat keeps documents indexed.
              </span>
            </div>
          )}

          {/* Empty State Hero vs Conversation Messages */}
          {messages.length === 0 ? (
            <div className="py-12 flex flex-col items-center text-center space-y-4">
              <div className="w-11 h-11 rounded-xl bg-[#147D65] flex items-center justify-center text-white shadow-sm">
                <FileText className="w-5 h-5" />
              </div>
              <h2 className="text-2xl font-semibold tracking-tight text-[#172B28] dark:text-[#F2F7F5]">
                Ask your documents. Inspect the supporting pages.
              </h2>
              <p className="text-xs text-[#6B7C77] dark:text-[#94A7A1] max-w-md leading-relaxed">
                References use physical PDF page numbers starting at 1. Check the cited text before relying on an answer.
              </p>
            </div>
          ) : (
            <div className="space-y-5">
              {messages.map((msg) => (
                <div key={msg.id}>
                  {msg.role === "user" ? (
                    <div className="p-4 rounded-2xl bg-white dark:bg-[#162E29] border border-[#E5EBE8] dark:border-[#26483F] shadow-xs">
                      <div className="text-[11px] font-semibold uppercase tracking-wider text-[#6B7C77] dark:text-[#94A7A1] mb-1">
                        You
                      </div>
                      <p className="text-sm font-medium text-[#172B28] dark:text-[#F2F7F5] whitespace-pre-wrap">
                        {msg.content}
                      </p>
                    </div>
                  ) : (
                    <div className="p-5 rounded-2xl bg-white dark:bg-[#162E29] border border-[#E5EBE8] dark:border-[#26483F] shadow-xs space-y-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="w-6 h-6 rounded-md bg-[#147D65] flex items-center justify-center text-white">
                            <FileText className="w-3.5 h-3.5" />
                          </div>
                          <span className="text-xs font-bold text-[#172B28] dark:text-[#F2F7F5]">
                            DocMind
                          </span>
                          <span className="text-xs text-[#6B7C77] dark:text-[#94A7A1]">
                            Grounded answer
                          </span>
                        </div>
                        {msg.latency && (
                          <span className="text-[11px] text-[#6B7C77] dark:text-[#94A7A1]">
                            {msg.latency}
                          </span>
                        )}
                      </div>

                      {msg.status === "conflict" && (
                        <div className="p-3 rounded-xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/40 text-amber-800 dark:text-amber-300 text-xs flex items-center gap-2 font-medium">
                          <AlertTriangle className="w-4 h-4 shrink-0" />
                          <span>The documents contain conflicting information. Compare cited sources carefully.</span>
                        </div>
                      )}

                      {msg.claims && msg.claims.length > 0 ? (
                        <div className="space-y-3">
                          {msg.claims.map((claim, cIdx) => (
                            <div key={cIdx} className="text-sm text-[#172B28] dark:text-[#E2EBE7] leading-relaxed">
                              <span>{claim.text}</span>
                              {claim.refs.length > 0 && (
                                <span className="inline-flex flex-wrap gap-1.5 ml-2 align-middle">
                                  {claim.refs.map((ref, rIdx) => (
                                    <button
                                      key={rIdx}
                                      type="button"
                                      onClick={() => {
                                        if (!msg.sources) return;
                                        const matchIdx = msg.sources.findIndex(
                                          (s) => s.filename === ref.filename && s.page === ref.page
                                        );
                                        openEvidence(msg.sources, matchIdx >= 0 ? matchIdx : 0);
                                      }}
                                      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-medium bg-[#EAF4EF] dark:bg-[#1C3E36] text-[#147D65] dark:text-[#4ADE80] border border-[#C8E2D5] dark:border-[#2A5247] hover:bg-[#D8EBE1]"
                                    >
                                      {ref.filename} · p. {ref.page}
                                    </button>
                                  ))}
                                </span>
                              )}
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-[#172B28] dark:text-[#E2EBE7] leading-relaxed whitespace-pre-wrap">
                          {msg.content}
                        </p>
                      )}

                      {/* Deduplicated Citation Pills */}
                      {msg.sources && msg.sources.length > 0 && (
                        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-[#E5EBE8] dark:border-[#22423B]">
                          {msg.sources.map((src, sIdx) => (
                            <button
                              key={`${src.filename}-${src.page}-${sIdx}`}
                              type="button"
                              onClick={() => openEvidence(msg.sources || [], sIdx)}
                              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium bg-[#EAF4EF] dark:bg-[#1C3E36] text-[#147D65] dark:text-[#4ADE80] border border-[#C8E2D5] dark:border-[#2A5247] hover:bg-[#D8EBE1] transition-colors"
                            >
                              <FileText className="w-3 h-3" />
                              <span>
                                {src.filename} · Page {src.page}
                              </span>
                            </button>
                          ))}
                        </div>
                      )}

                      {/* Copy footer */}
                      <div className="flex items-center justify-between pt-1 text-xs text-[#6B7C77] dark:text-[#94A7A1]">
                        <button
                          type="button"
                          onClick={() => handleCopy(msg.id, msg.content)}
                          className="inline-flex items-center gap-1 hover:text-[#172B28] dark:hover:text-white transition-colors"
                        >
                          {copiedId === msg.id ? (
                            <Check className="w-3.5 h-3.5 text-[#147D65] dark:text-[#4ADE80]" />
                          ) : (
                            <Copy className="w-3.5 h-3.5" />
                          )}
                          <span>{copiedId === msg.id ? "Copied" : "Copy"}</span>
                        </button>

                        {msg.sources && msg.sources.length > 0 && (
                          <button
                            type="button"
                            onClick={() => openEvidence(msg.sources || [], 0)}
                            className="text-xs font-medium text-[#147D65] dark:text-[#4ADE80] hover:underline"
                          >
                            View supporting passages ({msg.sources.length})
                          </button>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))}

              {isAsking && (
                <div className="p-4 rounded-2xl bg-white dark:bg-[#162E29] border border-[#E5EBE8] dark:border-[#26483F] text-xs text-[#5C7069] dark:text-[#9FB1AA] animate-pulse">
                  Finding supporting passages…
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Bottom Sticky Chat Input */}
      <div className="px-4 sm:px-8 lg:px-12 pb-5 pt-2 bg-[#F6F8F7] dark:bg-[#10221F] border-t border-[#E5EBE8] dark:border-[#22423B]">
        <div className="max-w-3xl mx-auto">
          <form
            onSubmit={handleSubmit}
            className="rounded-2xl bg-white dark:bg-[#162E29] border border-[#E5EBE8] dark:border-[#26483F] shadow-xs p-3 focus-within:ring-2 focus-within:ring-[#147D65] dark:focus-within:ring-[#4ADE80] transition-all flex items-end gap-2"
          >
            <textarea
              value={input}
              disabled={!chatEnabled || isAsking}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit();
                }
              }}
              rows={2}
              maxLength={2000}
              placeholder={
                chatEnabled
                  ? "Ask about your indexed PDFs"
                  : !indexed
                  ? "Index PDFs in the sidebar to enable chat"
                  : !consent
                  ? "Enable processing consent in the sidebar to ask questions"
                  : "Reset session before continuing"
              }
              className="flex-1 bg-transparent resize-none border-0 text-sm text-[#172B28] dark:text-[#F2F7F5] placeholder-[#8A9C96] focus:outline-hidden px-1 disabled:opacity-50"
            />

            <button
              type="submit"
              disabled={!chatEnabled || isAsking || !input.trim()}
              aria-label="Send question"
              className="w-8 h-8 rounded-lg bg-[#147D65] hover:bg-[#0E634F] disabled:opacity-40 text-white flex items-center justify-center transition-colors shrink-0"
            >
              <ArrowUp className="w-4 h-4 stroke-[2.5]" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
