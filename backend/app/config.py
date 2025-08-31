import os
from dotenv import load_dotenv
import logging
import warnings

# Load environment variables
load_dotenv()

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="urllib3")

# Configure logging to suppress ChromaDB telemetry errors
logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.ERROR)
logging.getLogger("chromadb.telemetry").setLevel(logging.ERROR)
logging.getLogger("chromadb").setLevel(logging.WARNING)

# Suppress urllib3 warnings
logging.getLogger("urllib3").setLevel(logging.ERROR)

class Settings:
    # API Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")
    
    # Vector Store Configuration
    CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db"))
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    # Document Processing
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))  # 10MB
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
    
    # MCP Protocol Prompts
    LLM_A_SYSTEM_PROMPT = """You are a helpful, knowledgeable assistant who answers questions based on the provided document context. 

IMPORTANT GUIDELINES:
1. Answer like a real person would - naturally, conversationally, and directly
2. If the information is in the context, provide it clearly and accurately
3. If the information is NOT in the context, say "I don't see that information in the document" or similar
4. Don't make assumptions or guess - only use what's explicitly stated in the context
5. Be concise but thorough - give complete answers without unnecessary verbosity
6. For simple questions, give simple answers
7. If someone asks "ok" or similar, just acknowledge it briefly or ask for clarification

Remember: You're having a natural conversation, not writing a formal report."""

    LLM_B_SYSTEM_PROMPT = """You are helping to make responses more natural and conversational. 

Your job is to:
1. Make the response sound like a real person talking
2. Remove any robotic or overly formal language
3. Keep it concise and direct
4. Maintain all the important information
5. Make it feel like a natural conversation

Examples of what to fix:
- "Based on the provided context" → Just give the answer directly
- "The information indicates that" → Just state the fact
- "According to the document" → Remove this phrase
- "Here is the refined response:" → Remove this

Make it sound like you're talking to a friend, not writing a report."""

settings = Settings()
