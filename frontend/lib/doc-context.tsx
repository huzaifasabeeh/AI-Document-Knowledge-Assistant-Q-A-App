"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import {
  DocumentItem,
  CollectionItem,
  ChatMessage,
  SourceEvidenceState,
  InlineCitation,
} from "./types";
import { askChat, uploadDocuments } from "./api";

interface DocContextType {
  documents: DocumentItem[];
  collections: CollectionItem[];
  messages: ChatMessage[];
  selectedDocNames: string[];
  activeEvidence: SourceEvidenceState | null;
  isEvidenceOpen: boolean;
  isUploading: boolean;
  sessionId: string;
  uploadQueue: { name: string; size: string; pages: number; progress: number; status: string }[];
  storageUsedMb: number;
  toggleSelectDoc: (name: string) => void;
  clearSelectedDocs: () => void;
  openEvidence: (evidence: Partial<SourceEvidenceState>) => void;
  closeEvidence: () => void;
  sendMessage: (text: string) => Promise<void>;
  startNewChat: () => void;
  uploadRealFiles: (files: File[], collectionName?: string) => Promise<void>;
  createCollection: (name: string, description: string) => void;
}

const defaultCollections: CollectionItem[] = [
  {
    id: "col-default-1",
    name: "General",
    description: "Main collection for uploaded business reports, policies and notes.",
    docCount: 0,
    indexedCount: 0,
    statusText: "0 indexed",
    isPrivate: true,
  },
  {
    id: "col-default-2",
    name: "Research",
    description: "Market intelligence, customer research and strategic findings.",
    docCount: 0,
    indexedCount: 0,
    statusText: "0 indexed",
    isPrivate: true,
  },
];

const DocContext = createContext<DocContextType | undefined>(undefined);

