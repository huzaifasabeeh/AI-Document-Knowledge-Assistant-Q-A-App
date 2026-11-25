"use client";

import React, { createContext, useCallback, useContext, useEffect, useState } from "react";
import {
  ChatMessage,
  PreviewPage,
  SavedWorkspaceSummary,
  SourcePassage,
  UploadedDocMeta,
} from "./types";
import {
  ApiError,
  askQuestion,
  clearSessionChat,
  deleteWorkspace,
  exportChatConversation,
  getSessionState,
  indexDocuments,
  listWorkspaces,
  loadWorkspace,
  previewDocuments,
  resetSession,
  saveWorkspaceChat,
  saveWorkspaceFromFiles,
  saveWorkspaceFromSession,
} from "./api";
import { useAuth } from "./auth-context";

const SESSION_ID_KEY = "docmind_active_session_id";
const CONSENT_KEY = "docmind_consent_identity";

async function computeSelectionSignature(files: File[]): Promise<string> {
  const parts: string[] = [];
  for (const f of files) {
    const buf = await f.arrayBuffer();
    const digest = await crypto.subtle.digest("SHA-256", buf);
    const hex = Array.from(new Uint8Array(digest))
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");
    parts.push(`${f.name}:${hex}`);
  }
  return parts.join("|");
}

function normalizeServerMessages(
  rows: {
    role: "user" | "assistant";
    content: string;
    status?: "answered" | "conflict" | "not_found";
    claims?: { text: string; refs: { filename: string; page: number }[] }[];
    sources?: SourcePassage[];
    latency?: string;
  }[]
): ChatMessage[] {
  return rows.map((m, idx) => ({
    id: `msg-restored-${idx}-${Date.now()}`,
    role: m.role,
    content: m.content,
    status: m.status,
    claims: m.claims,
    sources: m.sources,
    latency: m.latency,
  }));
}

interface DocContextType {
  selectedFiles: File[];
  documents: UploadedDocMeta[];
  totalPages: number;
  passageCount: number;
  previewPages: PreviewPage[];
  messages: ChatMessage[];
  consent: boolean;
  sessionId: string | null;
  indexed: boolean;
  providerChanged: boolean;
  cleanupBlocked: boolean;
  savedWorkspaceId: string | null;
  workspaces: SavedWorkspaceSummary[];
  chatSaveError: string | null;
  workspaceNotice: string | null;
  statusError: string | null;
  isPreviewing: boolean;
  isIndexing: boolean;
  isAsking: boolean;
  isResetting: boolean;
  isWorkspaceBusy: boolean;
  activeSources: SourcePassage[];
  activeSourceIndex: number;
  isEvidenceOpen: boolean;

  setConsent: (checked: boolean) => void;
  selectFiles: (files: File[]) => Promise<void>;
  runPreview: () => Promise<void>;
  runIndex: () => Promise<void>;
  sendQuestion: (question: string) => Promise<void>;
  clearChatOnly: () => Promise<void>;
  downloadChat: () => Promise<void>;
  resetWorkspace: () => Promise<void>;
  refreshWorkspaces: () => Promise<void>;
  saveNewWorkspace: (title: string) => Promise<void>;
  openSavedWorkspace: (workspaceId: string) => Promise<void>;
  retrySaveChat: () => Promise<void>;
  deleteSavedWorkspace: (workspaceId: string) => Promise<void>;
  openEvidence: (sources: SourcePassage[], index?: number) => void;
  closeEvidence: () => void;
  clearNotices: () => void;
}

const DocContext = createContext<DocContextType | undefined>(undefined);

