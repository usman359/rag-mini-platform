import React, { useRef, useState } from "react";
import { toast } from "react-hot-toast";
import apiService from "../services/api";

interface DocumentUploadProps {
  onUploadSuccess: () => void;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({ onUploadSuccess }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (file: File) => {
    if (!file) return;

    // Validate file type
    const allowedTypes = [".txt", ".pdf"];
    const fileExtension = file.name
      .toLowerCase()
      .substring(file.name.lastIndexOf("."));

    if (!allowedTypes.includes(fileExtension)) {
      toast.error("Please upload a PDF or TXT file");
      return;
    }

    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      toast.error("File size must be less than 10MB");
      return;
    }

    setIsUploading(true);
    const loadingToast = toast.loading("Uploading document...");

    try {
      await apiService.uploadDocument(file);
      toast.success(`Document "${file.name}" uploaded successfully!`, {
        id: loadingToast,
      });
      onUploadSuccess();
    } catch (error) {
      console.error("Upload error:", error);
      toast.error("Failed to upload document. Please try again.", {
        id: loadingToast,
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragActive
            ? "border-blue-500 bg-blue-50"
            : "border-gray-300 hover:border-gray-400"
        } ${isUploading ? "opacity-50 pointer-events-none" : ""}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="space-y-4">
          <div className="text-6xl text-gray-400">📄</div>
          <div>
            <h3 className="text-lg font-medium text-gray-900">
              Upload Document
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              Drag and drop a PDF or TXT file, or click to browse
            </p>
          </div>

          <div className="text-xs text-gray-400">Maximum file size: 10MB</div>

          <button
            type="button"
            onClick={openFileDialog}
            disabled={isUploading}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {isUploading ? "Uploading..." : "Choose File"}
          </button>
        </div>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.txt"
        onChange={handleFileInput}
        className="hidden"
      />
    </div>
  );
};

export default DocumentUpload;
