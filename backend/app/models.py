from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class DocumentUploadResponse(BaseModel):
    message: str
    document_id: str
    filename: str
    chunks_processed: int

class QueryRequest(BaseModel):
    query: str
    conversation_history: Optional[List[Dict[str, str]]] = []
    top_k: Optional[int] = 5
    document_filter: Optional[str] = None  # Document ID to filter queries

class QueryResponse(BaseModel):
    response: str
    context_used: List[str]
    sources: List[str]
    conversation_id: str
    timestamp: datetime

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime

class ConversationHistory(BaseModel):
    conversation_id: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime

class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    upload_date: datetime
    chunks_count: int
    file_size: int

class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    services: Dict[str, str]
