import React, { useState, useEffect } from "react";
import { Toaster } from "react-hot-toast";
import DocumentUpload from "./components/document-upload";
import DocumentList from "./components/document-list";
import ChatInterface from "./components/chat-interface";
import SystemStats from "./components/system-stats";
import { DocumentInfo, SystemStats as SystemStatsType } from "./types";
import apiService from "./services/api";
import "./App.css";
import Spinner from "./ui/spinner";

function App() {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [stats, setStats] = useState<SystemStatsType>({
    total_documents: 0,
    total_chunks: 0,
  });
  const [activeTab, setActiveTab] = useState<"upload" | "chat" | "documents">(
    "upload"
  );
  const [isLoading, setIsLoading] = useState(true);
  const [backendAvailable, setBackendAvailable] = useState<boolean | null>(
    null
  );
  const [retryCount, setRetryCount] = useState(0);

  const fetchDocuments = async () => {
    try {
      const docs = await apiService.listDocuments();
      setDocuments(docs);
    } catch (error) {
      console.error("Error fetching documents:", error);
    }
  };

  const fetchStats = async () => {
    try {
      const systemStats = await apiService.getStats();
      setStats(systemStats);
    } catch (error) {
      console.error("Error fetching stats:", error);
    }
  };

  const handleUploadSuccess = async () => {
    await fetchDocuments();
    await fetchStats();
  };

  const handleDocumentDeleted = async () => {
    await fetchDocuments();
    await fetchStats();
  };

  useEffect(() => {
    const initializeApp = async () => {
      try {
        // Check if backend is available
        await apiService.healthCheck();
        setBackendAvailable(true);
        setRetryCount(0);

        // Fetch documents and stats in parallel
        await Promise.all([fetchDocuments(), fetchStats()]);
      } catch (error) {
        console.error("Backend not available:", error);
        setBackendAvailable(false);
      } finally {
        setIsLoading(false);
      }
    };

    initializeApp();
  }, [retryCount]);

  if (isLoading) {
    return <Spinner message="Loading RAG Mini-Platform..." />;
  }

  // Show backend connection error
  if (backendAvailable === false) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md mx-auto text-center">
          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
              <svg
                className="h-6 w-6 text-red-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Backend Service Unavailable
            </h3>
            <p className="text-sm text-gray-600 mb-6">
              The RAG Mini-Platform backend service is not running. Please
              ensure the backend server is started.
            </p>
            <div className="space-y-3">
              <div className="bg-gray-50 rounded-md p-3 text-left">
                <p className="text-xs font-medium text-gray-700 mb-1">
                  To start the backend:
                </p>
                <code className="text-xs text-gray-600 block">
                  cd backend && source venv/bin/activate && uvicorn app.main:app
                  --reload --host 0.0.0.0 --port 8000
                </code>
              </div>
              <button
                onClick={() => {
                  setIsLoading(true);
                  setBackendAvailable(null);
                  setRetryCount((prev) => prev + 1);
                }}
                className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
              >
                Retry Connection
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster position="top-right" />

      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                RAG Mini-Platform
              </h1>
              <p className="text-sm text-gray-500">
                Retrieval-Augmented Generation with MCP Protocol
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-500">
                Powered by ChromaDB + OpenAI
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            <button
              onClick={(e) => {
                e.preventDefault();
                setActiveTab("upload");
              }}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === "upload"
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              Upload Documents
            </button>
            <button
              onClick={(e) => {
                e.preventDefault();
                setActiveTab("chat");
              }}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === "chat"
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              Chat Interface
            </button>
            <button
              onClick={(e) => {
                e.preventDefault();
                setActiveTab("documents");
              }}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === "documents"
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              Document Management
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === "upload" && (
          <div className="space-y-8">
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Upload Documents
              </h2>
              <DocumentUpload onUploadSuccess={handleUploadSuccess} />
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                How it works
              </h3>
              <div className="text-sm text-gray-600 space-y-2">
                <p>1. Upload PDF or TXT documents (max 10MB each)</p>
                <p>2. Documents are automatically processed and chunked</p>
                <p>3. Chunks are embedded and stored in the vector database</p>
                <p>4. Use the chat interface to query your knowledge base</p>
              </div>
            </div>
          </div>
        )}

        {activeTab === "chat" && (
          <div className="h-[calc(100vh-200px)]">
            <ChatInterface documents={documents} />
          </div>
        )}

        {activeTab === "documents" && (
          <div className="space-y-8">
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Document Management
              </h2>
              <DocumentList
                documents={documents}
                onDocumentDeleted={handleDocumentDeleted}
              />
            </div>

            <SystemStats stats={stats} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
