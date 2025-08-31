import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = "documents.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create documents table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS documents (
                        id TEXT PRIMARY KEY,
                        filename TEXT NOT NULL,
                        upload_date TEXT NOT NULL,
                        chunks_count INTEGER NOT NULL,
                        file_size INTEGER NOT NULL,
                        chunk_ids TEXT NOT NULL
                    )
                ''')
                
                # Create conversations table for MCP protocol
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversations (
                        id TEXT PRIMARY KEY,
                        created_date TEXT NOT NULL,
                        last_updated TEXT NOT NULL,
                        message_count INTEGER DEFAULT 0
                    )
                ''')
                
                # Migrate existing conversations table if needed
                self._migrate_conversations_table(cursor)
                
                conn.commit()
                logger.info(f"Database initialized at {self.db_path}")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def add_document(self, document_id: str, metadata: Dict[str, Any]) -> bool:
        """Add a document to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO documents 
                    (id, filename, upload_date, chunks_count, file_size, chunk_ids)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    document_id,
                    metadata["filename"],
                    metadata["upload_date"].isoformat() if isinstance(metadata["upload_date"], datetime) else metadata["upload_date"],
                    metadata["chunks_count"],
                    metadata["file_size"],
                    json.dumps(metadata["chunk_ids"])
                ))
                
                conn.commit()
                logger.info(f"Document {document_id} added to database")
                return True
                
        except Exception as e:
            logger.error(f"Error adding document to database: {e}")
            return False
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document from the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, filename, upload_date, chunks_count, file_size, chunk_ids
                    FROM documents WHERE id = ?
                ''', (document_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "filename": row[1],
                        "upload_date": datetime.fromisoformat(row[2]),
                        "chunks_count": row[3],
                        "file_size": row[4],
                        "chunk_ids": json.loads(row[5])
                    }
                return None
                
        except Exception as e:
            logger.error(f"Error getting document from database: {e}")
            return None
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents from the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, filename, upload_date, chunks_count, file_size, chunk_ids
                    FROM documents ORDER BY upload_date DESC
                ''')
                
                documents = []
                for row in cursor.fetchall():
                    documents.append({
                        "id": row[0],
                        "filename": row[1],
                        "upload_date": datetime.fromisoformat(row[2]),
                        "chunks_count": row[3],
                        "file_size": row[4],
                        "chunk_ids": json.loads(row[5])
                    })
                
                return documents
                
        except Exception as e:
            logger.error(f"Error getting all documents from database: {e}")
            return []
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document from the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM documents WHERE id = ?', (document_id,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Document {document_id} deleted from database")
                    return True
                else:
                    logger.warning(f"Document {document_id} not found in database")
                    return False
                
        except Exception as e:
            logger.error(f"Error deleting document from database: {e}")
            return False
    
    def get_document_count(self) -> int:
        """Get the total number of documents"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM documents')
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error getting document count: {e}")
            return 0
    
    def migrate_from_json(self, json_file_path: str) -> bool:
        """Migrate data from JSON file to database"""
        try:
            if not os.path.exists(json_file_path):
                logger.info("No JSON file to migrate from")
                return True
            
            with open(json_file_path, 'r') as f:
                json_data = json.load(f)
            
            migrated_count = 0
            for doc_id, metadata in json_data.items():
                # Convert string date to datetime if needed
                if isinstance(metadata.get("upload_date"), str):
                    metadata["upload_date"] = datetime.fromisoformat(metadata["upload_date"])
                
                if self.add_document(doc_id, metadata):
                    migrated_count += 1
            
            logger.info(f"Migrated {migrated_count} documents from JSON to database")
            return True
            
        except Exception as e:
            logger.error(f"Error migrating from JSON: {e}")
            return False

    def _migrate_conversations_table(self, cursor):
        """Migrate existing conversations table to include document_id column"""
        try:
            # Check if document_id column exists
            cursor.execute("PRAGMA table_info(conversations)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'document_id' not in columns:
                logger.info("Migrating conversations table to add document_id column")
                
                # Add document_id column
                cursor.execute('''
                    ALTER TABLE conversations 
                    ADD COLUMN document_id TEXT
                ''')
                
                # Add foreign key constraint (SQLite doesn't support adding FK constraints to existing tables)
                # We'll handle this in application logic
                logger.info("Added document_id column to conversations table")
            
            # Check if messages table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages'")
            if not cursor.fetchone():
                logger.info("Creating messages table")
                cursor.execute('''
                    CREATE TABLE messages (
                        id TEXT PRIMARY KEY,
                        conversation_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        sources TEXT
                    )
                ''')
                logger.info("Created messages table")
                
        except Exception as e:
            logger.error(f"Error migrating conversations table: {e}")
            raise

    def create_conversation(self, document_id: str) -> str:
        """Create a new conversation for a document"""
        try:
            conversation_id = f"conv_{document_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO conversations (id, document_id, created_date, last_updated, message_count)
                    VALUES (?, ?, ?, ?, 0)
                ''', (
                    conversation_id,
                    document_id,
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                logger.info(f"Created conversation {conversation_id} for document {document_id}")
                return conversation_id
                
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            raise
    
    def add_message(self, conversation_id: str, role: str, content: str, sources: Optional[List[str]] = None) -> bool:
        """Add a message to a conversation"""
        try:
            message_id = f"msg_{conversation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Add message
                cursor.execute('''
                    INSERT INTO messages (id, conversation_id, role, content, timestamp, sources)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    message_id,
                    conversation_id,
                    role,
                    content,
                    datetime.now().isoformat(),
                    json.dumps(sources) if sources else None
                ))
                
                # Update conversation
                cursor.execute('''
                    UPDATE conversations 
                    SET last_updated = ?, message_count = message_count + 1
                    WHERE id = ?
                ''', (datetime.now().isoformat(), conversation_id))
                
                conn.commit()
                logger.info(f"Added message to conversation {conversation_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error adding message: {e}")
            return False
    
    def get_conversation_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a conversation"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, role, content, timestamp, sources
                    FROM messages 
                    WHERE conversation_id = ?
                    ORDER BY timestamp ASC
                ''', (conversation_id,))
                
                messages = []
                for row in cursor.fetchall():
                    messages.append({
                        "id": row[0],
                        "role": row[1],
                        "content": row[2],
                        "timestamp": row[3],
                        "sources": json.loads(row[4]) if row[4] else None
                    })
                
                return messages
                
        except Exception as e:
            logger.error(f"Error getting conversation messages: {e}")
            return []
    
    def get_document_conversations(self, document_id: str) -> List[Dict[str, Any]]:
        """Get all conversations for a document"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, created_date, last_updated, message_count
                    FROM conversations 
                    WHERE document_id = ?
                    ORDER BY last_updated DESC
                ''', (document_id,))
                
                conversations = []
                for row in cursor.fetchall():
                    conversations.append({
                        "id": row[0],
                        "created_date": row[1],
                        "last_updated": row[2],
                        "message_count": row[3]
                    })
                
                return conversations
                
        except Exception as e:
            logger.error(f"Error getting document conversations: {e}")
            return []
    
    def get_latest_conversation(self, document_id: str) -> Optional[str]:
        """Get the most recent conversation ID for a document"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id FROM conversations 
                    WHERE document_id = ?
                    ORDER BY last_updated DESC
                    LIMIT 1
                ''', (document_id,))
                
                row = cursor.fetchone()
                return row[0] if row else None
                
        except Exception as e:
            logger.error(f"Error getting latest conversation: {e}")
            return None
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation and all its messages"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete messages first (due to foreign key constraint)
                cursor.execute('DELETE FROM messages WHERE conversation_id = ?', (conversation_id,))
                
                # Delete conversation
                cursor.execute('DELETE FROM conversations WHERE id = ?', (conversation_id,))
                
                conn.commit()
                logger.info(f"Deleted conversation {conversation_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting conversation: {e}")
            return False
    
    def get_conversation_stats(self) -> Dict[str, int]:
        """Get conversation statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) FROM conversations')
                total_conversations = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM messages')
                total_messages = cursor.fetchone()[0]
                
                return {
                    "total_conversations": total_conversations,
                    "total_messages": total_messages
                }
                
        except Exception as e:
            logger.error(f"Error getting conversation stats: {e}")
            return {"total_conversations": 0, "total_messages": 0}
