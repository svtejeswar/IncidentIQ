import type {
  ChatResponse,
  Document,
  DocumentListResponse,
  DocumentType,
  PlatformStats,
  SearchResponse,
  SimilarIncidentsResponse,
} from "@/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

type ChatRequest = {
  message: string;
  conversation_id?: string;
  history?: { role: string; content: string }[];
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail ?? "Request failed");
  }
  return res.json() as Promise<T>;
}

export const api = {
  documents: {
    upload: async (
      file: File,
      documentType: DocumentType,
      title?: string
    ): Promise<Document> => {
      const form = new FormData();
      form.append("file", file);
      form.append("document_type", documentType);
      if (title) form.append("title", title);

      const res = await fetch(`${BASE_URL}/documents`, {
        method: "POST",
        body: form,
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail ?? "Upload failed");
      }
      return res.json();
    },

    list: (skip = 0, limit = 20): Promise<DocumentListResponse> =>
      request(`/documents?skip=${skip}&limit=${limit}`),

    get: (id: string): Promise<Document> => request(`/documents/${id}`),

    delete: (id: string): Promise<void> =>
      request(`/documents/${id}`, { method: "DELETE" }),
  },

  search: {
    query: (payload: {
      query: string;
      limit?: number;
      include_ai_answer?: boolean;
      document_types?: string[];
    }): Promise<SearchResponse> =>
      request("/search", {
        method: "POST",
        body: JSON.stringify(payload),
      }),

    similar: (payload: {
      document_id?: string;
      text?: string;
      limit?: number;
    }): Promise<SimilarIncidentsResponse> =>
      request("/search/similar", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
  },

  assistant: {
    chat: (payload: ChatRequest): Promise<ChatResponse> =>
      request("/assistant/chat", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
  },

  stats: {
    get: (): Promise<PlatformStats> => request("/stats"),
  },
};
