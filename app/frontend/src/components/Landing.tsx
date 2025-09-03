import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useState } from "react";

function Landing() {
    const [searchMode, setSearchMode] = useState<"guarded" | "unguarded" | null>(null);

    // If no mode selected yet, show the choice prompt
    if (searchMode === null) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
                <div className="w-full max-w-md space-y-8 text-center">
                    <div>
                        <h1 className="mb-2 text-4xl font-bold text-gray-900">VoiceRAG</h1>
                        <p className="mb-8 text-xl text-gray-600">Interactive Voice Generative AI with RAG</p>
                    </div>

                    <div className="space-y-6 rounded-lg bg-white p-8 shadow-lg">
                        <div>
                            <h2 className="mb-2 text-2xl font-semibold text-gray-900">Choose Search Mode</h2>
                            <p className="text-gray-600">How would you like to search documents?</p>
                        </div>

                        <div className="space-y-4">
                            <button
                                onClick={() => setSearchMode("guarded")}
                                className="w-full rounded-lg border-2 border-blue-200 p-4 text-left transition-colors hover:border-blue-400 hover:bg-blue-50"
                            >
                                <div className="flex items-center space-x-3">
                                    <span className="text-2xl">🔒</span>
                                    <div>
                                        <div className="font-semibold text-gray-900">My Library</div>
                                        <div className="text-sm text-gray-600">Search only your uploaded PDFs</div>
                                    </div>
                                </div>
                            </button>

                            <button
                                onClick={() => setSearchMode("unguarded")}
                                className="w-full rounded-lg border-2 border-teal-200 p-4 text-left transition-colors hover:border-teal-400 hover:bg-teal-50"
                            >
                                <div className="flex items-center space-x-3">
                                    <span className="text-2xl">🌐</span>
                                    <div>
                                        <div className="font-semibold text-gray-900">Internet Search</div>
                                        <div className="text-sm text-gray-600">Search all available PDFs</div>
                                    </div>
                                </div>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // After mode is selected, show the main landing page
    return (
        <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
            {/* Clean mode indicator */}
            <div className="absolute right-4 top-4 rounded-lg bg-white px-4 py-2 shadow-md">
                <div className="flex items-center space-x-2 text-sm">
                    <span>{searchMode === "guarded" ? "🔒" : "🌐"}</span>
                    <span className="font-medium">{searchMode === "guarded" ? "My Library" : "Internet Search"}</span>
                    <button onClick={() => setSearchMode(null)} className="ml-2 text-blue-600 underline hover:text-blue-800">
                        Change
                    </button>
                </div>
            </div>

            <div className="w-full max-w-md space-y-8 text-center">
                <div>
                    <h1 className="mb-2 text-4xl font-bold text-gray-900">VoiceRAG</h1>
                    <p className="mb-4 text-xl text-gray-600">Interactive Voice Generative AI with RAG</p>
                    <p className="text-gray-500">Experience the future of AI-powered conversations with voice interaction and knowledge retrieval.</p>
                </div>
                <div className="space-y-4">
                    <Link to="/login" state={{ searchMode }}>
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
