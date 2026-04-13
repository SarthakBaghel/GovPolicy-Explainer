import axios from "axios";
import { getToken } from "@/lib/auth";
import type {
  AuthResponse,
  DocumentItem,
  DocumentsResponse,
  RagQueryResponse,
  RagSearchItem,
  UploadResponse,
} from "@/types";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000",
  timeout: 30000,
});

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (!error.response) {
      return `Could not reach the backend API at ${api.defaults.baseURL}.`;
    }
    return (error.response?.data?.detail || error.response?.data?.message || error.message) as string;
  }
  return "Unexpected error. Please try again.";
}

export const authApi = {
  register: (email: string, password: string) => api.post<{ message: string }>("/api/auth/register", { email, password }),
  login: (email: string, password: string) => api.post<AuthResponse>("/api/auth/login", { email, password }),
};

export const documentApi = {
  upload: async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post<UploadResponse>("/api/rag/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    return response.data;
  },
  list: async () => {
    const response = await api.get<DocumentsResponse>("/api/documents/documents");
    return response.data;
  },
  getById: async (docId: string) => {
    const response = await api.get<DocumentItem>(`/api/documents/documents/${docId}`);
    return response.data;
  },
  remove: async (docId: string) => {
    const response = await api.delete<{ message: string; doc_id: string }>(`/api/documents/documents/${docId}`);
    return response.data;
  },
};

export const ragApi = {
  queryDocument: async (question: string, docName: string, k = 3) => {
    const response = await api.post<RagQueryResponse>("/api/rag/query", {
      question,
      k,
      doc_name: docName,
    });
    return response.data;
  },
  searchDocument: async (query: string, docName: string, k = 3) => {
    const response = await api.post<RagSearchItem[]>("/api/rag/search", {
      query,
      k,
      doc_name: docName,
    });
    return response.data;
  },
};

export default api;
