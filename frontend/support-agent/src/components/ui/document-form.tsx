import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "./button";
import { Card } from "./card";

interface DocumentFormProps {
  onDocumentAdded: () => void;
}

export function DocumentForm({ onDocumentAdded }: DocumentFormProps) {
  const [title, setTitle] = useState("");
  const [fact, setFact] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { t } = useTranslation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!title.trim() || !fact.trim()) {
      setError(t("documentForm.fieldsRequired"));
      return;
    }
    
    setIsSubmitting(true);
    setError(null);
    
    try {
      const response = await fetch("/api/documents", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ title, fact }),
      });
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      
      // Clear the form
      setTitle("");
      setFact("");
      
      // Notify parent component
      onDocumentAdded();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create document");
      console.error("Error creating document:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card className="p-4 mb-6">
      <h2 className="text-xl font-semibold mb-4">{t("documentForm.title")}</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
            {t("documentForm.titleLabel")}
          </label>
          <input
            id="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            placeholder={t("documentForm.titlePlaceholder")}
            disabled={isSubmitting}
          />
        </div>
        
        <div className="mb-4">
          <label htmlFor="fact" className="block text-sm font-medium text-gray-700 mb-1">
            {t("documentForm.factLabel")}
          </label>
          <textarea
            id="fact"
            value={fact}
            onChange={(e) => setFact(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 min-h-[100px]"
            placeholder={t("documentForm.factPlaceholder")}
            disabled={isSubmitting}
          />
        </div>
        
        {error && (
          <div className="mb-4 text-red-500 text-sm">{error}</div>
        )}
        
        <Button
          type="submit"
          className="bg-purple-500 hover:bg-purple-600"
          disabled={isSubmitting}
        >
          {isSubmitting ? t("documentForm.submitting") : t("documentForm.submit")}
        </Button>
      </form>
    </Card>
  );
} 