import {
  AuthUser,
  ChatMessage,
  ClaimItem,
  HealthStatus,
  PreviewPage,
  SavedWorkspaceSummary,
  SourcePassage,
  UploadedDocMeta,
} from "./types";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export function getApiBase(): string {
  const configured = process.env.NEXT_PUBLIC_API_URL?.trim();
  if (configured) {
    return configured.replace(/\/+$/, "");
  }
  if (typeof window !== "undefined") {
    return `http://${window.location.hostname}:8000/api`;
  }
  return "http://127.0.0.1:8000/api";
}

async function requestJson<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null
): Promise<T> {
  const headers = new Headers(options.headers || {});
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  if (!(options.body instanceof FormData) && options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  let res: Response;
  try {
    res = await fetch(`${getApiBase()}${path}`, {
      ...options,
      headers,
    });
  } catch {
    throw new ApiError(
      "Cannot reach the application backend API. Ensure the FastAPI server is running on port 8000.",
      0
    );
  }

  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const detail =
      data && typeof data.detail === "string"
        ? data.detail
        : `Request failed with status ${res.status}.`;
    throw new ApiError(detail, res.status);
  }
  return data as T;
}

export function getHealth(): Promise<HealthStatus> {
  return requestJson<HealthStatus>("/health", { method: "GET" });
}

