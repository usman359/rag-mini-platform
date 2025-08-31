import React, { useEffect, useRef, useState } from "react";
import { toast } from "react-hot-toast";
import apiService from "../services/api";
import { ChatMessage } from "../types";

interface ChatInterfaceProps {
  documents: any[];
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ documents }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<string | null>(null);
  const [showDocumentSelector, setShowDocumentSelector] = useState(true);
  const [currentConversationId, setCurrentConversationId] = useState<
    string | null
  >(null);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop =
        messagesContainerRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Focus input field after response
  useEffect(() => {
    if (!isLoading && messages.length > 0) {
      inputRef.current?.focus();
    }
  }, [isLoading, messages.length]);

  // Reset document selector when documents change
  useEffect(() => {
    if (documents.length === 0) {
      setSelectedDocument(null);
      setShowDocumentSelector(true);
      setMessages([]);
      setCurrentConversationId(null);
    }
  }, [documents]);

  const loadConversationHistory = async (documentId: string) => {
    try {
      setIsLoadingHistory(true);

      // Get existing conversations for this document
      const conversations = await apiService.getDocumentConversations(
        documentId
      );

      if (conversations.length > 0) {
        // Load the most recent conversation
        const latestConversation = conversations[0];
        const conversationMessages = await apiService.getConversationMessages(
          latestConversation.id
        );

        // Convert database messages to ChatMessage format
        const chatMessages: ChatMessage[] = conversationMessages.map(
          (msg: any) => ({
            role: msg.role as "user" | "assistant",
            content: msg.content,
            timestamp: msg.timestamp,
            sources: msg.sources,
          })
        );

        setMessages(chatMessages);
        setCurrentConversationId(latestConversation.id);
        toast.success("Loaded previous conversation!");
      } else {
        // Create new conversation
        const newConversation = await apiService.createConversation(documentId);
        setCurrentConversationId(newConversation.conversation_id);
        setMessages([]);
      }
    } catch (error) {
      console.error("Error loading conversation history:", error);
      toast.error("Failed to load conversation history");
      // Create new conversation as fallback
      try {
        const newConversation = await apiService.createConversation(documentId);
        setCurrentConversationId(newConversation.conversation_id);
        setMessages([]);
      } catch (fallbackError) {
        console.error("Failed to create new conversation:", fallbackError);
      }
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const handleDocumentSelect = async (documentId: string) => {
    setSelectedDocument(documentId);
    setShowDocumentSelector(false);
    await loadConversationHistory(documentId);
  };

  const handleChangeDocument = () => {
    setSelectedDocument(null);
    setShowDocumentSelector(true);
    setMessages([]);
    setCurrentConversationId(null);
  };

  const saveMessageToDatabase = async (message: ChatMessage) => {
    if (!currentConversationId) return;

    try {
      await apiService.saveMessage(currentConversationId, {
        role: message.role,
        content: message.content,
        sources: message.sources,
      });
    } catch (error) {
      console.error("Failed to save message to database:", error);
      // Don't show error to user as this is background operation
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (
      !inputValue.trim() ||
      isLoading ||
      !selectedDocument ||
      !currentConversationId
    )
      return;

    const userMessage: ChatMessage = {
      role: "user",
      content: inputValue,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    // Save user message to database
    await saveMessageToDatabase(userMessage);

    const loadingToast = toast.loading("Processing your query...");

    try {
      // Prepare conversation history for the API
      const conversationHistory = messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
      }));

      const response = await apiService.queryKnowledgeBase({
        query: inputValue,
        conversation_history: conversationHistory,
        top_k: 5,
        document_filter: selectedDocument,
      });

      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: response.response,
        timestamp: response.timestamp,
        sources: response.sources,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Save assistant message to database
      await saveMessageToDatabase(assistantMessage);

      toast.success("Response received!", { id: loadingToast });
    } catch (error) {
      console.error("Query error:", error);
      toast.error("Failed to get response. Please try again.", {
        id: loadingToast,
      });

      // Add error message
      const errorMessage: ChatMessage = {
        role: "assistant",
        content:
          "Sorry, I encountered an error while processing your query. Please try again.",
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const getSelectedDocumentName = () => {
    const doc = documents.find((d) => d.document_id === selectedDocument);
    return doc ? doc.filename : "Unknown Document";
  };

  // Document Selection Screen
  if (showDocumentSelector) {
    return (
      <div className="flex flex-col h-full max-w-4xl mx-auto">
        <div className="bg-white border-b border-gray-200 p-4">
          <h2 className="text-xl font-semibold text-gray-900">
            Select Document to Chat With
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            Choose a document to start a focused conversation
          </p>
        </div>

        <div className="flex-1 overflow-y-auto py-4">
          {documents.length === 0 ? (
            <div className="text-center text-gray-500 mt-8">
              <div className="text-4xl mb-4">📄</div>
              <p className="text-lg font-medium mb-2">No documents available</p>
              <p className="text-sm">
                Upload some documents first to start chatting
              </p>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {documents.map((doc) => (
                <div
                  key={doc.document_id}
                  onClick={() => handleDocumentSelect(doc.document_id)}
                  className="bg-white border border-gray-200 rounded-lg p-4 cursor-pointer hover:border-blue-300 hover:shadow-md transition-all"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900 truncate">
                        {doc.filename}
                      </h3>
                      <p className="text-sm text-gray-500 mt-1">
                        {doc.chunks_count} chunks •{" "}
                        {Math.round(doc.file_size / 1024)}KB
                      </p>
                      <p className="text-xs text-gray-400 mt-1">
                        Uploaded:{" "}
                        {new Date(doc.upload_date).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="ml-2 text-blue-600">
                      <svg
                        className="w-5 h-5"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 5l7 7-7 7"
                        />
                      </svg>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              Chat with Knowledge Base
            </h2>
            <div className="flex items-center mt-1">
              <p className="text-sm text-gray-500">
                Currently chatting about:{" "}
                <span className="font-medium text-blue-600">
                  {getSelectedDocumentName()}
                </span>
              </p>
            </div>
          </div>
          <button
            onClick={handleChangeDocument}
            className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
          >
            Change Document
          </button>
        </div>
      </div>

      {/* Messages */}
      <div
        ref={messagesContainerRef}
        className="flex-1 overflow-y-auto p-4 space-y-4"
      >
        {isLoadingHistory ? (
          <div className="text-center text-gray-500 mt-8">
            <div role="status" className="mb-4">
              <svg
                aria-hidden="true"
                className="w-8 h-8 text-gray-200 animate-spin dark:text-gray-300 fill-blue-600"
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
            <p>Loading conversation history...</p>
          </div>
        ) : messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            <div className="text-4xl mb-4">💬</div>
            <p>
              Start a conversation about{" "}
              <strong>{getSelectedDocumentName()}</strong>
            </p>
            <p className="text-sm mt-2">
              Ask questions related to this specific document
            </p>
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.role === "user"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-100 text-gray-900"
                }`}
              >
                <div className="whitespace-pre-wrap">{message.content}</div>

                {message.sources && message.sources.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-gray-200">
                    <div className="text-xs text-gray-500 mb-1">Sources:</div>
                    <div className="text-xs">
                      {message.sources.map((source, idx) => (
                        <span
                          key={idx}
                          className="inline-block bg-gray-200 rounded px-2 py-1 mr-1 mb-1"
                        >
                          {source}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div
                  className={`text-xs mt-1 ${
                    message.role === "user" ? "text-blue-100" : "text-gray-500"
                  }`}
                >
                  {formatTimestamp(message.timestamp)}
                </div>
              </div>
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-900 max-w-xs lg:max-w-md px-4 py-2 rounded-lg">
              <div className="flex items-center space-x-2">
                <div role="status">
                  <svg
                    aria-hidden="true"
                    className="w-4 h-4 text-gray-200 animate-spin dark:text-gray-300 fill-blue-600"
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
                <span>Thinking...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="bg-white border-t border-gray-200 p-4">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={`Ask a question about ${getSelectedDocumentName()}...`}
            disabled={isLoading || isLoadingHistory}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || isLoading || isLoadingHistory}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;
