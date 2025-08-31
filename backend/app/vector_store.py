# Disable ChromaDB telemetry completely - must be set before any imports
import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_ENABLED"] = "False"

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
import uuid
from typing import List, Dict, Any, Optional
from .config import settings
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                is_persistent=True,
                persist_directory=settings.CHROMA_PERSIST_DIRECTORY
            )
        )
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        
    def add_documents(self, texts: List[str], metadata: List[Dict[str, Any]]) -> List[str]:
        """Add documents to the vector store"""
        try:
            # Generate embeddings
            embeddings = self.embedding_model.encode(texts).tolist()
            
            # Generate IDs
            ids = [str(uuid.uuid4()) for _ in texts]
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadata,
                ids=ids
            )
            
            logger.info(f"Added {len(texts)} documents to vector store")
            return ids
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise
    
    def search(self, query: str, top_k: int = 5, filter_dict: Optional[Dict] = None) -> Dict[str, Any]:
        """Search for similar documents"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()
            
            # Search in collection
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=top_k,
                where=filter_dict
            )
            
            return {
                "documents": results["documents"][0] if results["documents"] else [],
                "metadatas": results["metadatas"][0] if results["metadatas"] else [],
                "distances": results["distances"][0] if results["distances"] else [],
                "ids": results["ids"][0] if results["ids"] else []
            }
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection.name
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"total_documents": 0, "collection_name": "unknown"}
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document from the vector store"""
        try:
            self.collection.delete(ids=[document_id])
            logger.info(f"Deleted document {document_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False
