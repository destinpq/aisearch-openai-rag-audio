import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FileText, Search, Eye } from "lucide-react";
import axios from "axios";
import { useAuth } from "@/contexts/AuthContext";

interface SearchResult {
    title: string;
    content: string;
    chunk_id: string;
    filename: string;
    start_line: number;
    end_line: number;
    chunk_index: number;
    total_chunks: number;
    line_reference: string;
}

function Analyze() {
    const [query, setQuery] = useState("");
    const [results, setResults] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [selectedResult, setSelectedResult] = useState<SearchResult | null>(null);
    const [searchMode, setSearchMode] = useState<"guarded" | "unguarded">("guarded");
    const { token } = useAuth();

    const handleAnalyze = async () => {
        if (!query.trim()) return;

        setLoading(true);
        try {
            const requestData: any = { query };

            // If in guarded mode, search only uploaded PDFs
            if (searchMode === "guarded") {
                requestData.filename = "user_uploaded"; // Special flag for user's PDFs
            }

            const response = await axios.post("/api/analyze", requestData, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setResults(response.data);
        } catch (error) {
            setResults({ error: "Analysis failed" });
        } finally {
            setLoading(false);
        }
    };

    const handleViewPDF = (result: SearchResult) => {
        setSelectedResult(result);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
            <div className="mx-auto max-w-6xl space-y-8">
                {/* Search Section */}
                <div className="rounded-lg bg-white p-6 shadow-lg">
                    <div className="mb-6 text-center">
                        <h2 className="text-3xl font-bold text-gray-900">Analyze Your Documents</h2>
                        <p className="mt-2 text-gray-600">Search through your uploaded PDFs with AI-powered analysis</p>
                    </div>
                    <div className="space-y-4">
                        <div>
                            <label htmlFor="query" className="block text-sm font-medium text-gray-700">
                                Search Query
                            </label>
                            <input
                                id="query"
                                type="text"
                                value={query}
                                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setQuery(e.target.value)}
                                placeholder="Enter your question or search terms"
                                className="mt-1 block w-full rounded-md border-gray-300 px-3 py-2 shadow-sm"
                            />
                        </div>

                        {/* Search Mode Toggle */}
                        <div className="space-y-2">
                            <label className="block text-sm font-medium text-gray-700">Search Mode</label>
                            <div className="flex space-x-4">
                                <label className="flex items-center">
                                    <input
                                        type="radio"
                                        name="searchMode"
                                        value="guarded"
                                        checked={searchMode === "guarded"}
                                        onChange={e => setSearchMode(e.target.value as "guarded" | "unguarded")}
                                        className="mr-2"
                                    />
                                    <span className="text-sm text-gray-700">🔒 Guarded - Search only my uploaded PDFs</span>
                                </label>
                                <label className="flex items-center">
                                    <input
                                        type="radio"
                                        name="searchMode"
                                        value="unguarded"
                                        checked={searchMode === "unguarded"}
                                        onChange={e => setSearchMode(e.target.value as "guarded" | "unguarded")}
                                        className="mr-2"
                                    />
                                    <span className="text-sm text-gray-700">🌐 Unguarded - Search all available PDFs</span>
                                </label>
                            </div>
                        </div>

                        <Button onClick={handleAnalyze} className="w-full" disabled={loading || !query.trim()}>
                            {loading ? "Searching..." : `Search Documents (${searchMode})`}
                        </Button>
                    </div>
                </div>

                {/* Results Section */}
                {results && (
                    <div className="rounded-lg bg-white p-6 shadow-lg">
                        <div className="mb-6">
                            <h3 className="text-xl font-bold text-gray-900">Search Results</h3>
                            {results.query && (
                                <p className="mt-1 text-gray-600">
                                    Query: "{results.query}"
                                    {results.search_mode && (
                                        <span className="ml-2 text-sm">
                                            • Mode: <span className="font-medium capitalize">{results.search_mode}</span>
                                        </span>
                                    )}
                                </p>
                            )}
                        </div>

                        {results.error ? (
                            <div className="py-8 text-center">
                                <p className="text-red-500">{results.error}</p>
                            </div>
                        ) : results.results && results.results.length > 0 ? (
                            <div className="space-y-4">
                                <div className="flex items-center justify-between">
                                    <p className="text-gray-600">Found {results.total_results} relevant sections</p>
                                </div>

                                {results.results.map((result: SearchResult, index: number) => (
                                    <Card key={index} className="transition-shadow hover:shadow-md">
                                        <CardHeader>
                                            <CardTitle className="flex items-center justify-between">
                                                <div className="flex items-center">
                                                    <FileText className="mr-2 h-5 w-5 text-blue-500" />
                                                    {result.title}
                                                </div>
                                                <div className="flex items-center space-x-2">
                                                    <Badge variant="outline">{result.filename}</Badge>
                                                    <Badge variant="secondary">{result.line_reference}</Badge>
                                                </div>
                                            </CardTitle>
                                        </CardHeader>
                                        <CardContent>
                                            <p className="mb-4 text-gray-700">{result.content}</p>
                                            <div className="flex items-center justify-between">
                                                <div className="text-sm text-gray-500">
                                                    Chunk {result.chunk_index} of {result.total_chunks}
                                                </div>
                                                <Button size="sm" variant="outline" onClick={() => handleViewPDF(result)}>
                                                    <Eye className="mr-1 h-4 w-4" />
                                                    View in PDF
                                                </Button>
                                            </div>
                                        </CardContent>
                                    </Card>
                                ))}
                            </div>
                        ) : (
                            <div className="py-8 text-center">
                                <Search className="mx-auto h-12 w-12 text-gray-400" />
                                <h3 className="mt-2 text-sm font-medium text-gray-900">No results found</h3>
                                <p className="mt-1 text-sm text-gray-500">Try a different search query or upload more documents.</p>
                            </div>
                        )}
                    </div>
                )}

                {/* PDF Viewer Modal */}
                {selectedResult && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
                        <div className="mx-4 max-h-[90vh] w-full max-w-6xl overflow-hidden rounded-lg bg-white shadow-xl">
                            <div className="border-b p-4">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <h3 className="text-lg font-semibold">{selectedResult.filename}</h3>
                                        <p className="text-sm text-gray-600">
                                            {selectedResult.line_reference} • {selectedResult.title}
                                        </p>
                                    </div>
                                    <Button variant="outline" size="sm" onClick={() => setSelectedResult(null)}>
                                        Close
                                    </Button>
                                </div>
                            </div>
                            <div className="p-4">
                                <div className="mb-4 border-l-4 border-yellow-400 bg-yellow-50 p-4">
                                    <div className="flex">
                                        <div className="ml-3">
                                            <p className="text-sm text-yellow-700">
                                                <strong>Found at:</strong> {selectedResult.line_reference}
                                            </p>
                                            <p className="mt-1 text-sm text-yellow-700">{selectedResult.content}</p>
                                        </div>
                                    </div>
                                </div>
                                <iframe
                                    src={`/uploads/${selectedResult.filename}#page=${Math.ceil(selectedResult.start_line / 50)}`}
                                    className="h-[60vh] w-full rounded border"
                                    title={`PDF Viewer - ${selectedResult.filename}`}
                                />
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default Analyze;
