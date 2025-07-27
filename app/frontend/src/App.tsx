import { useState } from "react";
import { MessageSquare, FileText, Settings } from "lucide-react";
import { useTranslation } from "react-i18next";

import GroundingFileView from "@/components/ui/grounding-file-view";
import InternetSpeedIndicator from "@/components/ui/internet-speed-indicator";
import { IndexedDocuments } from "@/components/ui/indexed-documents";
import { ConversationInterface } from "@/components/ui/conversation-interface";
import { SettingsPage } from "@/components/ui/settings-page";
import { PDFUploader } from "@/components/documents/PDFUploader";
import { PendingJobs } from "@/components/documents/PendingJobs";
import { TabNavigation } from "@/components/ui/tab-navigation";

import useRealTime from "@/hooks/useRealtime";
import useAudioRecorder from "@/hooks/useAudioRecorder";
import useAudioPlayer from "@/hooks/useAudioPlayer";

import { GroundingFile, ToolResult } from "./types";

function App() {
    const [activeTab, setActiveTab] = useState("conversation");
    const [activeDocumentTab, setActiveDocumentTab] = useState("search");
    const [isRecording, setIsRecording] = useState(false);
    const [groundingFiles, setGroundingFiles] = useState<GroundingFile[]>([]);
    const [selectedFile, setSelectedFile] = useState<GroundingFile | null>(null);

    const { startSession, addUserAudio, inputAudioBufferClear } = useRealTime({
        onWebSocketOpen: () => console.log("WebSocket connection opened"),
        onWebSocketClose: () => console.log("WebSocket connection closed"),
        onWebSocketError: event => console.error("WebSocket error:", event),
        onReceivedError: message => console.error("error", message),
        onReceivedResponseAudioDelta: message => {
            isRecording && playAudio(message.delta);
        },
        onReceivedInputAudioBufferSpeechStarted: () => {
            stopAudioPlayer();
        },
        onReceivedExtensionMiddleTierToolResponse: message => {
            const result: ToolResult = JSON.parse(message.tool_result);

            const files: GroundingFile[] = result.sources.map(x => {
                return { id: x.chunk_id, name: x.title, content: x.chunk };
            });

            setGroundingFiles(prev => [...prev, ...files]);
        }
    });

    const { reset: resetAudioPlayer, play: playAudio, stop: stopAudioPlayer } = useAudioPlayer();
    const { start: startAudioRecording, stop: stopAudioRecording } = useAudioRecorder({ onAudioRecorded: addUserAudio });

    const onToggleListening = async () => {
        if (!isRecording) {
            startSession();
            await startAudioRecording();
            resetAudioPlayer();

            setIsRecording(true);
        } else {
            await stopAudioRecording();
            stopAudioPlayer();
            inputAudioBufferClear();

            setIsRecording(false);
        }
    };

    const { t } = useTranslation();

    const tabs = [
        { id: "conversation", label: t("tabs.conversation"), icon: <MessageSquare className="h-5 w-5" /> },
        { id: "documents", label: t("tabs.documents"), icon: <FileText className="h-5 w-5" /> },
        { id: "settings", label: t("tabs.settings"), icon: <Settings className="h-5 w-5" /> }
    ];

    return (
        <div className="flex h-screen bg-background text-foreground">
            {/* Sidebar */}
            <div className="hidden md:flex md:w-64 md:flex-col">
                <div className="flex flex-col flex-grow border-r border-border bg-card pt-5 pb-4 overflow-y-auto">
                    <div className="flex items-center flex-shrink-0 px-4">
                        <h1 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                            {t("app.title")}
                            <span className="block text-xs font-normal text-muted-foreground">By DestinPQ</span>
                        </h1>
                    </div>
                    <div className="mt-5 flex-grow flex flex-col">
                        <nav className="flex-1 px-2 space-y-1">
                            {tabs.map((tab) => (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={`group flex items-center px-2 py-3 text-sm font-medium rounded-md w-full ${
                                        activeTab === tab.id
                                            ? "bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300"
                                            : "text-muted-foreground hover:bg-muted hover:text-foreground"
                                    }`}
                                >
                                    <div className={`mr-3 ${
                                        activeTab === tab.id ? "text-purple-500 dark:text-purple-400" : "text-muted-foreground group-hover:text-foreground"
                                    }`}>
                                        {tab.icon}
                                    </div>
                                    {tab.label}
                                </button>
                            ))}
                        </nav>
                    </div>
                </div>
            </div>

            {/* Mobile header */}
            <div className="md:hidden bg-card border-b border-border p-4">
                <div className="flex items-center justify-between">
                    <h1 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                        {t("app.title")}
                        <span className="block text-xs font-normal text-muted-foreground">By DestinPQ</span>
                    </h1>
                    <InternetSpeedIndicator />
                </div>
                <div className="flex mt-3 space-x-2 overflow-x-auto">
                    {tabs.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                                activeTab === tab.id
                                    ? "bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300"
                                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                            }`}
                        >
                            <div className="mr-2">{tab.icon}</div>
                            {tab.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Main content */}
            <div className="flex flex-col flex-1 overflow-hidden">
                <div className="hidden md:flex md:items-center md:justify-between md:px-6 md:py-3 md:border-b md:border-border">
                    <h2 className="text-xl font-semibold text-foreground">
                        {tabs.find(tab => tab.id === activeTab)?.label}
                    </h2>
                    <InternetSpeedIndicator />
                </div>
                
                <main className="flex-1 relative overflow-y-auto focus:outline-none">
                    <div className="py-6 px-4 sm:px-6 lg:px-8">
                        {activeTab === "conversation" && (
                            <div className="max-w-3xl mx-auto">
                                <ConversationInterface 
                                    isRecording={isRecording}
                                    onToggleListening={onToggleListening}
                                    groundingFiles={groundingFiles}
                                    onFileSelected={setSelectedFile}
                                />
                            </div>
                        )}
                        
                        {activeTab === "documents" && (
                            <div className="max-w-4xl mx-auto space-y-6">
                                <TabNavigation
                                    activeTab={activeDocumentTab}
                                    onTabChange={setActiveDocumentTab}
                                    tabs={[
                                        { id: "search", label: "Search Documents" },
                                        { id: "jobs", label: "Upload & Process" },
                                    ]}
                                    className="mb-4"
                                />

                                {activeDocumentTab === "search" && (
                                    <div className="bg-card rounded-lg shadow p-6">
                                        <IndexedDocuments />
                                    </div>
                                )}

                                {activeDocumentTab === "jobs" && (
                                    <div className="space-y-6">
                                        <div className="bg-card rounded-lg shadow p-6">
                                            <h3 className="text-lg font-medium mb-4">Upload Document</h3>
                                            <PDFUploader />
                                        </div>
                                        <div className="bg-card rounded-lg shadow p-6">
                                            <h3 className="text-lg font-medium mb-4">Processing Jobs</h3>
                                            <PendingJobs />
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                        
                        {activeTab === "settings" && (
                            <div className="max-w-3xl mx-auto">
                                <SettingsPage />
                            </div>
                        )}
                    </div>
                </main>
                
                <footer className="hidden md:block bg-card border-t border-border p-4 text-center text-sm text-muted-foreground">
                    <p>{t("app.footer")}</p>
                </footer>
            </div>

            <GroundingFileView groundingFile={selectedFile} onClosed={() => setSelectedFile(null)} />
        </div>
    );
}

export default App;
