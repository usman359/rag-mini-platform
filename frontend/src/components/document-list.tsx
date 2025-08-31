import React, { useState } from "react";
import { toast } from "react-hot-toast";
import { DocumentInfo } from "../types";
import apiService from "../services/api";

interface DocumentListProps {
  documents: DocumentInfo[];
  onDocumentDeleted: () => void;
}

const DocumentList: React.FC<DocumentListProps> = ({
  documents,
  onDocumentDeleted,
}) => {
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleDelete = async (documentId: string) => {
    if (!window.confirm("Are you sure you want to delete this document?")) {
      return;
    }

    setDeletingId(documentId);
    const loadingToast = toast.loading("Deleting document...");

    try {
      await apiService.deleteDocument(documentId);
      toast.success("Document deleted successfully!", { id: loadingToast });
      onDocumentDeleted();
    } catch (error) {
      console.error("Delete error:", error);
      toast.error("Failed to delete document. Please try again.", {
        id: loadingToast,
      });
    } finally {
      setDeletingId(null);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return (
      new Date(dateString).toLocaleDateString() +
      " " +
      new Date(dateString).toLocaleTimeString()
    );
  };

  if (documents.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        <div className="text-4xl mb-4">📚</div>
        <p>No documents uploaded yet</p>
        <p className="text-sm">Upload some documents to get started</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-medium text-gray-900">Uploaded Documents</h3>

      <div className="grid gap-4">
        {documents.map((doc) => (
          <div
            key={doc.document_id}
            className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2">
                  <div className="text-2xl">
                    {doc.filename.toLowerCase().endsWith(".pdf") ? "📄" : "📝"}
                  </div>
                  <div className="min-w-0 flex-1">
                    <h4 className="text-sm font-medium text-gray-900 truncate">
                      {doc.filename}
                    </h4>
                    <div className="flex items-center space-x-4 text-xs text-gray-500 mt-1">
                      <span>{formatFileSize(doc.file_size)}</span>
                      <span>{doc.chunks_count} chunks</span>
                      <span>{formatDate(doc.upload_date)}</span>
                    </div>
                  </div>
                </div>
              </div>

              <button
                onClick={() => handleDelete(doc.document_id)}
                disabled={deletingId === doc.document_id}
                className="ml-4 text-red-600 hover:text-red-800 disabled:opacity-50 disabled:cursor-not-allowed"
                title="Delete document"
              >
                {deletingId === doc.document_id ? (
                  <div role="status">
                    <svg
                      aria-hidden="true"
                      className="w-4 h-4 text-gray-200 animate-spin dark:text-gray-300 fill-red-600"
                      viewBox="0 0 100 101"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
                        fill="currentColor"
                      />
                      <path
                        d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
                        fill="currentFill"
                      />
                    </svg>
                    <span className="sr-only">Loading...</span>
                  </div>
                ) : (
                  <svg
                    className="h-4 w-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                )}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DocumentList;