export function loginUser(
  email: string,
  password: string
): Promise<{ token: string; user: AuthUser }> {
  return requestJson("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function getMe(token: string): Promise<{ user: AuthUser }> {
  return requestJson("/auth/me", { method: "GET" }, token);
}

export function signupUser(
  email: string,
  password: string,
  confirmation: string
): Promise<{ message: string }> {
  return requestJson("/auth/signup", {
    method: "POST",
    body: JSON.stringify({ email, password, confirmation }),
  });
}

export function requestRecovery(email: string): Promise<{ message: string }> {
  return requestJson("/auth/recover", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}

export function resetPassword(
  email: string,
  code: string,
  password: string,
  confirmation: string
): Promise<{ message: string }> {
  return requestJson("/auth/reset", {
    method: "POST",
    body: JSON.stringify({ email, code, password, confirmation }),
  });
}

export function logoutUser(token: string): Promise<{
  signed_out: boolean;
  remote_failed: boolean;
  cleanup_failed: boolean;
  notice: string;
}> {
  return requestJson("/auth/logout", { method: "POST" }, token);
}

export function previewDocuments(
  token: string,
  files: File[]
): Promise<{
  pages: PreviewPage[];
  documents: UploadedDocMeta[];
  total_pages: number;
  selection_signature: [string, string][];
}> {
  const form = new FormData();
  files.forEach((f) => form.append("files", f));
  return requestJson("/documents/preview", { method: "POST", body: form }, token);
}

export function indexDocuments(
  token: string,
  params: { consent: boolean; files?: File[]; sessionId?: string }
): Promise<{
  session_id: string;
  documents: UploadedDocMeta[];
  total_pages: number;
  passage_count: number;
  provider_identity: string[];
  provider_label: string;
  saved_workspace_id: string | null;
}> {
  const form = new FormData();
  form.append("consent", String(params.consent));
  if (params.sessionId) {
    form.append("session_id", params.sessionId);
  }
  if (params.files) {
    params.files.forEach((f) => form.append("files", f));
  }
  return requestJson("/documents/index", { method: "POST", body: form }, token);
}

export function getSessionState(
  token: string,
  sessionId: string
): Promise<{
  session_id: string;
  documents: UploadedDocMeta[];
  total_pages: number;
  passage_count: number;
  indexed: boolean;
  cleanup_blocked: boolean;
  provider_changed: boolean;
  provider_identity: string[] | null;
  saved_workspace_id: string | null;
  messages: {
    role: "user" | "assistant";
    content: string;
    status?: "answered" | "conflict" | "not_found";
    claims?: ClaimItem[];
    sources?: SourcePassage[];
    latency?: string;
  }[];
}> {
  return requestJson(`/sessions/${encodeURIComponent(sessionId)}`, { method: "GET" }, token);
}

export function clearSessionChat(
  token: string,
  sessionId: string
): Promise<{ cleared: boolean }> {
  return requestJson(
    `/sessions/${encodeURIComponent(sessionId)}/clear`,
    { method: "POST" },
    token
  );
}

export function resetSession(token: string, sessionId: string): Promise<{ reset: boolean }> {
  return requestJson(`/sessions/${encodeURIComponent(sessionId)}/reset`, { method: "POST" }, token);
}

export function askQuestion(
  token: string,
  params: {
    session_id: string;
    question: string;
    history: { role: string; content: string }[];
    consent: boolean;
  }
): Promise<{
  status: "answered" | "conflict" | "not_found";
  content: string;
  claims: ClaimItem[];
  sources: SourcePassage[];
  latency: string;
}> {
  return requestJson(
    "/chat",
    {
      method: "POST",
      body: JSON.stringify(params),
    },
    token
  );
}

export function exportChatConversation(
  token: string,
  messages: ChatMessage[]
): Promise<{ filename: string; content: string }> {
  return requestJson(
    "/chat/export",
    {
      method: "POST",
      body: JSON.stringify({
        messages: messages.map((m) => ({
          role: m.role,
          content: m.content,
          sources: m.sources || [],
        })),
      }),
    },
    token
  );
}

export function listWorkspaces(
  token: string
): Promise<{ workspaces: SavedWorkspaceSummary[] }> {
  return requestJson("/workspaces", { method: "GET" }, token);
}

export function saveWorkspaceFromSession(
  token: string,
  sessionId: string,
  title: string,
  messages: ChatMessage[]
): Promise<{ workspace_id: string; title: string }> {
  return requestJson(
    "/workspaces/save",
    {
      method: "POST",
      body: JSON.stringify({
        session_id: sessionId,
        title,
        messages: messages.map((m) => ({
          role: m.role,
          content: m.content,
          ...(m.sources ? { sources: m.sources } : {}),
        })),
      }),
    },
    token
  );
}

export function saveWorkspaceFromFiles(
  token: string,
  title: string,
  files: File[],
  messages: ChatMessage[]
): Promise<{
  workspace_id: string;
  session_id: string;
  title: string;
  documents: UploadedDocMeta[];
  total_pages: number;
}> {
  const form = new FormData();
  form.append("title", title);
  form.append(
    "messages",
    JSON.stringify(
      messages.map((m) => ({
        role: m.role,
        content: m.content,
        ...(m.sources ? { sources: m.sources } : {}),
      }))
    )
  );
  files.forEach((f) => form.append("files", f));
  return requestJson("/workspaces/save-files", { method: "POST", body: form }, token);
}

export function loadWorkspace(
  token: string,
  workspaceId: string
): Promise<{
  session_id: string;
  workspace_id: string;
  documents: UploadedDocMeta[];
  total_pages: number;
  messages: { role: "user" | "assistant"; content: string; sources?: SourcePassage[] }[];
  indexed: boolean;
}> {
  return requestJson(
    "/workspaces/load",
    {
      method: "POST",
      body: JSON.stringify({ workspace_id: workspaceId }),
    },
    token
  );
}

export function saveWorkspaceChat(
  token: string,
  workspaceId: string,
  messages: ChatMessage[]
): Promise<{ saved: boolean; workspace_id: string }> {
  return requestJson(
    `/workspaces/${encodeURIComponent(workspaceId)}/chat`,
    {
      method: "PATCH",
      body: JSON.stringify({
        messages: messages.map((m) => ({
          role: m.role,
          content: m.content,
          ...(m.sources ? { sources: m.sources } : {}),
        })),
      }),
    },
    token
  );
}

export function deleteWorkspace(
  token: string,
  workspaceId: string
): Promise<{ deleted: boolean; workspace_id: string }> {
  return requestJson(
    `/workspaces/${encodeURIComponent(workspaceId)}`,
    { method: "DELETE" },
    token
  );
}
