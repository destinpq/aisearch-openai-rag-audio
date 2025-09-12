import { useState } from "react";
import { Routes, Route, Navigate, Link } from "react-router-dom";
import { ConfigProvider, theme } from "antd";
import { Mic, MicOff, UploadIcon, Search, LogOut, Phone } from "lucide-react";
import { useTranslation } from "react-i18next";

import { Button } from "@/components/ui/button";
import { GroundingFiles } from "@/components/ui/grounding-files";
import GroundingFileView from "@/components/ui/grounding-file-view";
import StatusMessage from "@/components/ui/status-message";

import useRealTime from "@/hooks/useRealtime";
import useAudioRecorder from "@/hooks/useAudioRecorder";
import useAudioPlayer from "@/hooks/useAudioPlayer";

import { GroundingFile, ToolResult } from "./types";
import { useAuth } from "./contexts/AuthContext";
import Landing from "./components/Landing";
import LoginAntd from "./components/LoginAntd";
import Register from "./components/Register";
import Upload from "./components/Upload";
import Analyze from "./components/Analyze";
import CallInterface from "./components/CallInterface";
import EnhancedPDFProcessor from "./components/EnhancedPDFProcessor";

import logo from "./assets/logo.svg";

function MainApp() {
    const [isRecording, setIsRecording] = useState(false);
    const [groundingFiles, setGroundingFiles] = useState<GroundingFile[]>([]);
    const [selectedFile, setSelectedFile] = useState<GroundingFile | null>(null);
    const [audioError, setAudioError] = useState<string | null>(null);
    const [voiceSearchMode, setVoiceSearchMode] = useState<"guarded" | "unguarded">("guarded");
    const { logout } = useAuth();

    const { startSession, addUserAudio, inputAudioBufferClear } = useRealTime({
        searchMode: voiceSearchMode,
        onReceivedResponseDone: () => {
            console.log("Response completed");
        },
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
                // Find the most relevant line in the content
                const lines = x.chunk.split("\n");
                let highlightLine = 1;
                let highlightText = "";

                // Look for lines that might contain key information
                // Try to find lines with substantive content (not just short phrases)
                for (let i = 0; i < lines.length; i++) {
                    const line = lines[i].trim();
                    if (line.length > 20 && !line.startsWith("#") && !line.startsWith("-")) {
                        highlightLine = i + 1;
                        highlightText = line.substring(0, 50); // First 50 chars as highlight text
                        break;
                    }
                }

                return {
                    id: x.chunk_id,
                    name: x.title,
                    content: x.chunk,
                    highlightLine: highlightLine,
                    highlightText: highlightText,
                    searchMode: result.search_mode // Add search mode to the file
                };
            });

            setGroundingFiles(prev => [...prev, ...files]);
        }
    });

    const { reset: resetAudioPlayer, play: playAudio, stop: stopAudioPlayer } = useAudioPlayer();
    const { start: startAudioRecording, stop: stopAudioRecording } = useAudioRecorder({ onAudioRecorded: addUserAudio });

    const onToggleListening = async () => {
        if (!isRecording) {
            try {
                setAudioError(null); // Clear any previous errors
                startSession();
                await startAudioRecording();
                resetAudioPlayer();
                setIsRecording(true);
            } catch (error) {
                console.error("Failed to start recording:", error);
                setAudioError(error instanceof Error ? error.message : "Failed to access microphone");
                setIsRecording(false);
            }
        } else {
            try {
                await stopAudioRecording();
                stopAudioPlayer();
                inputAudioBufferClear();
                setIsRecording(false);
                setAudioError(null);
            } catch (error) {
                console.error("Failed to stop recording:", error);
                setIsRecording(false);
            }
        }
    };

    const { t } = useTranslation();

    return (
        <div className="flex min-h-screen flex-col bg-gray-100 text-gray-900">
            <header className="flex items-center justify-between bg-white p-4 shadow">
                <div className="flex items-center space-x-4">
                    <img src={logo} alt="Azure logo" className="h-8 w-8" />
                    <span className="font-bold">VoiceRAG</span>
                </div>
                <nav className="flex space-x-4">
                    <Link to="/upload">
                        <Button variant="outline" size="sm">
                            <UploadIcon className="mr-2 h-4 w-4" />
                            Upload
                        </Button>
                    </Link>
                    <Link to="/analyze">
                        <Button variant="outline" size="sm">
                            <Search className="mr-2 h-4 w-4" />
                            Analyze
                        </Button>
                    </Link>
                    <Link to="/call">
                        <Button variant="outline" size="sm">
                            <Phone className="mr-2 h-4 w-4" />
                            Call
                        </Button>
                    </Link>
                    <Button variant="outline" size="sm" onClick={logout}>
                        <LogOut className="mr-2 h-4 w-4" />
                        Logout
                    </Button>
                </nav>
            </header>
            <main className="flex flex-grow flex-col items-center justify-center">
                <h1 className="mb-8 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-4xl font-bold text-transparent md:text-7xl">
                    {t("app.title")}
                </h1>

                {/* Simple iPhone-style Toggle */}
                <div className="mb-6 rounded-lg bg-white p-6 shadow-lg">
                    <div className="mb-4 text-center">
                        <h3 className="text-lg font-semibold text-gray-900">Search Mode</h3>
                    </div>

                    {/* Clean iOS-style Toggle */}
                    <div className="flex items-center justify-center space-x-4">
                        <span className={`text-sm font-medium ${voiceSearchMode === "guarded" ? "text-blue-600" : "text-gray-500"}`}>Your PDFs</span>
                        <button
                            onClick={() => setVoiceSearchMode(voiceSearchMode === "guarded" ? "unguarded" : "guarded")}
                            className={`relative h-8 w-14 rounded-full transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                                voiceSearchMode === "guarded" ? "bg-blue-600" : "bg-gray-300"
                            }`}
                        >
                            <div
                                className={`absolute top-1 h-6 w-6 rounded-full bg-white shadow-md transition-transform duration-200 ease-in-out ${
                                    voiceSearchMode === "guarded" ? "translate-x-1" : "translate-x-7"
                                }`}
                            />
                        </button>
                        <span className={`text-sm font-medium ${voiceSearchMode === "unguarded" ? "text-blue-600" : "text-gray-500"}`}>Internet</span>
                    </div>

                    {/* Simple status */}
                    <div className="mt-4 text-center">
                        <span className="text-sm text-gray-600">
                            {voiceSearchMode === "guarded" ? "🔒 Searching your documents only" : "🌐 Searching all documents"}
                        </span>
                    </div>
                </div>

                <div className="mb-4 flex flex-col items-center justify-center">
                    {audioError && (
                        <div className="mb-4 max-w-md rounded-lg border border-red-400 bg-red-100 px-4 py-3 text-red-700">
                            <p className="text-sm">
                                <strong>Microphone Error:</strong> {audioError}
                            </p>
                            <p className="mt-1 text-xs">Please check your browser settings and allow microphone access.</p>
                            <button onClick={() => setAudioError(null)} className="mt-2 text-xs underline hover:no-underline">
                                Try Again
                            </button>
                        </div>
                    )}
                    <Button
                        onClick={onToggleListening}
                        className={`h-12 w-60 ${isRecording ? "bg-red-600 hover:bg-red-700" : "bg-purple-500 hover:bg-purple-600"}`}
                        aria-label={isRecording ? t("app.stopRecording") : t("app.startRecording")}
                        disabled={!!audioError && !isRecording}
                    >
                        {isRecording ? (
                            <>
                                <MicOff className="mr-2 h-4 w-4" />
                                {t("app.stopConversation")}
                            </>
                        ) : (
                            <>
                                <Mic className="mr-2 h-6 w-6" />
                                {audioError ? "Fix Microphone Issues" : `Start Conversation (${voiceSearchMode})`}
                            </>
                        )}
                    </Button>
                    <StatusMessage isRecording={isRecording} />
                </div>
                <GroundingFiles files={groundingFiles} onSelected={setSelectedFile} />
            </main>

            <footer className="py-4 text-center">
                <p>{t("app.footer")}</p>
            </footer>

            <GroundingFileView groundingFile={selectedFile} onClosed={() => setSelectedFile(null)} />
        </div>
    );
}

function App() {
    const { isAuthenticated } = useAuth();

    const themeConfig = {
        algorithm: theme.defaultAlgorithm,
        token: {
            colorPrimary: "#6366f1",
            colorSuccess: "#10b981",
            colorWarning: "#f59e0b",
            colorError: "#ef4444",
            borderRadius: 8
        }
    };

    return (
        <ConfigProvider theme={themeConfig}>
            <Routes>
                <Route path="/" element={<Landing />} />
                <Route path="/login" element={<LoginAntd />} />
                <Route path="/landing" element={<Landing />} />
                <Route path="/register" element={<Register />} />
                <Route path="/upload" element={isAuthenticated ? <Upload /> : <Navigate to="/login" />} />
                <Route path="/analyze" element={isAuthenticated ? <Analyze /> : <Navigate to="/login" />} />
                <Route path="/enhanced-pdf" element={isAuthenticated ? <EnhancedPDFProcessor /> : <Navigate to="/login" />} />
                <Route path="/call" element={isAuthenticated ? <CallInterface /> : <Navigate to="/login" />} />
                <Route path="/app" element={isAuthenticated ? <MainApp /> : <Navigate to="/login" />} />
            </Routes>
        </ConfigProvider>
    );
}

export default App;
