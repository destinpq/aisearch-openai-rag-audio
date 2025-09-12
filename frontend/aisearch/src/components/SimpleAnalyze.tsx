import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Search, FileText, Phone, Mic, UploadIcon, LogOut } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import axios from "axios";

import logo from "../assets/logo.svg";

function SimpleAnalyze() {
    const [query, setQuery] = useState("");
    const [results, setResults] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const { token, logout } = useAuth();

    const handleSearch = async () => {
        if (!query.trim()) return;

        setLoading(true);
        setError("");
        setResults([]);

        try {
            const response = await axios.post("/api/analyze", { query: query.trim() }, { headers: { Authorization: `Bearer ${token}` } });

            setResults(response.data.results || []);
            if (response.data.results?.length === 0) {
                setError("No results found for your query.");
            }
        } catch (err: any) {
            setError(err.response?.data?.error || "Search failed. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === "Enter") {
            handleSearch();
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
            {/* Navigation Header */}
            <header className="flex items-center justify-between bg-white p-4 shadow-md">
                <div className="flex items-center space-x-4">
                    <img src={logo} alt="Azure logo" className="h-8 w-8" />
                    <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text font-bold text-transparent">VoiceRAG</span>
                </div>
                <nav className="flex space-x-2">
                    <Link to="/app">
                        <Button variant="outline" size="sm">
                            <Mic className="mr-2 h-4 w-4" />
                            Voice Chat
                        </Button>
                    </Link>
                    <Link to="/upload">
                        <Button variant="outline" size="sm">
                            <UploadIcon className="mr-2 h-4 w-4" />
                            Upload
                        </Button>
                    </Link>
                    <Link to="/analyze">
                        <Button size="sm" className="bg-blue-600">
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

            {/* Main Content */}
            <div className="p-4">
                <div className="mx-auto max-w-4xl space-y-6">
                    {/* Search Section */}
                    <Card className="bg-white shadow-lg">
                        <CardHeader className="text-center">
                            <CardTitle className="flex items-center justify-center text-3xl font-bold text-gray-900">
                                <Search className="mr-3 h-8 w-8 text-blue-600" />
                                Document Analysis
                            </CardTitle>
                            <p className="mt-2 text-gray-600">Search through your uploaded documents to find specific information</p>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="flex space-x-2">
                                <input
                                    type="text"
                                    value={query}
                                    onChange={e => setQuery(e.target.value)}
                                    onKeyPress={handleKeyPress}
                                    placeholder="Enter your search query (e.g., 'benefits package', 'vacation policy', etc.)"
                                    className="flex-1 rounded-md border border-gray-300 px-4 py-2 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                                <Button onClick={handleSearch} disabled={!query.trim() || loading} className="bg-blue-600 hover:bg-blue-700">
                                    {loading ? "Searching..." : "Search"}
                                </Button>
                            </div>

                            {error && (
                                <div className="rounded-md border border-red-200 bg-red-50 p-3">
                                    <p className="text-sm text-red-600">{error}</p>
                                </div>
                            )}
                        </CardContent>
                    </Card>

                    {/* Results Section */}
                    {results.length > 0 && (
                        <Card className="bg-white shadow-lg">
                            <CardHeader>
                                <CardTitle>Search Results</CardTitle>
                                <p className="text-gray-600">
                                    Found {results.length} result(s) for "{query}"
                                </p>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                {results.map((result, index) => (
                                    <div key={index} className="rounded-lg border border-gray-200 p-4">
                                        <div className="mb-2 flex items-center space-x-2">
                                            <FileText className="h-5 w-5 text-blue-600" />
                                            <h3 className="font-semibold text-gray-900">{result.documentName || result.title}</h3>
                                            {result.folderName && <span className="text-sm text-gray-500">in {result.folderName}</span>}
                                        </div>

                                        {result.matches && result.matches.length > 0 && (
                                            <div className="space-y-2">
                                                {result.matches.slice(0, 3).map((match: any, matchIndex: number) => (
                                                    <div key={matchIndex} className="rounded border-l-4 border-blue-400 bg-gray-50 p-3">
                                                        {match.lineNumber && (
                                                            <div className="mb-1 text-xs font-medium text-blue-600">Line {match.lineNumber}</div>
                                                        )}
                                                        <p className="text-sm text-gray-700">{match.text || match.content}</p>
                                                        {match.context && match.context !== match.text && (
                                                            <details className="mt-2">
                                                                <summary className="cursor-pointer text-xs text-gray-500">Show context</summary>
                                                                <div className="mt-1 whitespace-pre-wrap text-xs text-gray-600">{match.context}</div>
                                                            </details>
                                                        )}
                                                    </div>
                                                ))}
                                                {result.matches.length > 3 && (
                                                    <p className="text-sm text-gray-500">... and {result.matches.length - 3} more matches</p>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </CardContent>
                        </Card>
                    )}

                    {/* Help Section */}
                    <Card className="bg-white shadow">
                        <CardHeader>
                            <CardTitle className="text-lg">Search Tips</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-1 gap-4 text-sm text-gray-600 md:grid-cols-2">
                                <div>
                                    <h4 className="mb-2 font-medium text-gray-900">Search Examples:</h4>
                                    <ul className="space-y-1">
                                        <li>• "vacation policy"</li>
                                        <li>• "health benefits"</li>
                                        <li>• "employee handbook"</li>
                                        <li>• "401k retirement"</li>
                                    </ul>
                                </div>
                                <div>
                                    <h4 className="mb-2 font-medium text-gray-900">Features:</h4>
                                    <ul className="space-y-1">
                                        <li>• Search across all uploaded PDFs</li>
                                        <li>• Find exact line numbers</li>
                                        <li>• View context around matches</li>
                                        <li>• Multiple results per document</li>
                                    </ul>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}

export default SimpleAnalyze;
