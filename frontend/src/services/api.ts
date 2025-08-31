import axios from "axios";
import {
  DocumentInfo,
  QueryRequest,
  QueryResponse,
  DocumentUploadResponse,
  SystemStats,
} from "../types";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const apiService = {
  // Health check
  healthCheck: async () => {
    try {
      const response = await api.get("/");
      return response.data;
    } catch (error: any) {
      if (error.code === "ERR_NETWORK" || error.message === "Network Error") {
        throw new Error(
          "Backend service is not running. Please start the backend server."
        );
      }
      throw error;
    }
  },

  // Document management
  uploadDocument: async (file: File): Promise<DocumentUploadResponse> => {
    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await api.post("/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      return response.data;
    } catch (error: any) {
      if (error.code === "ERR_NETWORK" || error.message === "Network Error") {
        throw new Error(
          "Cannot upload document: Backend service is not available."
        );
      }
      throw error;
    }
  },

  listDocuments: async (): Promise<DocumentInfo[]> => {
    try {
      const response = await api.get("/documents");
      return response.data;
    } catch (error: any) {
      if (error.code === "ERR_NETWORK" || error.message === "Network Error") {
        throw new Error(
          "Cannot fetch documents: Backend service is not available."
        );
      }
      throw error;
    }
  },

  deleteDocument: async (documentId: string): Promise<void> => {
    await api.delete(`/documents/${documentId}`);
  },

  // Query and chat
  queryKnowledgeBase: async (request: QueryRequest): Promise<QueryResponse> => {
    try {
      const response = await api.post("/query", request);
      return response.data;
    } catch (error: any) {
      if (error.code === "ERR_NETWORK" || error.message === "Network Error") {
        throw new Error("Cannot send query: Backend service is not available.");
      }
      throw error;
    }
  },

  // Chat history management
  createConversation: async (
    documentId: string
  ): Promise<{ conversation_id: string }> => {
    try {
      const response = await api.post("/conversations", null, {
        params: { document_id: documentId },
      });
      return response.data;
    } catch (error: any) {
      if (error.code === "ERR_NETWORK" || error.message === "Network Error") {
        throw new Error(
          "Cannot create conversation: Backend service is not available."
        );
      }
      throw error;
    }
  },

  getDocumentConversations: async (documentId: string): Promise<any[]> => {
    try {
      const response = await api.get(`/conversations/${documentId}`);
      return response.data;
    } catch (error: any) {
      if (error.code === "ERR_NETWORK" || error.message === "Network Error") {
        throw new Error(
          "Cannot fetch conversations: Backend service is not available."
        );
      }
      throw error;
    }
  },

  getConversationMessages: async (conversationId: string): Promise<any[]> => {
    try {
      const response = await api.get(
        `/conversations/${conversationId}/messages`
      );
      return response.data;
    } catch (error: any) {
      if (error.code === "ERR_NETWORK" || error.message === "Network Error") {
        throw new Error(
          "Cannot fetch messages: Backend service is not available."
        );
      }
      throw error;
    }
  },

  saveMessage: async (conversationId: string, message: any): Promise<void> => {
    try {
      await api.post(`/conversations/${conversationId}/messages`, message);
    } catch (error: any) {
      if (error.code === "ERR_NETWORK" || error.message === "Network Error") {
        throw new Error(
          "Cannot save message: Backend service is not available."
        );
      }
      throw error;
    }
  },

  deleteConversation: async (conversationId: string): Promise<void> => {
    try {
      await api.delete(`/conversations/${conversationId}`);
    } catch (error: any) {
      if (error.code === "ERR_NETWORK" || error.message === "Network Error") {
        throw new Error(
          "Cannot delete conversation: Backend service is not available."
        );
      }
      throw error;
    }
  },

  // System stats
  getStats: async (): Promise<SystemStats> => {
    try {
      const response = await api.get("/stats");
      return response.data;
    } catch (error: any) {
      if (error.code === "ERR_NETWORK" || error.message === "Network Error") {
        throw new Error(
          "Cannot fetch stats: Backend service is not available."
        );
      }
      throw error;
    }
  },
};

export default apiService;
