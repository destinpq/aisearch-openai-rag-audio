import { useState, useEffect } from "react";
import { MessageSquare, FileText, Settings, Menu, X, LogOut, User, History } from "lucide-react";
import { useTranslation } from "react-i18next";

import { Button } from "@/components/ui/button";
import GroundingFileView from "@/components/ui/grounding-file-view";
import InternetSpeedIndicator from "@/components/ui/internet-speed-indicator";
import { IndexedDocuments } from "@/components/ui/indexed-documents";
import { ConversationInterface } from "@/components/ui/conversation-interface";
import { SettingsPage } from "@/components/ui/settings-page";
import { PDFUploader } from "@/components/documents/PDFUploader";
import { PendingJobs } from "@/components/documents/PendingJobs";
import { TabNavigation } from "@/components/ui/tab-navigation";
import { ConversationHistory } from "@/components/ConversationHistory";
import { LandingPage } from "@/components/LandingPage";
import { Auth } from "@/components/Auth";

import useRealTime from "@/hooks/useRealtime";
import useAudioRecorder from "@/hooks/useAudioRecorder";
import useAudioPlayer from "@/hooks/useAudioPlayer";

import { GroundingFile, ToolResult } from "./types";

type AppView = "landing" | "auth" | "app";

function App() {
    const [currentView, setCurrentView] = useState<AppView>("landing");
    const [currentUser, setCurrentUser] = useState<any>(null);
    const [activeTab, setActiveTab] = useState("conversation");
    const [activeDocumentTab, setActiveDocumentTab] = useState("search");
    const [isRecording, setIsRecording] = useState(false);
    const [groundingFiles, setGroundingFiles] = useState<GroundingFile[]>([]);
    const [selectedFile, setSelectedFile] = useState<GroundingFile | null>(null);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

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
                return {
                    id: x.chunk_id,
                    name: x.title,
                    content: x.chunk,
                    location: x.location
                };
            });

            setGroundingFiles(prev => [...prev, ...files]);
        }
    });

    const { reset: resetAudioPlayer, play: playAudio, stop: stopAudioPlayer } = useAudioPlayer();
    const { start: startAudioRecording, stop: stopAudioRecording } = useAudioRecorder({ onAudioRecorded: addUserAudio });

    // Authentication handlers
    const handleNavigateToApp = () => {
        if (currentUser) {
            setCurrentView("app");
        } else {
            setCurrentView("auth");
        }
    };

    const handleAuthSuccess = (user: any) => {
        setCurrentUser(user);
        setCurrentView("app");
    };

    const handleLogout = async () => {
        try {
            await fetch("/api/auth/logout", { method: "POST" });
            setCurrentUser(null);
            setCurrentView("landing");
            setActiveTab("conversation");
            setGroundingFiles([]);
            setSelectedFile(null);
        } catch (error) {
            console.error("Logout failed:", error);
        }
    };

    // Check for existing session on app load
    useEffect(() => {
        const checkAuth = async () => {
            try {
                const response = await fetch("/api/auth/me");
                if (response.ok) {
                    const data = await response.json();
                    if (data.user) {
                        setCurrentUser(data.user);
                        setCurrentView("app");
                        return;
                    }
                }
            } catch (error) {
                console.error("Auth check failed:", error);
            }
            // If no valid session, stay on landing page
        };

        checkAuth();
    }, []);

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

    // Close mobile menu when changing tabs
    useEffect(() => {
        setMobileMenuOpen(false);
    }, [activeTab]);

    const { t } = useTranslation();

    const tabs = [
        { id: "conversation", label: t("tabs.conversation"), icon: <MessageSquare className="h-5 w-5" /> },
        { id: "documents", label: t("tabs.documents"), icon: <FileText className="h-5 w-5" /> },
        { id: "history", label: "History", icon: <History className="h-5 w-5" /> },
        { id: "settings", label: t("tabs.settings"), icon: <Settings className="h-5 w-5" /> }
    ];

    // Render different views based on current state
    if (currentView === "landing") {
        return <LandingPage onNavigateToApp={handleNavigateToApp} />;
    }

    if (currentView === "auth") {
        return <Auth onAuthSuccess={handleAuthSuccess} />;
    }

    // Main app view
    return (
        <div className="flex h-screen bg-background text-foreground">
            {/* Desktop Sidebar */}
            <div className="hidden md:flex md:w-64 md:flex-col">
                <div className="flex flex-grow flex-col overflow-y-auto border-r border-border bg-card pb-4 pt-5">
                    <div className="flex flex-shrink-0 items-center px-4">
                        <h1 className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-xl font-bold text-transparent">
                            {t("app.title")}
                            <span className="block text-xs font-normal text-muted-foreground">By DestinPQ</span>
                        </h1>
                    </div>

                    {/* User Profile Section */}
                    <div className="border-b border-border px-4 py-3">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-r from-blue-500 to-purple-500">
                                    <User className="h-4 w-4 text-white" />
                                </div>
                                <div className="min-w-0 flex-1">
                                    <p className="truncate text-sm font-medium text-foreground">
                                        {currentUser?.first_name && currentUser?.last_name
                                            ? `${currentUser.first_name} ${currentUser.last_name}`
                                            : currentUser?.username || "User"}
                                    </p>
                                    <p className="truncate text-xs text-muted-foreground">{currentUser?.email}</p>
                                </div>
                            </div>
                            <Button variant="ghost" size="sm" onClick={handleLogout} className="text-muted-foreground hover:text-foreground">
                                <LogOut className="h-4 w-4" />
                            </Button>
                        </div>
                    </div>
                    <div className="mt-5 flex flex-grow flex-col">
                        <nav className="flex-1 space-y-1 px-2">
                            {tabs.map(tab => (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={`group flex w-full items-center rounded-md px-2 py-3 text-sm font-medium ${
                                        activeTab === tab.id
                                            ? "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300"
                                            : "text-muted-foreground hover:bg-muted hover:text-foreground"
                                    }`}
                                >
                                    <div
                                        className={`mr-3 ${
                                            activeTab === tab.id ? "text-purple-500 dark:text-purple-400" : "text-muted-foreground group-hover:text-foreground"
                                        }`}
                                    >
                                        {tab.icon}
                                    </div>
                                    {tab.label}
                                </button>
                            ))}
                        </nav>
                    </div>
                </div>
            </div>

            {/* Mobile Sidebar (Drawer) */}
            <div className={`fixed inset-0 z-40 md:hidden ${mobileMenuOpen ? "block" : "hidden"}`}>
                {/* Backdrop */}
                <div className="fixed inset-0 bg-black/50 transition-opacity" onClick={() => setMobileMenuOpen(false)} aria-hidden="true"></div>

                {/* Drawer panel */}
                <div className="fixed inset-y-0 left-0 w-full max-w-xs transform bg-card shadow-lg transition-transform duration-300 ease-in-out">
                    <div className="flex h-16 items-center justify-between border-b border-border px-4">
                        <h1 className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-xl font-bold text-transparent">{t("app.title")}</h1>
                        <button onClick={() => setMobileMenuOpen(false)} className="rounded-md text-muted-foreground hover:text-foreground focus:outline-none">
                            <X className="h-6 w-6" />
                        </button>
                    </div>
                    <div className="h-full overflow-y-auto px-2 py-3">
                        <nav className="space-y-1">
                            {tabs.map(tab => (
                                <button
                                    key={tab.id}
                                    onClick={() => {
                                        setActiveTab(tab.id);
                                        setMobileMenuOpen(false);
                                    }}
                                    className={`group flex w-full items-center rounded-md px-3 py-4 text-base font-medium ${
                                        activeTab === tab.id
                                            ? "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300"
                                            : "text-muted-foreground hover:bg-muted hover:text-foreground"
                                    }`}
                                >
                                    <div
                                        className={`mr-4 ${
                                            activeTab === tab.id ? "text-purple-500 dark:text-purple-400" : "text-muted-foreground group-hover:text-foreground"
                                        }`}
                                    >
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
            <div className="border-b border-border bg-card p-4 md:hidden">
                <div className="flex items-center justify-between">
                    <button onClick={() => setMobileMenuOpen(true)} className="-ml-2 rounded-md p-2 text-muted-foreground hover:bg-muted hover:text-foreground">
                        <Menu className="h-6 w-6" />
                    </button>
                    <h1 className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-lg font-bold text-transparent">
                        {tabs.find(tab => tab.id === activeTab)?.label}
                    </h1>
                    <InternetSpeedIndicator />
                </div>
            </div>

            {/* Main content */}
            <div className="flex flex-1 flex-col overflow-hidden">
                <div className="hidden md:flex md:items-center md:justify-between md:border-b md:border-border md:px-6 md:py-3">
                    <h2 className="text-xl font-semibold text-foreground">{tabs.find(tab => tab.id === activeTab)?.label}</h2>
                    <InternetSpeedIndicator />
                </div>

                <main className="relative flex-1 overflow-y-auto focus:outline-none">
                    <div className="px-3 py-4 sm:px-6 sm:py-6 lg:px-8">
                        {activeTab === "conversation" && (
                            <div className="mx-auto max-w-3xl">
                                <ConversationInterface
                                    isRecording={isRecording}
                                    onToggleListening={onToggleListening}
                                    groundingFiles={groundingFiles}
                                    onFileSelected={setSelectedFile}
                                />
                            </div>
                        )}

                        {activeTab === "documents" && (
                            <div className="mx-auto max-w-4xl space-y-4 sm:space-y-6">
                                <TabNavigation
                                    activeTab={activeDocumentTab}
                                    onTabChange={setActiveDocumentTab}
                                    tabs={[
                                        { id: "search", label: "Search Documents" },
                                        { id: "jobs", label: "Upload & Process" }
                                    ]}
                                    className="mb-4"
                                />

                                {activeDocumentTab === "search" && (
                                    <div className="rounded-lg bg-card p-4 shadow sm:p-6">
                                        <IndexedDocuments />
                                    </div>
                                )}

                                {activeDocumentTab === "jobs" && (
                                    <div className="space-y-4 sm:space-y-6">
                                        <div className="rounded-lg bg-card p-4 shadow sm:p-6">
                                            <h3 className="mb-4 text-lg font-medium">Upload Document</h3>
                                            <PDFUploader />
                                        </div>
                                        <div className="rounded-lg bg-card p-4 shadow sm:p-6">
                                            <h3 className="mb-4 text-lg font-medium">Processing Jobs</h3>
                                            <PendingJobs />
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}

                        {activeTab === "history" && (
                            <div className="mx-auto max-w-4xl">
                                <ConversationHistory
                                    onConversationSelect={conversationId => {
                                        console.log("Selected conversation:", conversationId);
                                        // TODO: Implement conversation loading
                                    }}
                                />
                            </div>
                        )}

                        {activeTab === "settings" && (
                            <div className="mx-auto max-w-3xl">
                                <SettingsPage />
                            </div>
                        )}
                    </div>
                </main>

                <footer className="hidden border-t border-border bg-card p-4 text-center text-sm text-muted-foreground md:block">
                    <p>{t("app.footer")}</p>
                </footer>
            </div>

            <GroundingFileView groundingFile={selectedFile} onClosed={() => setSelectedFile(null)} />
        </div>
    );
}

export default App;