export function DocProvider({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  return <DocProviderInner key={user?.id || "anon"}>{children}</DocProviderInner>;
}

function DocProviderInner({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, token, health, refreshHealth, invalidateSession } = useAuth();

  const currentIdentity = health?.ai?.identity ?? null;
  const currentIdentityKey = currentIdentity ? currentIdentity.join("|") : "";

  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [selectionSignature, setSelectionSignature] = useState<string>("");
  const [documents, setDocuments] = useState<UploadedDocMeta[]>([]);
  const [totalPages, setTotalPages] = useState<number>(0);
  const [passageCount, setPassageCount] = useState<number>(0);
  const [previewPages, setPreviewPages] = useState<PreviewPage[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [consent, setConsentState] = useState<boolean>(() => {
    if (typeof window === "undefined" || !currentIdentityKey) return false;
    return sessionStorage.getItem(CONSENT_KEY) === currentIdentityKey;
  });
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [indexed, setIndexed] = useState<boolean>(false);
  const [indexedProviderIdentity, setIndexedProviderIdentity] = useState<string[] | null>(null);
  const [cleanupBlocked, setCleanupBlocked] = useState<boolean>(false);
  const [savedWorkspaceId, setSavedWorkspaceId] = useState<string | null>(null);
  const [workspaces, setWorkspaces] = useState<SavedWorkspaceSummary[]>([]);

  const [chatSaveError, setChatSaveError] = useState<string | null>(null);
  const [workspaceNotice, setWorkspaceNotice] = useState<string | null>(null);
  const [statusError, setStatusError] = useState<string | null>(null);

  const [isPreviewing, setIsPreviewing] = useState<boolean>(false);
  const [isIndexing, setIsIndexing] = useState<boolean>(false);
  const [isAsking, setIsAsking] = useState<boolean>(false);
  const [isResetting, setIsResetting] = useState<boolean>(false);
  const [isWorkspaceBusy, setIsWorkspaceBusy] = useState<boolean>(false);

  const [activeSources, setActiveSources] = useState<SourcePassage[]>([]);
  const [activeSourceIndex, setActiveSourceIndex] = useState<number>(0);
  const [isEvidenceOpen, setIsEvidenceOpen] = useState<boolean>(false);

  const providerChanged = Boolean(
    indexed &&
      indexedProviderIdentity &&
      currentIdentity &&
      indexedProviderIdentity.join("|") !== currentIdentityKey
  );

  const clearLocalWorkspaceState = useCallback(() => {
    setSelectedFiles([]);
    setSelectionSignature("");
    setDocuments([]);
    setTotalPages(0);
    setPassageCount(0);
    setPreviewPages([]);
    setMessages([]);
    setConsentState(false);
    setSessionId(null);
    setIndexed(false);
    setIndexedProviderIdentity(null);
    setCleanupBlocked(false);
    setSavedWorkspaceId(null);
    setChatSaveError(null);
    setWorkspaceNotice(null);
    setStatusError(null);
    setActiveSources([]);
    setActiveSourceIndex(0);
    setIsEvidenceOpen(false);
    if (typeof window !== "undefined") {
      sessionStorage.removeItem(SESSION_ID_KEY);
      sessionStorage.removeItem(CONSENT_KEY);
    }
  }, []);

  // Restore same-tab server session if present on F5 refresh (zero synchronous setState before await)
  useEffect(() => {
    if (!isAuthenticated || !token) {
      return;
    }

    let cancelled = false;
    async function restoreFromSessionStorage() {
      const savedSid =
        typeof window !== "undefined" ? sessionStorage.getItem(SESSION_ID_KEY) : null;
      if (!savedSid || !token) return;
      try {
        const sess = await getSessionState(token, savedSid);
        if (cancelled) return;
        setSessionId(sess.session_id);
        setDocuments(sess.documents);
        setTotalPages(sess.total_pages);
        setPassageCount(sess.passage_count);
        setIndexed(sess.indexed);
        setCleanupBlocked(sess.cleanup_blocked);
        setIndexedProviderIdentity(sess.provider_identity);
        setSavedWorkspaceId(sess.saved_workspace_id);
        const restoredMsgs = normalizeServerMessages(sess.messages || []);
        setMessages(restoredMsgs);
        const lastWithSources = [...restoredMsgs].reverse().find((m) => m.sources && m.sources.length > 0);
        if (lastWithSources?.sources) {
          setActiveSources(lastWithSources.sources);
          setActiveSourceIndex(0);
        }
      } catch (err) {
        if (cancelled) return;
        if (err instanceof ApiError && err.status === 401) {
          invalidateSession(err.message);
          return;
        }
        if (typeof window !== "undefined") {
          sessionStorage.removeItem(SESSION_ID_KEY);
        }
      }
    }

    restoreFromSessionStorage();
    return () => {
      cancelled = true;
    };
  }, [invalidateSession, isAuthenticated, token]);

  const handleApiError = useCallback(
    (err: unknown, fallback: string) => {
      if (err instanceof ApiError && err.status === 401) {
        invalidateSession(err.message);
        return;
      }
      const message = err instanceof Error ? err.message : fallback;
      if (message.toLowerCase().includes("cleanup failed") || message.toLowerCase().includes("session paused")) {
        setCleanupBlocked(true);
      }
      setStatusError(message);
    },
    [invalidateSession]
  );

  const setConsent = (checked: boolean) => {
    setConsentState(checked);
    if (typeof window !== "undefined") {
      if (checked && currentIdentityKey) {
        sessionStorage.setItem(CONSENT_KEY, currentIdentityKey);
      } else {
        sessionStorage.removeItem(CONSENT_KEY);
      }
    }
  };

  const selectFiles = async (files: File[]) => {
    setStatusError(null);
    if (indexed || cleanupBlocked || providerChanged || savedWorkspaceId) {
      setStatusError("Reset before changing this workspace's document set.");
      return;
    }

    if (files.length === 0) {
      setSelectedFiles([]);
      setSelectionSignature("");
      setPreviewPages([]);
      setDocuments([]);
      setTotalPages(0);
      return;
    }

    // Immediate client-side feedback mirroring core.py limits
    if (files.length > 10) {
      setStatusError("Select between 1 and 10 PDFs.");
      return;
    }
    const seenNames = new Set<string>();
    for (const file of files) {
      const cleanName = file.name.replace(/\\/g, "/").split("/").pop() || file.name;
      if (seenNames.has(cleanName)) {
        setStatusError("Use distinct filenames for each PDF.");
        return;
      }
      seenNames.add(cleanName);
      if (!cleanName.toLowerCase().endsWith(".pdf")) {
        setStatusError("Only PDF files are supported.");
        return;
      }
      if (file.size === 0 || file.size > 10 * 1024 * 1024) {
        setStatusError("Each PDF must be nonempty and at most 10 MB.");
        return;
      }
    }

    const nextSig = await computeSelectionSignature(files);
    if (nextSig !== selectionSignature) {
      setPreviewPages([]);
      setSelectionSignature(nextSig);
      setDocuments(
        files.map((f) => ({
          name: f.name.replace(/\\/g, "/").split("/").pop() || f.name,
          size_bytes: f.size,
          pages: 0,
        }))
      );
      setTotalPages(0);
    }
    setSelectedFiles(files);
  };

  const runPreview = async () => {
    if (!token || selectedFiles.length === 0 || indexed || cleanupBlocked || providerChanged) {
      return;
    }
    setIsPreviewing(true);
    setStatusError(null);
    setPreviewPages([]);
    try {
      const res = await previewDocuments(token, selectedFiles);
      setPreviewPages(res.pages);
      setDocuments(res.documents);
      setTotalPages(res.total_pages);
    } catch (err) {
      handleApiError(err, "Could not preview PDF pages.");
    } finally {
      setIsPreviewing(false);
    }
  };

  const runIndex = async () => {
    if (!token || !consent || indexed || cleanupBlocked || providerChanged) return;
    if (selectedFiles.length === 0 && !sessionId) return;

    setIsIndexing(true);
    setStatusError(null);
    try {
      const res = await indexDocuments(token, {
        consent,
        files: sessionId ? undefined : selectedFiles,
        sessionId: sessionId || undefined,
      });
      setSessionId(res.session_id);
      if (typeof window !== "undefined") {
        sessionStorage.setItem(SESSION_ID_KEY, res.session_id);
      }
      setDocuments(res.documents);
      setTotalPages(res.total_pages);
      setPassageCount(res.passage_count);
      setIndexed(true);
      setIndexedProviderIdentity(res.provider_identity);
      setPreviewPages([]);
      if (res.saved_workspace_id) {
        setSavedWorkspaceId(res.saved_workspace_id);
      }
      await refreshHealth();
    } catch (err) {
      handleApiError(err, "Document indexing failed.");
    } finally {
      setIsIndexing(false);
    }
  };

  const persistMessagesIfSaved = useCallback(
    async (targetMessages: ChatMessage[]) => {
      if (!token || !savedWorkspaceId) return;
      try {
        await saveWorkspaceChat(token, savedWorkspaceId, targetMessages);
        setChatSaveError(null);
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) {
          invalidateSession(err.message);
          return;
        }
        const msg = err instanceof Error ? err.message : "Could not save chat to saved workspace.";
        setChatSaveError(msg);
      }
    },
    [invalidateSession, savedWorkspaceId, token]
  );

  const sendQuestion = async (question: string) => {
    const trimmed = question.trim();
    if (!token || !sessionId || !indexed || !consent || cleanupBlocked || providerChanged || !trimmed) {
      return;
    }

    setIsAsking(true);
    setStatusError(null);
    const historyPayload = messages.map((m) => ({ role: m.role, content: m.content }));

    try {
      const res = await askQuestion(token, {
        session_id: sessionId,
        question: trimmed,
        history: historyPayload,
        consent,
      });

      const userMsg: ChatMessage = {
        id: `msg-u-${Date.now()}`,
        role: "user",
        content: trimmed,
      };
      const assistantMsg: ChatMessage = {
        id: `msg-a-${Date.now() + 1}`,
        role: "assistant",
        content: res.content,
        status: res.status,
        claims: res.claims,
        sources: res.sources,
        latency: res.latency,
      };

      const nextMessages = [...messages, userMsg, assistantMsg];
      setMessages(nextMessages);
      if (res.sources && res.sources.length > 0) {
        setActiveSources(res.sources);
        setActiveSourceIndex(0);
        setIsEvidenceOpen(true);
      }
      await persistMessagesIfSaved(nextMessages);
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        await refreshHealth();
      } else if (err instanceof ApiError && err.status === 404) {
        setIndexed(false);
        setSessionId(null);
        if (typeof window !== "undefined") {
          sessionStorage.removeItem(SESSION_ID_KEY);
        }
      }
      handleApiError(err, "Question could not be answered.");
    } finally {
      setIsAsking(false);
    }
  };

  const clearChatOnly = async () => {
    if (!token || cleanupBlocked || providerChanged) return;
    setStatusError(null);
    if (sessionId) {
      try {
        await clearSessionChat(token, sessionId);
      } catch (err) {
        handleApiError(err, "Could not clear session chat.");
        return;
      }
    }
    setMessages([]);
    setActiveSources([]);
    setIsEvidenceOpen(false);
    await persistMessagesIfSaved([]);
  };

  const downloadChat = async () => {
    if (!token || messages.length === 0) return;
    setStatusError(null);
    try {
      const res = await exportChatConversation(token, messages);
      const blob = new Blob([res.content], { type: "text/plain;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = res.filename || "document-chat.txt";
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      handleApiError(err, "Could not export chat.");
    }
  };

  const resetWorkspace = async () => {
    if (!token) {
      clearLocalWorkspaceState();
      return;
    }
    setIsResetting(true);
    setStatusError(null);
    try {
      if (sessionId) {
        await resetSession(token, sessionId);
      }
      clearLocalWorkspaceState();
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        clearLocalWorkspaceState();
      } else {
        handleApiError(err, "Cleanup failed. Retry reset or restart the server before continuing.");
      }
    } finally {
      setIsResetting(false);
    }
  };

  const refreshWorkspaces = useCallback(async () => {
    if (!token) return;
    setIsWorkspaceBusy(true);
    setStatusError(null);
    try {
      const res = await listWorkspaces(token);
      setWorkspaces(res.workspaces);
    } catch (err) {
      handleApiError(err, "Could not load saved workspaces.");
    } finally {
      setIsWorkspaceBusy(false);
    }
  }, [handleApiError, token]);

  const saveNewWorkspace = async (title: string) => {
    if (!token || cleanupBlocked || providerChanged) return;
    if (!sessionId && selectedFiles.length === 0) {
      setStatusError("Select PDF files before saving a workspace.");
      return;
    }
    setIsWorkspaceBusy(true);
    setStatusError(null);
    setWorkspaceNotice(null);
    try {
      if (sessionId) {
        const res = await saveWorkspaceFromSession(token, sessionId, title, messages);
        setSavedWorkspaceId(res.workspace_id);
      } else {
        const res = await saveWorkspaceFromFiles(token, title, selectedFiles, messages);
        setSessionId(res.session_id);
        if (typeof window !== "undefined") {
          sessionStorage.setItem(SESSION_ID_KEY, res.session_id);
        }
        setSavedWorkspaceId(res.workspace_id);
        setDocuments(res.documents);
        setTotalPages(res.total_pages);
        // Bind uploader to the saved workspace's exact document set
        setSelectedFiles([]);
      }
      setChatSaveError(null);
      setWorkspaceNotice("Workspace saved to your account.");
      await refreshWorkspaces();
    } catch (err) {
      handleApiError(err, "Failed to save workspace.");
    } finally {
      setIsWorkspaceBusy(false);
    }
  };

  const openSavedWorkspace = async (workspaceId: string) => {
    if (!token || indexed || cleanupBlocked || providerChanged || selectedFiles.length > 0 || messages.length > 0 || savedWorkspaceId) {
      return;
    }
    setIsWorkspaceBusy(true);
    setStatusError(null);
    setWorkspaceNotice(null);
    try {
      const res = await loadWorkspace(token, workspaceId);
      setSessionId(res.session_id);
      if (typeof window !== "undefined") {
        sessionStorage.setItem(SESSION_ID_KEY, res.session_id);
      }
      setSavedWorkspaceId(res.workspace_id);
      setDocuments(res.documents);
      setTotalPages(res.total_pages);
      setIndexed(false);
      setPassageCount(0);
      setPreviewPages([]);
      const restoredMsgs = normalizeServerMessages(res.messages);
      setMessages(restoredMsgs);
      const lastWithSources = [...restoredMsgs].reverse().find((m) => m.sources && m.sources.length > 0);
      if (lastWithSources?.sources) {
        setActiveSources(lastWithSources.sources);
        setActiveSourceIndex(0);
      }
      setWorkspaceNotice("Saved workspace opened. Re-index its PDFs with consent to ask new questions.");
    } catch (err) {
      handleApiError(err, "Could not open saved workspace.");
    } finally {
      setIsWorkspaceBusy(false);
    }
  };

  const retrySaveChat = async () => {
    if (!savedWorkspaceId) return;
    setIsWorkspaceBusy(true);
    await persistMessagesIfSaved(messages);
    setIsWorkspaceBusy(false);
  };

  const deleteSavedWorkspace = async (workspaceId: string) => {
    if (!token || cleanupBlocked || providerChanged) return;
    setIsWorkspaceBusy(true);
    setStatusError(null);
    try {
      await deleteWorkspace(token, workspaceId);
      if (savedWorkspaceId === workspaceId) {
        setSavedWorkspaceId(null);
        setChatSaveError(null);
      }
      setWorkspaceNotice("Saved copy deleted. Any open session or downloaded copy remains until cleared.");
      await refreshWorkspaces();
    } catch (err) {
      handleApiError(
        err,
        "Deletion could not be confirmed. Refresh the list and retry; a deleting item cannot be reopened."
      );
    } finally {
      setIsWorkspaceBusy(false);
    }
  };

  const openEvidence = (sources: SourcePassage[], index = 0) => {
    setActiveSources(sources);
    setActiveSourceIndex(index);
    setIsEvidenceOpen(true);
  };

  const closeEvidence = () => {
    setIsEvidenceOpen(false);
  };

  const clearNotices = () => {
    setStatusError(null);
    setWorkspaceNotice(null);
  };

  return (
    <DocContext.Provider
      value={{
        selectedFiles,
        documents,
        totalPages,
        passageCount,
        previewPages,
        messages,
        consent,
        sessionId,
        indexed,
        providerChanged,
        cleanupBlocked,
        savedWorkspaceId,
        workspaces,
        chatSaveError,
        workspaceNotice,
        statusError,
        isPreviewing,
        isIndexing,
        isAsking,
        isResetting,
        isWorkspaceBusy,
        activeSources,
        activeSourceIndex,
        isEvidenceOpen,
        setConsent,
        selectFiles,
        runPreview,
        runIndex,
        sendQuestion,
        clearChatOnly,
        downloadChat,
        resetWorkspace,
        refreshWorkspaces,
        saveNewWorkspace,
        openSavedWorkspace,
        retrySaveChat,
        deleteSavedWorkspace,
        openEvidence,
        closeEvidence,
        clearNotices,
      }}
    >
      {children}
    </DocContext.Provider>
  );
}

export function useDocs() {
  const ctx = useContext(DocContext);
  if (!ctx) {
    throw new Error("useDocs must be used within DocProvider");
  }
  return ctx;
}
