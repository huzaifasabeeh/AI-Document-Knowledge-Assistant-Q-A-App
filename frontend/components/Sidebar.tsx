"use client";

import React, { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import {
  ChevronDown,
  ChevronUp,
  FileText,
  FolderOpen,
  Info,
  LogOut,
  RefreshCw,
  RotateCcw,
  Save,
  Trash2,
  UploadCloud,
  X,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { useDocs } from "@/lib/doc-context";

interface SidebarProps {
  mobileOpen?: boolean;
  onCloseMobile?: () => void;
}

export function Sidebar({ mobileOpen = false, onCloseMobile }: SidebarProps) {
  const router = useRouter();
  const { user, health, logout } = useAuth();
  const {
    selectedFiles,
    documents,
    totalPages,
    consent,
    indexed,
    providerChanged,
    cleanupBlocked,
    savedWorkspaceId,
    workspaces,
    messages,
    isPreviewing,
    isIndexing,
    isResetting,
    isWorkspaceBusy,
    sessionId,
    setConsent,
    selectFiles,
    runPreview,
    runIndex,
    resetWorkspace,
    refreshWorkspaces,
    saveNewWorkspace,
    openSavedWorkspace,
    deleteSavedWorkspace,
  } = useDocs();

  const fileInputRef = useRef<HTMLInputElement>(null);
  const [showDataInfo, setShowDataInfo] = useState(false);
  const [showSavedPanel, setShowSavedPanel] = useState(false);
  const [workspaceTitle, setWorkspaceTitle] = useState("");
  const [chosenWorkspaceId, setChosenWorkspaceId] = useState("");
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const blocked = cleanupBlocked || providerChanged;
  const uploadDisabled = indexed || blocked || Boolean(savedWorkspaceId);
  const aiLabel = health?.ai?.label || "the configured AI provider";
  const aiReady = Boolean(health?.ai?.ready);
  const hasSelection = selectedFiles.length > 0 || (Boolean(sessionId) && documents.length > 0);

  const effectiveWorkspaceId = workspaces.some((w) => w.id === chosenWorkspaceId)
    ? chosenWorkspaceId
    : workspaces[0]?.id || "";
  const selectedSaved = workspaces.find((w) => w.id === effectiveWorkspaceId) || null;
  const canOpenSaved =
    !indexed &&
    !blocked &&
    selectedFiles.length === 0 &&
    messages.length === 0 &&
    !savedWorkspaceId &&
    Boolean(selectedSaved && selectedSaved.status === "ready") &&
    !isWorkspaceBusy;

  const handleLogout = async () => {
    if (isLoggingOut) return;
    setIsLoggingOut(true);
    try {
      await logout();
      router.replace("/login");
    } finally {
      setIsLoggingOut(false);
    }
  };

  const handleSaveWorkspace = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!workspaceTitle.trim()) return;
    await saveNewWorkspace(workspaceTitle);
    setWorkspaceTitle("");
  };

  const content = (
    <aside className="w-72 lg:w-80 flex-shrink-0 border-r border-[#E5EBE8] dark:border-[#22423B] bg-white dark:bg-[#132723] flex flex-col justify-between h-full overflow-y-auto transition-colors duration-200">
      <div className="p-4 space-y-4">
        {/* Brand Row */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#147D65] flex items-center justify-center text-white shadow-xs">
              <FileText className="w-4 h-4 stroke-[2.5]" />
            </div>
            <span className="font-semibold text-base tracking-tight text-[#172B28] dark:text-[#F2F7F5]">
              DocMind
            </span>
          </div>
          {onCloseMobile && (
            <button
              type="button"
              onClick={onCloseMobile}
              aria-label="Close sidebar"
              className="md:hidden p-1.5 rounded-lg text-[#6B7C77] hover:bg-[#F6F8F7] dark:hover:bg-[#1A3831]"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Reset documents and chat */}
        <div className="space-y-1.5">
          <p className="text-[11px] text-[#6B7C77] dark:text-[#94A7A1]">
            Text PDFs · up to 10 files · 10 MB each · 200 pages total
          </p>
          <button
            type="button"
            onClick={resetWorkspace}
            disabled={isResetting}
            className="w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded-xl bg-[#EAF4EF] dark:bg-[#1A3831] text-[#147D65] dark:text-[#4ADE80] font-semibold text-xs hover:bg-[#D8EBE1] dark:hover:bg-[#23473E] disabled:opacity-50 transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>{isResetting ? "Resetting…" : "Reset documents and chat"}</span>
          </button>
        </div>

        {/* Data usage disclosure */}
        <div className="rounded-xl border border-[#E5EBE8] dark:border-[#25463D] bg-[#FAFCFB] dark:bg-[#172E29]">
          <button
            type="button"
            onClick={() => setShowDataInfo(!showDataInfo)}
            className="w-full px-3 py-2 flex items-center justify-between text-xs font-medium text-[#172B28] dark:text-[#E2EBE7]"
          >
            <span className="flex items-center gap-1.5">
              <Info className="w-3.5 h-3.5 text-[#147D65] dark:text-[#4ADE80]" />
              <span>How your data is used</span>
            </span>
            {showDataInfo ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
          {showDataInfo && (
            <div className="px-3 pb-3 pt-1 text-[11px] text-[#5C7069] dark:text-[#9FB1AA] space-y-2 border-t border-[#E5EBE8] dark:border-[#22423B]">
              <p>
                Uploads are processed on the app server. Saving a workspace stores PDFs and chat in your account; AI indexing requires the consent below.
              </p>
              <p>
                Indexing sends extracted text to {aiLabel} for embeddings. Questions and retrieved passages are sent there for answers. Only upload documents you are authorized to process.
              </p>
              <p>
                Reset clears this app&apos;s active index and chat. Provider retention is separate. Closing the browser does not guarantee immediate cleanup; restart the server to clear ephemeral state.
              </p>
            </div>
          )}
        </div>

        {/* PDF Uploader */}
        <div className="space-y-2">
          <div className="text-xs font-semibold text-[#172B28] dark:text-[#F2F7F5]">
            Upload PDFs
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,application/pdf"
            multiple
            disabled={uploadDisabled}
            onChange={(e) => {
              const list = e.target.files ? Array.from(e.target.files) : [];
              selectFiles(list);
              e.target.value = "";
            }}
            className="hidden"
          />
          <div
            onDragOver={(e) => {
              e.preventDefault();
            }}
            onDrop={(e) => {
              e.preventDefault();
              if (uploadDisabled) return;
              const list = e.dataTransfer.files ? Array.from(e.dataTransfer.files) : [];
              selectFiles(list);
            }}
            onClick={() => {
              if (!uploadDisabled) fileInputRef.current?.click();
            }}
            className={`border-2 border-dashed rounded-xl p-4 text-center transition-colors ${
              uploadDisabled
                ? "border-[#E5EBE8] dark:border-[#22423B] bg-[#F6F8F7] dark:bg-[#122420] opacity-60 cursor-not-allowed"
                : "border-[#147D65]/40 dark:border-[#4ADE80]/30 hover:border-[#147D65] bg-[#FAFCFB] dark:bg-[#122420] cursor-pointer"
            }`}
          >
            <UploadCloud className="w-5 h-5 mx-auto text-[#147D65] dark:text-[#4ADE80] mb-1.5" />
            <div className="text-xs font-medium text-[#172B28] dark:text-[#F2F7F5]">
              {uploadDisabled ? "Document set locked" : "Drop PDFs here or browse"}
            </div>
            <div className="text-[11px] text-[#6B7C77] dark:text-[#94A7A1] mt-0.5">
              PDF only · max 10 MB per file
            </div>
          </div>

          {(indexed || savedWorkspaceId) && (
            <p className="text-[11px] text-[#6B7C77] dark:text-[#94A7A1]">
              Reset before changing this workspace&apos;s document set. Saved copies remain in your account.
            </p>
          )}

          {/* Selected / Restored / Indexed files list */}
          {documents.length > 0 && (
            <div className="space-y-1 pt-1">
              <div className="text-[11px] font-medium text-[#5C7069] dark:text-[#9FB1AA]">
                {indexed
                  ? `Indexed files (${documents.length} · ${totalPages} pages)`
                  : `${documents.length} file(s) selected — not yet indexed`}
              </div>
              <div className="max-h-28 overflow-y-auto space-y-1">
                {documents.map((doc) => (
                  <div
                    key={doc.name}
                    className="flex items-center justify-between gap-2 px-2.5 py-1.5 rounded-lg bg-[#F6F8F7] dark:bg-[#172E29] border border-[#E5EBE8] dark:border-[#25463D] text-[11px]"
                  >
                    <span className="truncate font-medium text-[#172B28] dark:text-[#F2F7F5]">
                      {doc.name}
                    </span>
                    <span className="text-[#6B7C77] dark:text-[#94A7A1] shrink-0">
                      {doc.pages > 0
                        ? `${doc.pages}p`
                        : `${(doc.size_bytes / (1024 * 1024)).toFixed(2)} MB`}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Local Preview (No API) */}
        <div className="space-y-1.5">
          <button
            type="button"
            onClick={runPreview}
            disabled={selectedFiles.length === 0 || indexed || blocked || isPreviewing}
            className="w-full py-2 px-3 rounded-xl border border-[#E5EBE8] dark:border-[#26483F] bg-white dark:bg-[#172E29] hover:bg-[#F6F8F7] dark:hover:bg-[#1B3831] disabled:opacity-45 text-xs font-medium text-[#172B28] dark:text-[#F2F7F5] transition-colors"
          >
            {isPreviewing ? "Extracting pages…" : "Preview pages (no API)"}
          </button>
          <p className="text-[11px] text-[#6B7C77] dark:text-[#94A7A1] leading-snug">
            Preview extracts text locally. It does not index documents or generate AI answers.
          </p>
        </div>

        {/* Consent & Index documents */}
        <div className="pt-2 border-t border-[#E5EBE8] dark:border-[#22423B] space-y-2.5">
          <label className="flex items-start gap-2 cursor-pointer text-xs text-[#172B28] dark:text-[#E2EBE7]">
            <input
              type="checkbox"
              checked={consent}
              onChange={(e) => setConsent(e.target.checked)}
              className="mt-0.5 rounded text-[#147D65]"
            />
            <span className="leading-snug">
              I agree to send these documents and questions to {aiLabel}.
            </span>
          </label>

          {!aiReady && health && (
            <div className="p-2.5 rounded-xl bg-[#EAF4EF] dark:bg-[#1A3831] border border-[#C8E2D5] dark:border-[#274F44] text-[11px] text-[#172B28] dark:text-[#CFDFD9]">
              Configure the {aiLabel} API key and both model names on the server. PDF preview remains available.
            </div>
          )}

          <p className="text-[11px] text-[#6B7C77] dark:text-[#94A7A1] leading-snug">
            AI provider: {health?.ai?.label || "Unconfigured"}. Availability and charges depend on your provider plan and quota; a configured key does not confirm access.
          </p>

          <button
            type="button"
            onClick={runIndex}
            disabled={!consent || !hasSelection || indexed || blocked || !aiReady || isIndexing}
            className="w-full py-2.5 px-3 rounded-xl bg-[#147D65] hover:bg-[#0E634F] disabled:opacity-45 text-white font-semibold text-xs shadow-xs transition-colors"
          >
            {isIndexing ? "Extracting and indexing…" : "Index documents"}
          </button>
        </div>

        {/* Saved Workspaces Section */}
        <div className="pt-2 border-t border-[#E5EBE8] dark:border-[#22423B]">
          <button
            type="button"
            onClick={() => {
              const next = !showSavedPanel;
              setShowSavedPanel(next);
              if (next && workspaces.length === 0) {
                refreshWorkspaces();
              }
            }}
            className="w-full py-1.5 flex items-center justify-between text-xs font-semibold text-[#172B28] dark:text-[#F2F7F5]"
          >
            <span className="flex items-center gap-1.5">
              <FolderOpen className="w-3.5 h-3.5 text-[#147D65] dark:text-[#4ADE80]" />
              <span>Saved workspaces</span>
            </span>
            {showSavedPanel ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>

          {showSavedPanel && (
            <div className="mt-2.5 space-y-3 text-xs">
              <p className="text-[11px] text-[#6B7C77] dark:text-[#94A7A1] leading-snug">
                Save PDFs and chat privately to your account. Opening a saved workspace restores its chat; index its PDFs again to ask new questions.
              </p>

              {/* Save new workspace form */}
              <form onSubmit={handleSaveWorkspace} className="space-y-2">
                <input
                  type="text"
                  maxLength={120}
                  placeholder="Workspace name"
                  value={workspaceTitle}
                  onChange={(e) => setWorkspaceTitle(e.target.value)}
                  className="w-full p-2 rounded-lg border border-[#E5EBE8] dark:border-[#25463D] bg-transparent text-xs text-[#172B28] dark:text-[#F2F7F5] placeholder-[#8A9C96] focus:outline-hidden focus:ring-1 focus:ring-[#147D65]"
                />
                <button
                  type="submit"
                  disabled={!hasSelection || blocked || !workspaceTitle.trim() || isWorkspaceBusy}
                  className="w-full flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg border border-[#E5EBE8] dark:border-[#26483F] bg-white dark:bg-[#172E29] hover:bg-[#F6F8F7] dark:hover:bg-[#1B3831] disabled:opacity-45 font-medium text-[#172B28] dark:text-[#F2F7F5]"
                >
                  <Save className="w-3.5 h-3.5" />
                  <span>Save as new workspace</span>
                </button>
              </form>

              {/* Refresh list */}
              <button
                type="button"
                onClick={refreshWorkspaces}
                disabled={isWorkspaceBusy}
                className="w-full flex items-center justify-center gap-1.5 py-1.5 px-3 rounded-lg border border-[#E5EBE8] dark:border-[#26483F] text-[11px] font-medium text-[#5C7069] dark:text-[#9FB1AA] hover:bg-[#F6F8F7] dark:hover:bg-[#1A3831]"
              >
                <RefreshCw className={`w-3 h-3 ${isWorkspaceBusy ? "animate-spin" : ""}`} />
                <span>Refresh saved workspaces</span>
              </button>

              {selectedSaved && (
                <div className="space-y-2 pt-1 border-t border-[#E5EBE8] dark:border-[#22423B]">
                  <label className="block text-[11px] font-medium text-[#5C7069] dark:text-[#9FB1AA]">
                    Choose saved workspace
                  </label>
                  <select
                    value={effectiveWorkspaceId}
                    onChange={(e) => {
                      setChosenWorkspaceId(e.target.value);
                      setConfirmDelete(false);
                    }}
                    className="w-full p-2 rounded-lg border border-[#E5EBE8] dark:border-[#25463D] bg-white dark:bg-[#172E29] text-xs text-[#172B28] dark:text-[#F2F7F5]"
                  >
                    {workspaces.map((w) => (
                      <option key={w.id} value={w.id}>
                        {w.title} · {w.created_at.slice(0, 19)} · {w.status}
                      </option>
                    ))}
                  </select>

                  <p className="text-[11px] text-[#6B7C77] dark:text-[#94A7A1] leading-snug">
                    Reset the current session before opening a different workspace.
                  </p>
                  <button
                    type="button"
                    onClick={() => openSavedWorkspace(selectedSaved.id)}
                    disabled={!canOpenSaved}
                    className="w-full py-2 px-3 rounded-lg bg-[#EAF4EF] dark:bg-[#1A3831] text-[#147D65] dark:text-[#4ADE80] disabled:opacity-40 font-semibold text-xs hover:bg-[#D8EBE1]"
                  >
                    Open saved workspace
                  </button>

                  {/* Deletion confirmation */}
                  <div className="pt-2 space-y-1.5">
                    <label className="flex items-start gap-2 cursor-pointer text-[11px] text-[#6B7C77] dark:text-[#94A7A1]">
                      <input
                        type="checkbox"
                        checked={confirmDelete}
                        onChange={(e) => setConfirmDelete(e.target.checked)}
                        className="mt-0.5 rounded text-red-600"
                      />
                      <span>Permanently delete: {selectedSaved.title}</span>
                    </label>
                    <button
                      type="button"
                      onClick={() => {
                        setConfirmDelete(false);
                        deleteSavedWorkspace(selectedSaved.id);
                      }}
                      disabled={!confirmDelete || blocked || isWorkspaceBusy}
                      className="w-full flex items-center justify-center gap-1.5 py-1.5 px-3 rounded-lg border border-red-200 dark:border-red-900/50 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30 disabled:opacity-40 text-[11px] font-semibold"
                    >
                      <Trash2 className="w-3 h-3" />
                      <span>Delete saved workspace</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Footer Account & Sign Out */}
      <div className="p-4 border-t border-[#E5EBE8] dark:border-[#22423B] bg-[#FAFCFB] dark:bg-[#112420] space-y-2">
        <div className="text-[11px] text-[#6B7C77] dark:text-[#94A7A1] truncate">
          Signed in as <span className="font-semibold text-[#172B28] dark:text-[#F2F7F5]">{user?.email}</span>
        </div>
        <button
          type="button"
          onClick={handleLogout}
          disabled={isLoggingOut}
          className="w-full flex items-center justify-center gap-1.5 py-2 px-3 rounded-xl border border-[#E5EBE8] dark:border-[#26483F] bg-white dark:bg-[#172E29] hover:bg-[#F6F8F7] dark:hover:bg-[#1C3831] disabled:opacity-50 text-xs font-medium text-[#172B28] dark:text-[#F2F7F5] transition-colors"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span>{isLoggingOut ? "Logging out…" : "Log out"}</span>
        </button>
      </div>
    </aside>
  );

  return (
    <>
      <div className="hidden md:flex h-full">{content}</div>
      {mobileOpen && (
        <div className="fixed inset-0 z-40 flex md:hidden">
          <div className="fixed inset-0 bg-black/40" onClick={onCloseMobile} />
          <div className="relative z-50 h-full flex">{content}</div>
        </div>
      )}
    </>
  );
}
