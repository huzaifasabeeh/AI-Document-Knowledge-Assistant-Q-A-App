export type DocumentStatus = "ready" | "indexing" | "attention" | "failed";

export interface DocumentItem {
  id: string;
  name: string;
  type: "pdf" | "docx" | "txt";
  pages: number;
  size: string;
  collection: string;
  status: DocumentStatus;
  indexingProgress?: number;
  addedAt: string;
}

export interface CollectionItem {
  id: string;
  name: string;
  description: string;
  docCount: number;
  indexedCount: number;
  statusText?: string;
  isPrivate: boolean;
}

export interface InlineCitation {
  id: number;
  label: string; // e.g. "1 Q3 Financial Report - pp. 8-12"
  docName: string;
  pages: string;
  highlightText: string;
  fullSnippet?: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  selectedDocs?: string[];
  points?: {
    num: string;
    title: string;
    body: string;
    citationId?: number;
  }[];
  citations?: InlineCitation[];
  groundingSources?: number;
  latency?: string;
}

export interface SourceEvidenceState {
  isOpen: boolean;
  docTitle: string;
  docType: string;
  page: number;
  totalPages: number;
  heading: string;
  fullText: string;
  highlightSnippet: string;
  relatedPassages: {
    num: number;
    title: string;
    docAndPage: string;
  }[];
}

export interface UserProfile {
  name: string;
  email: string;
  avatarUrl: string;
  workspaceName: string;
  storageUsedMb: number;
  storageLimitMb: number;
}
