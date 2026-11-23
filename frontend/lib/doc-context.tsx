"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import {
  DocumentItem,
  CollectionItem,
  ChatMessage,
  SourceEvidenceState,
  InlineCitation,
} from "./types";
import {
  initialDocuments,
  initialCollections,
  sampleInitialChat,
  defaultEvidence,
} from "./mock-data";
import { askChat, uploadDocuments } from "./api";

interface DocContextType {
  documents: DocumentItem[];
  collections: CollectionItem[];
  messages: ChatMessage[];
  selectedDocNames: string[];
  activeEvidence: SourceEvidenceState;
  isEvidenceOpen: boolean;
  isUploading: boolean;
  sessionId: string;
  uploadQueue: { name: string; size: string; pages: number; progress: number; status: string }[];
  toggleSelectDoc: (name: string) => void;
  clearSelectedDocs: () => void;
  openEvidence: (evidence: Partial<SourceEvidenceState>) => void;
  closeEvidence: () => void;
  sendMessage: (text: string) => Promise<void>;
  startNewChat: () => void;
  addUploadedFile: (file: { name: string; size: string; pages: number; collection?: string }) => void;
  uploadRealFiles: (files: File[], collectionName?: string) => Promise<void>;
  createCollection: (name: string, description: string) => void;
}

const DocContext = createContext<DocContextType | undefined>(undefined);

export function DocProvider({ children }: { children: React.ReactNode }) {
  const [documents, setDocuments] = useState<DocumentItem[]>(initialDocuments);
  const [collections, setCollections] = useState<CollectionItem[]>(initialCollections);
  const [messages, setMessages] = useState<ChatMessage[]>(sampleInitialChat);
  const [selectedDocNames, setSelectedDocNames] = useState<string[]>([
    "Q3 Financial Report.pdf",
    "Market Research.docx",
  ]);
  const [sessionId, setSessionId] = useState<string>("");
  const [activeEvidence, setActiveEvidence] = useState<SourceEvidenceState>(defaultEvidence);
  const [isEvidenceOpen, setIsEvidenceOpen] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadQueue, setUploadQueue] = useState([
    { name: "Q3 Financial Report.pdf", size: "2.4 MB", pages: 24, progress: 100, status: "Ready to ask" },
    { name: "Market Research.docx", size: "1.8 MB", pages: 18, progress: 100, status: "Ready to ask" },
    { name: "Onboarding Handbook.pdf", size: "8.6 MB", pages: 64, progress: 68, status: "Indexing - 68%" },
  ]);

  useEffect(() => {
    const saved = localStorage.getItem("docmind_session_id");
    if (saved) {
      setSessionId(saved);
    }
  }, []);

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
      ...prev,
      ...evidence,
      isOpen: true,
    }));
    setIsEvidenceOpen(true);
  };

  const closeEvidence = () => {
    setIsEvidenceOpen(false);
  };

  const startNewChat = () => {
    setMessages([]);
  };

  const addUploadedFile = (file: { name: string; size: string; pages: number; collection?: string }) => {
    const newDoc: DocumentItem = {
      id: `doc-${Date.now()}`,
      name: file.name,
      type: file.name.endsWith(".pdf") ? "pdf" : file.name.endsWith(".docx") ? "docx" : "txt",
      pages: file.pages || 1,
      size: file.size,
      collection: file.collection || "Operations",
      status: "ready",
      addedAt: "Just now",
    };
    setDocuments((prev) => [newDoc, ...prev]);
    setSelectedDocNames((prev) => [...prev, file.name]);
  };

  const uploadRealFiles = async (files: File[], collectionName: string = "Operations") => {
    setIsUploading(true);
    try {
      const res = await uploadDocuments(files);
      if (res.session_id) {
        setSessionId(res.session_id);
        localStorage.setItem("docmind_session_id", res.session_id);
      }
      files.forEach((f) => {
        const sizeMb = (f.size / (1024 * 1024)).toFixed(1);
        addUploadedFile({
          name: f.name,
          size: `${sizeMb} MB`,
          pages: 12,
          collection: collectionName,
        });
      });
    } catch (err) {
      console.error("Real upload failed, using client simulation:", err);
      files.forEach((f) => {
        const sizeMb = (f.size / (1024 * 1024)).toFixed(1);
        addUploadedFile({
          name: f.name,
          size: `${sizeMb} MB`,
          pages: 12,
          collection: collectionName,
        });
      });
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
    setCollections((prev) => [...prev, newCol]);
  };

  const sendMessage = async (text: string) => {
    const userMsg: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: "user",
      content: text,
      selectedDocs: [...selectedDocNames],
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);

    const history = messages.map((m) => ({ role: m.role, content: m.content }));
    const apiRes = await askChat(text, sessionId, history);

    const assistantMsg: ChatMessage = {
      id: `msg-${Date.now() + 1}`,
      role: "assistant",
      content: apiRes.answer,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      groundingSources: apiRes.groundingSources || apiRes.citations?.length || 1,
      latency: apiRes.latency || "1.1s",
      points: apiRes.points && apiRes.points.length > 0 ? apiRes.points : [
        {
          num: "01",
          title: "Key observation",
          body: apiRes.answer,
          citationId: 1,
        },
      ],
      citations: (apiRes.citations as InlineCitation[]) || [],
    };

    setMessages((prev) => [...prev, assistantMsg]);

    // Update right-hand Source Evidence panel if evidence provided
    if (apiRes.evidence) {
      openEvidence(apiRes.evidence);
    } else if (apiRes.citations && apiRes.citations[0]) {
      const firstCite = apiRes.citations[0];
      openEvidence({
        docTitle: firstCite.docName.replace(/\.[^/.]+$/, ""),
        heading: "Relevant passage",
        fullText: firstCite.fullSnippet || firstCite.highlightText,
        highlightSnippet: firstCite.highlightText,
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
        toggleSelectDoc,
        clearSelectedDocs,
        openEvidence,
        closeEvidence,
        sendMessage,
        startNewChat,
        addUploadedFile,
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