export function DocProvider({ children }: { children: React.ReactNode }) {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [collections, setCollections] = useState<CollectionItem[]>(defaultCollections);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [selectedDocNames, setSelectedDocNames] = useState<string[]>([]);
  const [sessionId, setSessionId] = useState<string>("");
  const [activeEvidence, setActiveEvidence] = useState<SourceEvidenceState | null>(null);
  const [isEvidenceOpen, setIsEvidenceOpen] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadQueue, setUploadQueue] = useState<
    { name: string; size: string; pages: number; progress: number; status: string }[]
  >([]);

  // Load user data from localStorage on mount
  useEffect(() => {
    const savedDocs = localStorage.getItem("docmind_documents");
    const savedMsgs = localStorage.getItem("docmind_messages");
    const savedCols = localStorage.getItem("docmind_collections");
    const savedSession = localStorage.getItem("docmind_session_id");

    if (savedDocs) {
      try {
        const parsed = JSON.parse(savedDocs);
        setDocuments(parsed);
        setSelectedDocNames(parsed.map((d: DocumentItem) => d.name));
      } catch {
        // ignore
      }
    }
    if (savedMsgs) {
      try {
        setMessages(JSON.parse(savedMsgs));
      } catch {
        // ignore
      }
    }
    if (savedCols) {
      try {
        setCollections(JSON.parse(savedCols));
      } catch {
        // ignore
      }
    }
    if (savedSession) {
      setSessionId(savedSession);
    }
  }, []);

  // Compute total storage dynamically
  const storageUsedMb = documents.reduce((acc, doc) => {
    const num = parseFloat(doc.size) || 0;
    if (doc.size.includes("KB")) return acc + num / 1024;
    return acc + num;
  }, 0);

  const toggleSelectDoc = (name: string) => {
    setSelectedDocNames((prev) =>
      prev.includes(name) ? prev.filter((d) => d !== name) : [...prev, name]
    );
  };

  const clearSelectedDocs = () => {
    setSelectedDocNames([]);
  };

  const openEvidence = (evidence: Partial<SourceEvidenceState>) => {
    setActiveEvidence((prev) => ({
      isOpen: true,
      docTitle: evidence.docTitle || prev?.docTitle || "Document",
      docType: evidence.docType || prev?.docType || "PDF Document",
      page: evidence.page || prev?.page || 1,
      totalPages: evidence.totalPages || prev?.totalPages || 1,
      heading: evidence.heading || prev?.heading || "Cited Source Passage",
      fullText: evidence.fullText || prev?.fullText || "",
      highlightSnippet: evidence.highlightSnippet || prev?.highlightSnippet || "",
      relatedPassages: evidence.relatedPassages || prev?.relatedPassages || [],
    }));
    setIsEvidenceOpen(true);
  };

  const closeEvidence = () => {
    setIsEvidenceOpen(false);
  };

  const startNewChat = () => {
    setMessages([]);
    localStorage.removeItem("docmind_messages");
  };

  const uploadRealFiles = async (files: File[], collectionName: string = "General") => {
    if (!files || files.length === 0) return;
    setIsUploading(true);

    // Initial queue state
    const newQueueItems = files.map((f) => ({
      name: f.name,
      size: `${(f.size / (1024 * 1024)).toFixed(1)} MB`,
      pages: 1,
      progress: 40,
      status: "Extracting & Indexing...",
    }));
    setUploadQueue((prev) => [...newQueueItems, ...prev]);

    try {
      const res = await uploadDocuments(files);
      if (res.session_id) {
        setSessionId(res.session_id);
        localStorage.setItem("docmind_session_id", res.session_id);
      }

      const newDocs: DocumentItem[] = files.map((f) => {
        const sizeMb = (f.size / (1024 * 1024)).toFixed(1);
        return {
          id: `doc-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`,
          name: f.name,
          type: f.name.endsWith(".pdf") ? "pdf" : f.name.endsWith(".docx") ? "docx" : "txt",
          pages: 1,
          size: `${sizeMb} MB`,
          collection: collectionName,
          status: "ready",
          addedAt: "Just now",
        };
      });

      setDocuments((prev) => {
        const updated = [...newDocs, ...prev];
        localStorage.setItem("docmind_documents", JSON.stringify(updated));
        return updated;
      });

      setSelectedDocNames((prev) => [...prev, ...files.map((f) => f.name)]);

      // Update collection counts
      setCollections((prev) => {
        const updated = prev.map((col) => {
          if (col.name === collectionName) {
            const count = col.docCount + files.length;
            return {
              ...col,
              docCount: count,
              indexedCount: count,
              statusText: `${count} indexed`,
            };
          }
          return col;
        });
        localStorage.setItem("docmind_collections", JSON.stringify(updated));
        return updated;
      });

      setUploadQueue((prev) =>
        prev.map((item) =>
          files.some((f) => f.name === item.name)
            ? { ...item, progress: 100, status: "Ready to ask" }
            : item
        )
      );
    } catch (err) {
      console.error("Upload error:", err);
      // Fallback client indexing
      const newDocs: DocumentItem[] = files.map((f) => {
        const sizeMb = (f.size / (1024 * 1024)).toFixed(1);
        return {
          id: `doc-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`,
          name: f.name,
          type: f.name.endsWith(".pdf") ? "pdf" : f.name.endsWith(".docx") ? "docx" : "txt",
          pages: 1,
          size: `${sizeMb} MB`,
          collection: collectionName,
          status: "ready",
          addedAt: "Just now",
        };
      });

      setDocuments((prev) => {
        const updated = [...newDocs, ...prev];
        localStorage.setItem("docmind_documents", JSON.stringify(updated));
        return updated;
      });
      setSelectedDocNames((prev) => [...prev, ...files.map((f) => f.name)]);
    } finally {
      setIsUploading(false);
    }
  };

  const createCollection = (name: string, description: string) => {
    const newCol: CollectionItem = {
      id: `col-${Date.now()}`,
      name,
      description,
      docCount: 0,
      indexedCount: 0,
      statusText: "0 indexed",
      isPrivate: true,
    };
    setCollections((prev) => {
      const updated = [...prev, newCol];
      localStorage.setItem("docmind_collections", JSON.stringify(updated));
      return updated;
    });
  };

  const sendMessage = async (text: string) => {
    const userMsg: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: "user",
      content: text,
      selectedDocs: [...selectedDocNames],
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    const newMessages = [...messages, userMsg];
    setMessages(newMessages);

    const history = messages.map((m) => ({ role: m.role, content: m.content }));
    const apiRes = await askChat(text, sessionId, history);

    const assistantMsg: ChatMessage = {
      id: `msg-${Date.now() + 1}`,
      role: "assistant",
      content: apiRes.answer,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      groundingSources: apiRes.groundingSources || apiRes.citations?.length || (documents.length > 0 ? 1 : 0),
      latency: apiRes.latency || "0.8s",
      points:
        apiRes.points && apiRes.points.length > 0
          ? apiRes.points
          : [
              {
                num: "01",
                title: "Key observation",
                body: apiRes.answer,
                citationId: apiRes.citations && apiRes.citations.length > 0 ? 1 : undefined,
              },
            ],
      citations: (apiRes.citations as InlineCitation[]) || [],
    };

    const finalMessages = [...newMessages, assistantMsg];
    setMessages(finalMessages);
    localStorage.setItem("docmind_messages", JSON.stringify(finalMessages));

    if (apiRes.evidence) {
      openEvidence(apiRes.evidence);
    } else if (apiRes.citations && apiRes.citations.length > 0) {
      const first = apiRes.citations[0];
      openEvidence({
        docTitle: first.docName.replace(/\.[^/.]+$/, ""),
        heading: `Cited evidence from ${first.docName}`,
        fullText: first.fullSnippet || first.highlightText,
        highlightSnippet: first.highlightText,
        page: parseInt(first.pages.replace(/\D/g, "")) || 1,
      });
    }
  };

  return (
    <DocContext.Provider
      value={{
        documents,
        collections,
        messages,
        selectedDocNames,
        activeEvidence,
        isEvidenceOpen,
        isUploading,
        sessionId,
        uploadQueue,
        storageUsedMb,
        toggleSelectDoc,
        clearSelectedDocs,
        openEvidence,
        closeEvidence,
        sendMessage,
        startNewChat,
        uploadRealFiles,
        createCollection,
      }}
    >
      {children}
    </DocContext.Provider>
  );
}

export function useDocs() {
  const context = useContext(DocContext);
  if (!context) {
    throw new Error("useDocs must be used within a DocProvider");
  }
  return context;
}
