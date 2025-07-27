import { Mic, MicOff } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "./button";
import StatusMessage from "./status-message";
import { GroundingFiles } from "./grounding-files";
import { GroundingFile } from "@/types";

// interface Message {
//   id: string;
//   content: string;
//   isUser: boolean;
//   timestamp: Date;
// }

interface ConversationInterfaceProps {
  isRecording: boolean;
  onToggleListening: () => Promise<void>;
  groundingFiles: GroundingFile[];
  onFileSelected: (file: GroundingFile) => void;
}

export function ConversationInterface({
  isRecording,
  onToggleListening,
  groundingFiles,
  onFileSelected,
}: ConversationInterfaceProps) {
  const { t } = useTranslation();
  // const [messages, setMessages] = useState<Message[]>([
  //   {
  //     id: "welcome",
  //     content: "Welcome! How can I help you today?",
  //     isUser: false,
  //     timestamp: new Date(),
  //   },
  // ]);

  // This would be connected to the actual conversation in a real implementation
  // For now, it's just a placeholder to demonstrate the UI

  return (
    <div className="flex flex-col h-full">
      {/* Chat messages area */}
      {/* <div className="flex-1 overflow-y-auto mb-4 p-4 bg-card rounded-lg shadow">
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.isUser ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`flex items-start max-w-[80%] ${
                  message.isUser ? "flex-row-reverse" : "flex-row"
                }`}
              >
                <div
                  className={`flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center ${
                    message.isUser ? "bg-primary/10 ml-2" : "bg-muted mr-2"
                  }`}
                >
                  {message.isUser ? (
                    <User className="h-5 w-5 text-primary" />
                  ) : (
                    <Bot className="h-5 w-5 text-muted-foreground" />
                  )}
                </div>
                <div
                  className={`p-3 rounded-lg ${
                    message.isUser
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted text-muted-foreground"
                  }`}
                >
                  <p className="text-sm">{message.content}</p>
                  <p className="text-xs mt-1 opacity-70">
                    {message.timestamp.toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div> */}

      {/* Recording controls */}
      <div className="flex flex-col items-center justify-center mb-4 sm:mb-6 px-2 sm:px-0">
        <Button
          onClick={onToggleListening}
          className={`h-12 sm:h-14 w-full max-w-xs sm:max-w-sm text-base sm:text-lg ${
            isRecording 
              ? "bg-destructive hover:bg-destructive/90 text-destructive-foreground" 
              : "bg-purple-600 hover:bg-purple-700 text-white dark:bg-purple-700 dark:hover:bg-purple-800"
          }`}
          aria-label={isRecording ? t("app.stopRecording") : t("app.startRecording")}
        >
          {isRecording ? (
            <>
              <MicOff className="mr-2 h-5 w-5" />
              {t("app.stopConversation")}
            </>
          ) : (
            <>
              <Mic className="mr-2 h-5 w-5" />
              {t("app.startRecording")}
            </>
          )}
        </Button>
        
        <StatusMessage isRecording={isRecording} />
      </div>

      {/* Grounding files */}
      {groundingFiles.length > 0 && (
        <div className="mt-2 sm:mt-4 w-full overflow-x-hidden">
          <GroundingFiles files={groundingFiles} onSelected={onFileSelected} />
        </div>
      )}
    </div>
  );
} 