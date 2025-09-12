import { useState } from "react";
import { AlertTriangle } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "./button";

interface ClearIndexButtonProps {
  onSuccess?: () => void;
}

export function ClearIndexButton({ onSuccess }: ClearIndexButtonProps) {
  const [isClearing, setIsClearing] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [result, setResult] = useState<{
    success: boolean;
    message: string;
    deleted_count?: number;
    total_count?: number;
  } | null>(null);
  
  const { t } = useTranslation();

  const handleClearIndex = async () => {
    setIsClearing(true);
    setResult(null);
    
    try {
      const response = await fetch("/api/index/clear", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ confirm: true }),
      });
      
      const data = await response.json();
      setResult(data);
      
      if (data.success && onSuccess) {
        onSuccess();
      }
    } catch (err) {
      setResult({
        success: false,
        message: err instanceof Error ? err.message : "Failed to clear index",
      });
      console.error("Error clearing index:", err);
    } finally {
      setIsClearing(false);
      setShowConfirmation(false);
    }
  };

  return (
    <div className="mt-6">
      {!showConfirmation ? (
        <Button
          variant="destructive"
          onClick={() => setShowConfirmation(true)}
          className="w-full"
        >
          <AlertTriangle className="h-5 w-5 mr-2" />
          {t("index.clearAll")}
        </Button>
      ) : (
        <div className="border border-red-200 bg-red-50 rounded-md p-4">
          <div className="flex items-center mb-4">
            <AlertTriangle className="h-6 w-6 text-red-500 mr-2" />
            <h3 className="text-lg font-medium text-red-800">
              {t("index.confirmClearTitle")}
            </h3>
          </div>
          
          <p className="text-red-700 mb-4">
            {t("index.confirmClearMessage")}
          </p>
          
          <div className="flex space-x-3">
            <Button
              variant="destructive"
              onClick={handleClearIndex}
              disabled={isClearing}
              className="flex-1"
            >
              {isClearing ? (
                <>
                  <div className="animate-spin h-4 w-4 border-2 border-white rounded-full border-t-transparent mr-2"></div>
                  {t("index.clearing")}
                </>
              ) : (
                t("index.confirmClear")
              )}
            </Button>
            
            <Button
              variant="outline"
              onClick={() => setShowConfirmation(false)}
              disabled={isClearing}
              className="flex-1"
            >
              {t("common.cancel")}
            </Button>
          </div>
        </div>
      )}

      {result && (
        <div className={`mt-4 p-3 rounded-md ${
          result.success ? "bg-green-50 text-green-800" : "bg-red-50 text-red-800"
        }`}>
          <p className="font-medium">{result.message}</p>
          {result.success && result.deleted_count !== undefined && (
            <p className="text-sm mt-1">
              {t("index.deletedCount", { count: result.deleted_count })}
            </p>
          )}
        </div>
      )}
    </div>
  );
} 