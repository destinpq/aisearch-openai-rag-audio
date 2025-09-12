import React, { useState, useRef, useCallback } from "react";
import { Upload, FileText, Search, BarChart3, Zap, Database, MapPin } from "lucide-react";

interface TokenResult {
    token_id: string;
    content: string;
    token_count: number;
    page_number: number;
    line_start: number;
    line_end: number;
    char_start: number;
    char_end: number;
    bbox: {
        x: number;
        y: number;
        width: number;
        height: number;
    };
    filename: string;
    highlight_info: {
        highlightLine: number;
        highlightText: string;
    };
    live_data?: string;
    enhanced_at?: string;
}

interface DocumentStats {
    document: {
        id: number;
        filename: string;
        upload_date: string;
        total_pages: number;
    };
    tokens: {
        total_chunks: number;
        total_tokens: number;
        avg_tokens_per_chunk: number;
        page_range: string;
    };
    page_distribution: Array<{
        page: number;
        chunks: number;
    }>;
    images: {
        total_images: number;
    };
}

export default function EnhancedPDFProcessor() {
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [uploadResult, setUploadResult] = useState<any>(null);
    const [searchQuery, setSearchQuery] = useState("");
    const [searchResults, setSearchResults] = useState<TokenResult[]>([]);
    const [searching, setSearching] = useState(false);
    const [documentStats, setDocumentStats] = useState<DocumentStats | null>(null);
    const [selectedDocId, setSelectedDocId] = useState<number | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileSelect = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file && file.type === "application/pdf") {
            setSelectedFile(file);
            setUploadResult(null);
        } else {
            alert("Please select a PDF file");
        }
    }, []);

    const handleUpload = useCallback(async () => {
        if (!selectedFile) return;

        setUploading(true);
        const formData = new FormData();
        formData.append("file", selectedFile);

        try {
            const response = await fetch("/api/pdf/upload", {
                method: "POST",
                body: formData,
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("token")}`
                }
            });

            const result = await response.json();

            if (result.success) {
                setUploadResult(result.result);
                setSelectedDocId(result.result.doc_id);

                // Automatically fetch document stats
                if (result.result.doc_id) {
                    await fetchDocumentStats(result.result.doc_id);
                }
            } else {
                alert(`Upload failed: ${result.error || "Unknown error"}`);
            }
        } catch (error) {
            console.error("Upload error:", error);
            alert("Upload failed. Please try again.");
        } finally {
            setUploading(false);
        }
    }, [selectedFile]);

    const fetchDocumentStats = async (docId: number) => {
        try {
            const response = await fetch(`/api/pdf/document/${docId}`, {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("token")}`
                }
            });

            const result = await response.json();
            if (result.success) {
                setDocumentStats(result.document_stats);
            }
        } catch (error) {
            console.error("Error fetching document stats:", error);
        }
    };

    const handleSearch = useCallback(async () => {
        if (!searchQuery.trim()) return;

        setSearching(true);
        try {
            const response = await fetch("/api/pdf/search", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${localStorage.getItem("token")}`
                },
                body: JSON.stringify({
                    query: searchQuery,
                    doc_id: selectedDocId,
                    limit: 10
                })
            });

            const result = await response.json();
            if (result.success) {
                setSearchResults(result.results);
            } else {
                alert(`Search failed: ${result.error || "Unknown error"}`);
            }
        } catch (error) {
            console.error("Search error:", error);
            alert("Search failed. Please try again.");
        } finally {
            setSearching(false);
        }
    }, [searchQuery, selectedDocId]);

    const handleAnalyzeWithLiveData = useCallback(async () => {
        if (!searchQuery.trim()) return;

        setSearching(true);
        try {
            const response = await fetch("/api/pdf/analyze", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${localStorage.getItem("token")}`
                },
                body: JSON.stringify({
                    query: searchQuery,
                    context_tokens: searchResults.slice(0, 3).map(r => r.token_id)
                })
            });

            const result = await response.json();
            if (result.success) {
                setSearchResults(result.token_matches);
                // Show analysis result in a modal or separate section
                console.log("Analysis result:", result.analysis);
            }
        } catch (error) {
            console.error("Analysis error:", error);
        } finally {
            setSearching(false);
        }
    }, [searchQuery, searchResults]);

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
            <div className="mx-auto max-w-7xl">
                {/* Header */}
                <div className="mb-8 text-center">
                    <h1 className="mb-4 text-4xl font-bold text-white">Enhanced PDF Processing System</h1>
                    <p className="text-lg text-gray-300">
                        Upload PDFs for token-based analysis with page/line precision, vectorization, live data enhancement, and image analysis
                    </p>
                </div>

                {/* Upload Section */}
                <div className="mb-8 rounded-xl bg-white/10 p-6 backdrop-blur-sm">
                    <h2 className="mb-4 flex items-center text-2xl font-semibold text-white">
                        <Upload className="mr-2" />
                        Upload PDF for Processing
                    </h2>

                    <div className="flex flex-col gap-4 sm:flex-row">
                        <input type="file" ref={fileInputRef} onChange={handleFileSelect} accept=".pdf" className="hidden" />

                        <button
                            onClick={() => fileInputRef.current?.click()}
                            className="flex flex-1 items-center justify-center rounded-lg bg-blue-600 px-6 py-3 text-white transition-colors hover:bg-blue-700"
                        >
                            <FileText className="mr-2" />
                            Choose PDF File
                        </button>

                        <button
                            onClick={handleUpload}
                            disabled={!selectedFile || uploading}
                            className="flex flex-1 items-center justify-center rounded-lg bg-green-600 px-6 py-3 text-white transition-colors hover:bg-green-700 disabled:bg-gray-600"
                        >
                            {uploading ? (
                                <>Processing...</>
                            ) : (
                                <>
                                    <Database className="mr-2" />
                                    Process & Tokenize
                                </>
                            )}
                        </button>
                    </div>

                    {selectedFile && (
                        <div className="mt-4 text-gray-300">
                            Selected: <span className="font-medium text-white">{selectedFile.name}</span>
                        </div>
                    )}
                </div>

                {/* Upload Results */}
                {uploadResult && (
                    <div className="mb-8 rounded-xl bg-green-600/20 p-6 backdrop-blur-sm">
                        <h3 className="mb-4 text-xl font-semibold text-white">Processing Results</h3>
                        <div className="grid grid-cols-2 gap-4 text-center md:grid-cols-4">
                            <div className="rounded-lg bg-white/10 p-4">
                                <div className="text-2xl font-bold text-white">{uploadResult.total_tokens}</div>
                                <div className="text-gray-300">Total Tokens</div>
                            </div>
                            <div className="rounded-lg bg-white/10 p-4">
                                <div className="text-2xl font-bold text-white">{uploadResult.total_pages}</div>
                                <div className="text-gray-300">Pages</div>
                            </div>
                            <div className="rounded-lg bg-white/10 p-4">
                                <div className="text-2xl font-bold text-white">{uploadResult.chunks_created}</div>
                                <div className="text-gray-300">Chunks Created</div>
                            </div>
                            <div className="rounded-lg bg-white/10 p-4">
                                <div className="text-2xl font-bold text-green-400">✓</div>
                                <div className="text-gray-300">Status</div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Document Statistics */}
                {documentStats && (
                    <div className="mb-8 rounded-xl bg-white/10 p-6 backdrop-blur-sm">
                        <h3 className="mb-4 flex items-center text-xl font-semibold text-white">
                            <BarChart3 className="mr-2" />
                            Document Statistics
                        </h3>

                        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                            <div>
                                <h4 className="mb-3 text-lg font-medium text-white">Token Analysis</h4>
                                <div className="space-y-2">
                                    <div className="flex justify-between text-gray-300">
                                        <span>Total Chunks:</span>
                                        <span className="font-medium text-white">{documentStats.tokens.total_chunks}</span>
                                    </div>
                                    <div className="flex justify-between text-gray-300">
                                        <span>Total Tokens:</span>
                                        <span className="font-medium text-white">{documentStats.tokens.total_tokens}</span>
                                    </div>
                                    <div className="flex justify-between text-gray-300">
                                        <span>Avg per Chunk:</span>
                                        <span className="font-medium text-white">{documentStats.tokens.avg_tokens_per_chunk}</span>
                                    </div>
                                </div>
                            </div>

                            <div>
                                <h4 className="mb-3 text-lg font-medium text-white">Page Distribution</h4>
                                <div className="max-h-32 space-y-1 overflow-y-auto">
                                    {documentStats.page_distribution.map(page => (
                                        <div key={page.page} className="flex justify-between text-sm text-gray-300">
                                            <span>Page {page.page}:</span>
                                            <span className="text-white">{page.chunks} chunks</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Search Section */}
                <div className="mb-8 rounded-xl bg-white/10 p-6 backdrop-blur-sm">
                    <h2 className="mb-4 flex items-center text-2xl font-semibold text-white">
                        <Search className="mr-2" />
                        Search with Precision
                    </h2>

                    <div className="mb-4 flex flex-col gap-4 sm:flex-row">
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={e => setSearchQuery(e.target.value)}
                            placeholder="Enter your search query..."
                            className="flex-1 rounded-lg border border-white/30 bg-white/20 px-4 py-3 text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            onKeyPress={e => e.key === "Enter" && handleSearch()}
                        />

                        <button
                            onClick={handleSearch}
                            disabled={!searchQuery.trim() || searching}
                            className="flex items-center justify-center rounded-lg bg-blue-600 px-6 py-3 text-white transition-colors hover:bg-blue-700 disabled:bg-gray-600"
                        >
                            {searching ? "Searching..." : "Search Tokens"}
                        </button>

                        <button
                            onClick={handleAnalyzeWithLiveData}
                            disabled={!searchQuery.trim() || searching}
                            className="flex items-center justify-center rounded-lg bg-purple-600 px-6 py-3 text-white transition-colors hover:bg-purple-700 disabled:bg-gray-600"
                        >
                            <Zap className="mr-2" />
                            {searching ? "Analyzing..." : "Analyze + Live Data"}
                        </button>
                    </div>
                </div>

                {/* Search Results */}
                {searchResults.length > 0 && (
                    <div className="rounded-xl bg-white/10 p-6 backdrop-blur-sm">
                        <h3 className="mb-4 text-xl font-semibold text-white">Search Results ({searchResults.length} found)</h3>

                        <div className="space-y-4">
                            {searchResults.map(result => (
                                <div key={result.token_id} className="rounded-lg border border-white/20 bg-white/5 p-4">
                                    <div className="mb-3 flex flex-wrap items-center gap-4">
                                        <div className="flex items-center text-blue-400">
                                            <MapPin className="mr-1 h-4 w-4" />
                                            Page {result.page_number}, Lines {result.line_start}-{result.line_end}
                                        </div>
                                        <div className="text-green-400">{result.token_count} tokens</div>
                                        <div className="text-purple-400">Token ID: {result.token_id}</div>
                                    </div>

                                    <div className="mb-3 leading-relaxed text-gray-300">{result.content}</div>

                                    {result.bbox && (
                                        <div className="mb-2 text-xs text-gray-400">
                                            Position: x={result.bbox.x.toFixed(1)}, y={result.bbox.y.toFixed(1)}, w={result.bbox.width.toFixed(1)}, h=
                                            {result.bbox.height.toFixed(1)}
                                        </div>
                                    )}

                                    {result.live_data && (
                                        <div className="mt-3 rounded-lg bg-gradient-to-r from-purple-600/20 to-pink-600/20 p-3">
                                            <h4 className="mb-2 flex items-center font-medium text-white">
                                                <Zap className="mr-1 h-4 w-4" />
                                                Live Data Enhancement
                                            </h4>
                                            <p className="text-sm text-gray-300">{result.live_data}</p>
                                            {result.enhanced_at && (
                                                <div className="mt-2 text-xs text-gray-400">Enhanced at: {new Date(result.enhanced_at).toLocaleString()}</div>
                                            )}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
