import PyPDF2
import io
import os
from typing import List, Dict, Any, Tuple
from langchain.text_splitter import RecursiveCharacterTextSplitter
from .config import settings
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
        )
    
    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def extract_text_from_txt(self, file_content: bytes) -> str:
        """Extract text from TXT file"""
        try:
            return file_content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return file_content.decode('latin-1')
            except Exception as e:
                logger.error(f"Error decoding text file: {e}")
                raise
    
    def process_document(self, file_content: bytes, filename: str) -> Tuple[List[str], List[Dict[str, Any]]]:
        """Process document and return chunks with metadata"""
        try:
            # Extract text based on file extension
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext == '.pdf':
                text = self.extract_text_from_pdf(file_content)
            elif file_ext == '.txt':
                text = self.extract_text_from_txt(file_content)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            
            # Create metadata for each chunk
            metadata_list = []
            for i, chunk in enumerate(chunks):
                metadata = {
                    "filename": filename,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "file_type": file_ext,
                    "file_size": len(file_content)
                }
                metadata_list.append(metadata)
            
            logger.info(f"Processed {filename}: {len(chunks)} chunks created")
            return chunks, metadata_list
            
        except Exception as e:
            logger.error(f"Error processing document {filename}: {e}")
            raise
    
    def validate_file(self, filename: str, file_size: int) -> bool:
        """Validate uploaded file"""
        # Check file size
        if file_size > settings.MAX_FILE_SIZE:
            return False
        
        # Check file extension
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            return False
        
        return True
