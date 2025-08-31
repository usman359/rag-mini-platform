import warnings
import logging

# Suppress all warnings and errors at the very beginning
warnings.filterwarnings("ignore")
logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.ERROR)
logging.getLogger("chromadb.telemetry").setLevel(logging.ERROR)
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.ERROR)

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
import uuid
import json
import os
from typing import List, Dict, Any

from .models import (
    DocumentUploadResponse, QueryRequest, QueryResponse, 
    HealthCheckResponse, DocumentInfo
)
from .vector_store import VectorStore
from .document_processor import DocumentProcessor
from .mcp_protocol import MCPProtocol
from .database import Database
from .config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAG Mini-Platform API",
    description="A lightweight Retrieval-Augmented Generation system with MCP protocol",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
vector_store = VectorStore()
document_processor = DocumentProcessor()
mcp_protocol = MCPProtocol()

# Initialize database
DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(os.path.dirname(__file__)), "documents.db"))
database = Database(DB_PATH)

# Migrate from JSON if needed
JSON_METADATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "document_metadata.json")
database.migrate_from_json(JSON_METADATA_FILE)

logger.info(f"Database initialized with {database.get_document_count()} documents")

@app.get("/", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check vector store
        stats = vector_store.get_collection_stats()
        
        # Check LLM connection (Groq)
        llm_status = "healthy"
        try:
            # Test Groq connection
            mcp_protocol.client.models_list()
        except Exception as e:
            logger.error(f"LLM connection failed: {e}")
            llm_status = "unhealthy"
        
        return HealthCheckResponse(
            status="healthy",
            timestamp=datetime.now(),
            services={
                "vector_store": "healthy" if stats["total_documents"] >= 0 else "unhealthy",
                "llm": llm_status,
                "document_processor": "healthy"
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Service unhealthy")

@app.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document"""
    try:
        # Validate file
        if not document_processor.validate_file(file.filename, file.size):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file. Must be PDF or TXT, max 10MB"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Process document
        chunks, metadata_list = document_processor.process_document(file_content, file.filename)
        
        # Add to vector store
        chunk_ids = vector_store.add_documents(chunks, metadata_list)
        
        # Store document metadata in database
        document_id = str(uuid.uuid4())
        metadata = {
            "filename": file.filename,
            "upload_date": datetime.now(),
            "chunks_count": len(chunks),
            "file_size": len(file_content),
            "chunk_ids": chunk_ids
        }
        
        if not database.add_document(document_id, metadata):
            raise HTTPException(status_code=500, detail="Failed to save document metadata")
        
        logger.info(f"Document uploaded successfully: {file.filename}")
        
        return DocumentUploadResponse(
            message="Document uploaded and processed successfully",
            document_id=document_id,
            filename=file.filename,
            chunks_processed=len(chunks)
        )
        
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def query_knowledge_base(request: QueryRequest):
    """Query the knowledge base using MCP protocol"""
    try:
        # Prepare filter for document-specific queries
        filter_dict = None
        if request.document_filter:
            # Get document metadata to filter by filename
            doc_data = database.get_document(request.document_filter)
            if doc_data:
                filter_dict = {"filename": doc_data["filename"]}
        
        # Search for relevant documents with more context
        search_results = vector_store.search(request.query, max(request.top_k, 8), filter_dict)
        
        # Extract context from search results
        context_documents = search_results.get("documents", [])
        context_metadatas = search_results.get("metadatas", [])
        
        # Process through MCP protocol
        mcp_result = mcp_protocol.process_query(
            request.query,
            context_documents,
            request.conversation_history
        )
        
        # Extract source filenames
        sources = list(set([meta.get("filename", "Unknown") for meta in context_metadatas]))
        
        return QueryResponse(
            response=mcp_result["response"],
            context_used=context_documents,
            sources=sources,
            conversation_id=mcp_result["conversation_id"],
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/conversations", response_model=Dict[str, str])
async def create_conversation(document_id: str = Query(...)):
    """Create a new conversation for a document"""
    try:
        # Verify document exists
        doc_data = database.get_document(document_id)
        if not doc_data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Create new conversation
        conversation_id = database.create_conversation(document_id)
        
        return {"conversation_id": conversation_id}
        
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations/{document_id}")
async def get_document_conversations(document_id: str):
    """Get all conversations for a document"""
    try:
        # Verify document exists
        doc_data = database.get_document(document_id)
        if not doc_data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        conversations = database.get_document_conversations(document_id)
        return conversations
        
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: str):
    """Get all messages for a conversation"""
    try:
        messages = database.get_conversation_messages(conversation_id)
        return messages
        
    except Exception as e:
        logger.error(f"Error getting conversation messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/conversations/{conversation_id}/messages")
async def add_message_to_conversation(
    conversation_id: str, 
    message: Dict[str, Any]
):
    """Add a message to a conversation"""
    try:
        success = database.add_message(
            conversation_id=conversation_id,
            role=message["role"],
            content=message["content"],
            sources=message.get("sources")
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save message")
        
        return {"message": "Message saved successfully"}
        
    except Exception as e:
        logger.error(f"Error adding message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation and all its messages"""
    try:
        success = database.delete_conversation(conversation_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {"message": "Conversation deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents", response_model=List[DocumentInfo])
async def list_documents():
    """List all uploaded documents"""
    try:
        db_documents = database.get_all_documents()
        documents = []
        for doc_data in db_documents:
            documents.append(DocumentInfo(
                document_id=doc_data["id"],
                filename=doc_data["filename"],
                upload_date=doc_data["upload_date"],
                chunks_count=doc_data["chunks_count"],
                file_size=doc_data["file_size"]
            ))
        
        return documents
        
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and its chunks"""
    try:
        # Get document from database
        doc_data = database.get_document(document_id)
        if not doc_data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get chunk IDs for this document
        chunk_ids = doc_data["chunk_ids"]
        
        # Delete chunks from vector store
        for chunk_id in chunk_ids:
            vector_store.delete_document(chunk_id)
        
        # Remove from database
        if not database.delete_document(document_id):
            raise HTTPException(status_code=500, detail="Failed to delete document from database")
        
        logger.info(f"Document deleted successfully: {document_id}")
        
        return {"message": "Document deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    try:
        vector_stats = vector_store.get_collection_stats()
        
        return {
            "total_documents": database.get_document_count(),
            "total_chunks": vector_stats["total_documents"],
            "llm_provider": "Groq",
            "llm_model": settings.GROQ_MODEL
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
