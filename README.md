# RAG Mini-Platform

A lightweight Retrieval-Augmented Generation (RAG) system with Multi-Context Protocol (MCP) implementation, built with FastAPI, React, ChromaDB, and Groq.

## Features

- **Document Storage & Retrieval**: Upload and process PDF/TXT documents using ChromaDB vector database
- **KNN-based Retrieval**: Semantic search with sentence transformers
- **Multi-Context Protocol (MCP)**: Two-stage LLM processing (LLM-A for retrieval, LLM-B for refinement)
- **Conversation Memory**: Maintain context across chat sessions
- **Modern Web Interface**: React-based UI with drag-and-drop file upload
- **Docker Deployment**: Containerized application with docker-compose

## Architecture

### Backend (FastAPI)

- **Vector Store**: ChromaDB with sentence-transformers embeddings
- **Document Processing**: PDF/TXT extraction and chunking
- **MCP Protocol**: LLM-A (retrieval) + LLM-B (refinement) pipeline
- **API Endpoints**: RESTful API for document management and queries

### Frontend (React)

- **Document Upload**: Drag-and-drop interface with file validation
- **Chat Interface**: Real-time conversation with knowledge base
- **Document Management**: View and delete uploaded documents
- **System Monitoring**: Real-time statistics and health checks

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Groq API key

### ⚠️ Development Note

This project is designed for **local development and demonstration purposes**. It's optimized for hands-on development and testing rather than cloud deployment. See [DEPLOYMENT.md](./DEPLOYMENT.md) for usage guidelines.

### Option 1: Using the Start Script (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd rag-mini-platform

# Run the start script
./start.sh

# The script will:
# - Check Docker is running
# - Create .env file from template
# - Validate your API key
# - Start all services
# - Show access information
```

### Option 2: Manual Setup

```bash
# Clone the repository
git clone <repository-url>
cd rag-mini-platform

# Copy environment file
cp env.example .env

# Edit .env and add your Groq API key
GROQ_API_KEY=your_actual_api_key_here

# Build and start all services
docker-compose up --build
```

### Access the Application

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/

### Management Commands

```bash
# Using the start script
./start.sh          # Start the application
./start.sh stop     # Stop all services
./start.sh restart  # Restart all services
./start.sh logs     # View logs
./start.sh status   # Check service status

# Using docker-compose directly
docker-compose up --build    # Start services
docker-compose down          # Stop services
docker-compose restart       # Restart services
docker-compose logs -f       # View logs
docker-compose ps            # Check status

# Test deployment
python3 test_deployment.py   # Run deployment tests
```

### 3. Development Setup (Optional)

#### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Development

```bash
cd frontend
npm install
npm start
```

## Usage

### 1. Upload Documents

- Navigate to the "Upload Documents" tab
- Drag and drop PDF or TXT files (max 10MB each)
- Documents are automatically processed and chunked
- Chunks are embedded and stored in the vector database

### 2. Chat with Knowledge Base

- Go to the "Chat Interface" tab
- Ask questions about your uploaded documents
- The system uses MCP protocol for enhanced responses
- View source documents for each response

### 3. Manage Documents

- Visit the "Document Management" tab
- View all uploaded documents with metadata
- Delete documents as needed
- Monitor system statistics

## API Endpoints

### Health Check

- `GET /` - System health and service status

### Document Management

- `POST /upload` - Upload and process documents
- `GET /documents` - List all documents
- `DELETE /documents/{id}` - Delete a document

### Query Interface

- `POST /query` - Query the knowledge base with MCP protocol

### System Information

- `GET /stats` - System statistics

## Multi-Context Protocol (MCP)

The system implements a two-stage LLM processing pipeline:

### LLM-A (First Pass)

- Analyzes user query
- Retrieves relevant context from vector database
- Generates initial response based on retrieved context
- Prepares context for LLM-B refinement

### LLM-B (Refinement)

- Reviews context and initial response from LLM-A
- Improves response quality, clarity, and accuracy
- Ensures well-structured and comprehensive answers
- Maintains conversation continuity

## Technical Details

### Vector Database

- **ChromaDB**: Open-source vector database
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Chunking**: RecursiveCharacterTextSplitter (1000 chars, 200 overlap)

### Document Processing

- **Supported Formats**: PDF, TXT
- **File Size Limit**: 10MB per file
- **Text Extraction**: PyPDF2 for PDFs, UTF-8/Latin-1 for TXT

### LLM Integration

- **Provider**: OpenAI API
- **Model**: Configurable (default: gpt-3.5-turbo)
- **Temperature**: 0.7 for LLM-A, 0.5 for LLM-B

## Configuration

### Environment Variables

```bash
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-3.5-turbo
CHROMA_PERSIST_DIRECTORY=./chroma_db
MAX_FILE_SIZE=10485760
```

### Backend Configuration

- Chunk size: 1000 characters
- Chunk overlap: 200 characters
- Top-k retrieval: 5 documents
- Embedding model: all-MiniLM-L6-v2

## Development

### Project Structure

```
rag-mini-platform/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models.py
│   │   ├── vector_store.py
│   │   ├── document_processor.py
│   │   └── mcp_protocol.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   ├── types/
│   │   └── App.tsx
│   └── package.json
├── docker/
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── nginx.conf
├── docker-compose.yml
└── README.md
```

### Adding New Features

1. **Backend**: Add new endpoints in `app/main.py`
2. **Frontend**: Create new components in `src/components/`
3. **Types**: Update TypeScript interfaces in `src/types/`
4. **API**: Extend service layer in `src/services/api.ts`

## Troubleshooting

### Common Issues

1. **OpenAI API Errors**

   - Verify API key in `.env` file
   - Check API quota and billing
   - Ensure model name is correct

2. **Document Upload Failures**

   - Check file size (max 10MB)
   - Verify file format (PDF/TXT only)
   - Ensure backend is running

3. **Vector Database Issues**

   - Check ChromaDB persistence directory
   - Verify disk space
   - Restart backend service

4. **Document Persistence Issues**

   - Document metadata is now stored in SQLite database (`backend/documents.db`)
   - Files survive server restarts thanks to Docker volumes
   - Database automatically migrates from JSON file on first run
   - If documents disappear after restart, check database file permissions

5. **Frontend Connection Issues**
   - Verify backend is running on port 8000
   - Check CORS configuration
   - Ensure API URL is correct

### Logs

```bash
# View backend logs
docker-compose logs backend

# View frontend logs
docker-compose logs frontend

# View all logs
docker-compose logs -f
```

## Performance Considerations

- **Vector Database**: ChromaDB is in-memory by default; consider persistence for production
- **Embedding Model**: all-MiniLM-L6-v2 is fast but consider larger models for better quality
- **Chunking**: Adjust chunk size based on document characteristics
- **Caching**: Consider Redis for conversation memory in production

## Security

- **API Keys**: Never commit API keys to version control
- **File Upload**: Validate file types and sizes
- **CORS**: Configure CORS properly for production
- **Rate Limiting**: Consider implementing rate limiting for production

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Acknowledgments

- ChromaDB for vector database
- OpenAI for LLM capabilities
- FastAPI for backend framework
- React for frontend framework
- Sentence Transformers for embeddings
