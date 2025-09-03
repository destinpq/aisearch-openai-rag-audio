import { useState } from "react";
import { Routes, Route, Navigate, Link } from "react-router-dom";
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
import Login from "./components/Login";
import Register from "./components/Register";
import Upload from "./components/Upload";
import Analyze from "./components/Analyze";
import CallInterface from "./components/CallInterface";

import logo from "./assets/logo.svg";

function MainApp() {
    const [isRecording, setIsRecording] = useState(false);
    const [groundingFiles, setGroundingFiles] = useState<GroundingFile[]>([]);
    const [selectedFile, setSelectedFile] = useState<GroundingFile | null>(null);
    const [audioError, setAudioError] = useState<string | null>(null);
    const [voiceSearchMode, setVoiceSearchMode] = useState<"guarded" | "unguarded">("guarded");
    const { logout } = useAuth();

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

                {/* MASSIVE SLIDING TOGGLE BUTTON */}
                <div className="mb-6 rounded-3xl border-4 border-purple-500 bg-white p-8 shadow-2xl">
                    <div className="mb-6 text-center">
                        <h3 className="text-2xl font-bold text-gray-900">🎛️ Voice Chat Search Mode</h3>
                        <p className="text-lg text-gray-600">Choose which documents to search during voice conversations</p>
                    </div>

                    {/* BIG SLIDING BUTTON */}
                    <div className="flex justify-center">
                        <div className="relative">
                            <button
                                onClick={() => setVoiceSearchMode(voiceSearchMode === "guarded" ? "unguarded" : "guarded")}
                                className={`relative h-24 w-96 rounded-full border-4 shadow-xl transition-all duration-300 ease-in-out ${
                                    voiceSearchMode === "guarded" ? "border-red-600 bg-red-400" : "border-teal-600 bg-teal-400"
                                }`}
                            >
                                {/* Sliding Circle */}
                                <div
                                    className={`absolute top-1 flex h-20 w-20 items-center justify-center rounded-full bg-white text-3xl shadow-2xl transition-all duration-300 ease-in-out ${
                                        voiceSearchMode === "guarded" ? "left-1 translate-x-0 transform" : "left-1 translate-x-72 transform"
                                    }`}
                                >
                                    {voiceSearchMode === "guarded" ? "🔒" : "🌐"}
                                </div>

                                {/* Button Labels */}
                                <div className="absolute inset-0 flex items-center justify-between px-8 text-xl font-bold text-white">
                                    <span className={`transition-opacity duration-300 ${voiceSearchMode === "guarded" ? "opacity-100" : "opacity-50"}`}>
                                        GUARDED
                                    </span>
                                    <span className={`transition-opacity duration-300 ${voiceSearchMode === "unguarded" ? "opacity-100" : "opacity-50"}`}>
                                        INTERNET
                                    </span>
                                </div>
                            </button>
                        </div>
                    </div>

                    {/* Status Display */}
                    <div
                        className={`mt-6 rounded-2xl p-4 text-center text-xl font-bold ${
                            voiceSearchMode === "guarded"
                                ? "border-2 border-red-300 bg-red-100 text-red-700"
                                : "border-2 border-teal-300 bg-teal-100 text-teal-700"
                        }`}
                    >
                        Current Mode: {voiceSearchMode === "guarded" ? "🔒 GUARDED (Your PDFs Only)" : "🌐 INTERNET (All PDFs)"}
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

    return (
        <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/upload" element={isAuthenticated ? <Upload /> : <Navigate to="/login" />} />
            <Route path="/analyze" element={isAuthenticated ? <Analyze /> : <Navigate to="/login" />} />
            <Route path="/call" element={isAuthenticated ? <CallInterface /> : <Navigate to="/login" />} />
            <Route path="/app" element={isAuthenticated ? <MainApp /> : <Navigate to="/login" />} />
        </Routes>
    );
}

export default App;
