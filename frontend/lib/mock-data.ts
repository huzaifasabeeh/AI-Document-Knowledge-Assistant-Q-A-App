import { DocumentItem, CollectionItem, ChatMessage, SourceEvidenceState } from "./types";

export const initialDocuments: DocumentItem[] = [
  {
    id: "doc-1",
    name: "Q3 Financial Report.pdf",
    type: "pdf",
    pages: 24,
    size: "2.4 MB",
    collection: "Finance",
    status: "ready",
    addedAt: "Nov 21",
  },
  {
    id: "doc-2",
    name: "Market Research.docx",
    type: "docx",
    pages: 18,
    size: "1.8 MB",
    collection: "Research",
    status: "ready",
    addedAt: "Nov 20",
  },
  {
    id: "doc-3",
    name: "Onboarding Handbook.pdf",
    type: "pdf",
    pages: 64,
    size: "8.6 MB",
    collection: "Operations",
    status: "indexing",
    indexingProgress: 68,
    addedAt: "Today",
  },
  {
    id: "doc-4",
    name: "Vendor Comparison.pdf",
    type: "pdf",
    pages: 12,
    size: "1.2 MB",
    collection: "Research",
    status: "ready",
    addedAt: "Nov 18",
  },
  {
    id: "doc-5",
    name: "Product Roadmap.txt",
    type: "txt",
    pages: 8,
    size: "42 KB",
    collection: "Operations",
    status: "ready",
    addedAt: "Nov 17",
  },
  {
    id: "doc-6",
    name: "Scanned Contract.pdf",
    type: "pdf",
    pages: 6,
    size: "3.1 MB",
    collection: "Operations",
    status: "attention",
    addedAt: "Today",
  },
];

export const initialCollections: CollectionItem[] = [
  {
    id: "col-1",
    name: "Finance",
    description: "Quarterly reports, forecasts and the numbers behind the decisions.",
    docCount: 6,
    indexedCount: 6,
    statusText: "6 indexed",
    isPrivate: true,
  },
  {
    id: "col-2",
    name: "Research",
    description: "Market intelligence, customer insights and competitive perspectives.",
    docCount: 4,
    indexedCount: 4,
    statusText: "4 indexed",
    isPrivate: true,
  },
  {
    id: "col-3",
    name: "Operations",
    description: "The policies and playbooks that keep your team moving.",
    docCount: 4,
    indexedCount: 2,
    statusText: "2 indexed • 1 indexing • 1 failed",
    isPrivate: true,
  },
];

export const defaultEvidence: SourceEvidenceState = {
  isOpen: true,
  docTitle: "Q3 Financial Report",
  docType: "PDF • 24 pages",
  page: 8,
  totalPages: 24,
  heading: "3. Revenue performance",
  fullText: `Quarterly revenue reached $12.8M, representing 24% year-over-year growth.

Enterprise revenue increased 32%, adding $2.4M in net new revenue. Existing account expansion drove the majority of this increase.

Net revenue retention improved to 118%, reflecting stronger customer value and broader product adoption.`,
  highlightSnippet: "Enterprise revenue increased 32%, adding $2.4M in net new revenue. Existing account expansion drove the majority of this increase.",
  relatedPassages: [
    {
      num: 1,
      title: "Retention & expansion",
      docAndPage: "Q3 Financial Report • p. 12",
    },
    {
      num: 2,
      title: "Market outlook",
      docAndPage: "Market Research • p. 6",
    },
  ],
};

export const sampleInitialChat: ChatMessage[] = [
  {
    id: "msg-1",
    role: "user",
    content: "What drove revenue growth in Q3, and how does it compare with the market outlook?",
    selectedDocs: ["Q3 Financial Report.pdf", "Market Research.docx"],
    timestamp: "10:42 AM",
  },
  {
    id: "msg-2",
    role: "assistant",
    content: "Revenue grew 24% year over year in Q3, led by enterprise expansion and stronger customer retention.",
    timestamp: "10:42 AM",
    groundingSources: 3,
    latency: "1.2s",
    points: [
      {
        num: "01",
        title: "Enterprise momentum",
        body: "Enterprise revenue rose 32%, contributing $2.4M in net new revenue. Expansion within existing accounts was the main driver.",
        citationId: 1,
      },
      {
        num: "02",
        title: "Better retention, more predictable growth",
        body: "Net revenue retention reached 118%, up from 109% last year, while churn fell to 2.1%.",
        citationId: 1,
      },
      {
        num: "03",
        title: "Ahead of a growing market",
        body: "Your 24% growth outpaced the market's projected 14%. Demand for AI-enabled workflows supports a positive Q4 outlook.",
        citationId: 2,
      },
    ],
    citations: [
      {
        id: 1,
        label: "1 Q3 Financial Report • pp. 8-12",
        docName: "Q3 Financial Report.pdf",
        pages: "pp. 8-12",
        highlightText: "Enterprise revenue increased 32%, adding $2.4M in net new revenue. Existing account expansion drove the majority of this increase.",
      },
      {
        id: 2,
        label: "2 Market Research • p. 6",
        docName: "Market Research.docx",
        pages: "p. 6",
        highlightText: "Market growth projected at 14% across AI and document intelligence sectors.",
      },
    ],
  },
];
