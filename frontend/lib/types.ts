export interface AuthUser {
  id: string;
  email: string;
}

export interface AiHealthInfo {
  provider: "openai" | "gemini" | null;
  label: string | null;
  identity: string[] | null;
  ready: boolean;
  error: string | null;
}

export interface HealthStatus {
  status: string;
  auth_configured: boolean;
  auth_error: string | null;
  ai: AiHealthInfo;
  limits: {
    max_files: number;
    max_file_mb: number;
    max_total_pages: number;
  };
}

export interface UploadedDocMeta {
  name: string;
  size_bytes: number;
  pages: number;
}

export interface PreviewPage {
  filename: string;
  page: number;
  text: string;
}

export interface SourcePassage {
  filename: string;
  page: number;
  text: string;
}

export interface ClaimItem {
  text: string;
  refs: {
    filename: string;
    page: number;
  }[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  status?: "answered" | "conflict" | "not_found";
  claims?: ClaimItem[];
  sources?: SourcePassage[];
  latency?: string;
}

export interface SavedWorkspaceSummary {
  id: string;
  title: string;
  created_at: string;
  status: "saving" | "ready" | "deleting";
}
