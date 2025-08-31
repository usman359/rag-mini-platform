export interface DocumentInfo {
  document_id: string;
  filename: string;
  upload_date: string;
  chunks_count: number;
  file_size: number;
}

export interface QueryRequest {
  query: string;
  conversation_history: Array<{ role: string; content: string }>;
  top_k?: number;
  document_filter?: string; // Optional document ID to filter queries
}

export interface QueryResponse {
  response: string;
  context_used: string[];
  sources: string[];
  conversation_id: string;
  timestamp: string;
}

export interface DocumentUploadResponse {
  message: string;
  document_id: string;
  filename: string;
  chunks_processed: number;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  sources?: string[];
}

export interface SystemStats {
  total_documents: number;
  total_chunks: number;
}
