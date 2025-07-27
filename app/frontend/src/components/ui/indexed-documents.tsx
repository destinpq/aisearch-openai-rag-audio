import { useState, useEffect } from "react";
import { Search, Trash2, Plus, X } from "lucide-react";
import { useTranslation } from "react-i18next";
import { IndexedDocument } from "@/types";
import { Button } from "./button";
import { Card } from "./card";
import { DocumentForm } from "./document-form";

export function IndexedDocuments() {
  const [documents, setDocuments] = useState<IndexedDocument[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const { t } = useTranslation();

  // Remove the initial document fetch on component mount
  // We'll only load documents when the user searches

  const handleDelete = async (id: string) => {
    if (!confirm(t("documents.confirmDelete"))) return;
    
    try {
      const response = await fetch(`/api/documents/${id}`, {
        method: "DELETE",
      });
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      
      // Remove the deleted document from the list
      setDocuments((prev) => prev.filter((doc) => doc.id !== id));
    } catch (err) {
      console.error("Error deleting document:", err);
      alert(t("documents.deleteError"));
    }
  };

  const handleDocumentAdded = () => {
    // After adding a document, search for it if there's a search term
    if (searchTerm.trim()) {
      searchDocuments(searchTerm);
    }
    setShowForm(false);
  };

  // Search documents using Azure AI Search
  const searchDocuments = async (query: string) => {
    setIsSearching(true);
    setError(null);
    
    try {
      if (!query.trim()) {
        // If search is empty, clear results instead of fetching all documents
        setDocuments([]);
        setIsSearching(false);
        return;
      }
      
      const response = await fetch(`/api/search?query=${encodeURIComponent(query)}`);
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      
      const data = await response.json();
      setDocuments(data.results || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to search documents");
      console.error("Error searching documents:", err);
    } finally {
      setIsSearching(false);
    }
  };

  // Debounce search to avoid too many requests
  useEffect(() => {
    const timer = setTimeout(() => {
      searchDocuments(searchTerm);
    }, 500);
    
    return () => clearTimeout(timer);
  }, [searchTerm]);

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return new Intl.DateTimeFormat("en-US", {
        dateStyle: "medium",
        timeStyle: "short",
      }).format(date);
    } catch (e) {
      return dateString;
    }
  };

  if (loading) {
    return <div className="text-center py-8">{t("documents.loading")}</div>;
  }

  if (error) {
    return (
      <div className="text-center py-8 text-red-500">
        {t("documents.error")}: {error}
        <Button
          className="mt-4 bg-purple-500 hover:bg-purple-600"
          onClick={() => searchDocuments(searchTerm)}
        >
          {t("documents.retry")}
        </Button>
      </div>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto">
      {showForm ? (
        <>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">{t("documents.addNew")}</h2>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setShowForm(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              <X className="h-5 w-5" />
            </Button>
          </div>
          <DocumentForm onDocumentAdded={handleDocumentAdded} />
        </>
      ) : (
        <div className="flex justify-between items-center mb-6">
          <div className="relative flex-grow mr-4">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder={t("documents.search")}
              className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              autoFocus
            />
            {isSearching && (
              <div className="absolute inset-y-0 right-3 flex items-center">
                <div className="animate-spin h-4 w-4 border-2 border-purple-500 rounded-full border-t-transparent"></div>
              </div>
            )}
          </div>
          <Button
            onClick={() => setShowForm(true)}
            className="bg-purple-500 hover:bg-purple-600"
          >
            <Plus className="h-5 w-5 mr-1" />
            {t("documents.add")}
          </Button>
        </div>
      )}

      {!showForm && documents.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          {searchTerm
            ? t("documents.noSearchResults")
            : t("documents.searchToViewDocuments")}
        </div>
      ) : (
        !showForm && (
          <div className="space-y-4">
            {documents.map((doc) => (
              <Card key={doc.id} className="p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">
                      {doc.title}
                    </h3>
                    <p className="text-sm text-gray-500 mb-2">
                      {formatDate(doc.created_at)}
                    </p>
                    <p className="text-gray-700">{doc.fact}</p>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleDelete(doc.id)}
                    aria-label={t("documents.delete")}
                    className="text-red-500 hover:text-red-700 hover:bg-red-50"
                  >
                    <Trash2 className="h-5 w-5" />
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )
      )}
    </div>
  );
} 