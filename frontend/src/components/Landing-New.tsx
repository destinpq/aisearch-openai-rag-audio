import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useState } from "react";

function Landing() {
    const [searchMode, setSearchMode] = useState<"guarded" | "unguarded">("guarded");

    return (
        <div className="relative flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
            {/* BIG SLIDER OVERLAY */}
            <div className="fixed left-1/2 top-1/2 z-50 min-w-[600px] -translate-x-1/2 -translate-y-1/2 transform rounded-3xl border-4 border-purple-500 bg-white p-12 shadow-2xl">
                <div className="space-y-8 text-center">
                    <h2 className="text-4xl font-bold text-gray-900">🎛️ SEARCH MODE SLIDER</h2>
                    <p className="text-xl text-gray-600">Choose your search preference</p>

                    <div className="space-y-6">
                        <div className="relative">
                            <input
                                type="range"
                                min="0"
                                max="1"
                                value={searchMode === "guarded" ? 0 : 1}
                                onChange={e => setSearchMode(e.target.value === "0" ? "guarded" : "unguarded")}
                                className="h-20 w-full cursor-pointer appearance-none rounded-full"
                                style={{
                                    background: "linear-gradient(to right, #ff6b6b, #4ecdc4)"
                                }}
                            />
                        </div>

                        <div className="flex justify-between text-2xl font-bold">
                            <span className="text-red-500">🔒 GUARDED</span>
                            <span className="text-teal-500">🌐 UNGUARDED</span>
                        </div>

                        <div
                            className={`rounded-2xl p-6 text-2xl font-bold ${
                                searchMode === "guarded"
                                    ? "border-2 border-red-300 bg-red-100 text-red-700"
                                    : "border-2 border-teal-300 bg-teal-100 text-teal-700"
                            }`}
                        >
                            Current Mode: {searchMode === "guarded" ? "🔒 GUARDED (Your PDFs Only)" : "🌐 UNGUARDED (All PDFs)"}
                        </div>
                    </div>
                </div>
            </div>

            <div className="w-full max-w-md space-y-8 text-center opacity-30">
                <div>
                    <h1 className="mb-2 text-4xl font-bold text-gray-900">VoiceRAG</h1>
                    <p className="mb-4 text-xl text-gray-600">Interactive Voice Generative AI with RAG</p>
                    <p className="text-gray-500">Experience the future of AI-powered conversations with voice interaction and knowledge retrieval.</p>
                </div>
                <div className="space-y-4">
                    <Link to="/login">
                        <Button className="w-full">Get Started</Button>
                    </Link>
                    <p className="text-sm text-gray-500">
                        <Link to="/register" className="text-blue-500">
                            Register
                        </Link>{" "}
                        |{" "}
                        <Link to="/login" className="text-blue-500">
                            Login
                        </Link>
                    </p>
                    <p className="text-sm text-gray-500">Powered by Azure AI Search and OpenAI</p>
                </div>
            </div>
        </div>
    );
}

export default Landing;
