import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FileText, Eye, Trash2 } from "lucide-react";
import axios from "axios";
import { useAuth } from "@/contexts/AuthContext";

interface UploadedFile {
    filename: string;
    size: number;
    modified: number;
    user_id: string;
}

function Upload() {
    const [file, setFile] = useState<File | null>(null);
    const [message, setMessage] = useState("");
    const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
    const [loading, setLoading] = useState(false);
    const [selectedFile, setSelectedFile] = useState<UploadedFile | null>(null);
    const { token } = useAuth();

    const fetchUploadedFiles = async () => {
        try {
            const response = await axios.get("/api/files", {
                headers: { Authorization: `Bearer ${token}` }
            });
            setUploadedFiles(response.data.files);
        } catch (error) {
            console.error("Failed to fetch files:", error);
        }
    };

    useEffect(() => {
        if (token) {
            fetchUploadedFiles();
        }
    }, [token]);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            setFile(e.target.files[0]);
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setLoading(true);
        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await axios.post("/api/upload", formData, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setMessage(response.data.message);
            setFile(null);
            // Reset file input
            const fileInput = document.getElementById("file") as HTMLInputElement;
            if (fileInput) fileInput.value = "";
            // Refresh file list
            fetchUploadedFiles();
        } catch (error: any) {
            if (error.response?.status === 409) {
                setMessage("File already exists");
            } else {
                setMessage("Upload failed");
            }
        } finally {
            setLoading(false);
        }
    };

    const formatFileSize = (bytes: number) => {
        if (bytes === 0) return "0 Bytes";
        const k = 1024;
        const sizes = ["Bytes", "KB", "MB", "GB"];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
    };

    const formatDate = (timestamp: number) => {
        return new Date(timestamp * 1000).toLocaleDateString();
    };

    const handleViewFile = (file: UploadedFile) => {
        setSelectedFile(file);
    };

    const handleDeleteFile = async (filename: string) => {
        // Note: This would require a delete endpoint in the backend
        // For now, just show a message
        setMessage(`Delete functionality for ${filename} not implemented yet`);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
            <div className="mx-auto max-w-6xl space-y-8">
                {/* Upload Section */}
                <div className="rounded-lg bg-white p-6 shadow-lg">
                    <div className="mb-6 text-center">
                        <h2 className="text-3xl font-bold text-gray-900">Upload PDF</h2>
                        <p className="mt-2 text-gray-600">Upload a PDF for analysis</p>
                    </div>
                    <div className="space-y-4">
                        <div>
                            <label htmlFor="file" className="block text-sm font-medium text-gray-700">
                                Select PDF File
                            </label>
                            <input id="file" type="file" accept=".pdf" onChange={handleFileChange} className="mt-1 block w-full" />
                        </div>
                        <Button onClick={handleUpload} className="w-full" disabled={!file || loading}>
                            {loading ? "Uploading..." : "Upload"}
                        </Button>
                        {message && <p className="text-center text-gray-600">{message}</p>}
                    </div>
                </div>

                {/* Uploaded Files Section */}
                <div className="rounded-lg bg-white p-6 shadow-lg">
                    <div className="mb-6 text-center">
                        <h2 className="text-3xl font-bold text-gray-900">Your Uploaded Files</h2>
                        <p className="mt-2 text-gray-600">View and manage your uploaded PDFs</p>
                    </div>

                    {uploadedFiles.length === 0 ? (
                        <div className="py-8 text-center">
                            <FileText className="mx-auto h-12 w-12 text-gray-400" />
                            <h3 className="mt-2 text-sm font-medium text-gray-900">No files uploaded</h3>
                            <p className="mt-1 text-sm text-gray-500">Upload your first PDF to get started.</p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
                            {uploadedFiles.map((file, index) => (
                                <Card key={index} className="transition-shadow hover:shadow-md">
                                    <CardHeader className="pb-3">
                                        <CardTitle className="flex items-center text-lg">
                                            <FileText className="mr-2 h-5 w-5 text-red-500" />
                                            {file.filename}
                                        </CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="space-y-2">
                                            <div className="flex justify-between text-sm">
                                                <span className="text-gray-500">Size:</span>
                                                <Badge variant="secondary">{formatFileSize(file.size)}</Badge>
                                            </div>
                                            <div className="flex justify-between text-sm">
                                                <span className="text-gray-500">Modified:</span>
                                                <span className="text-gray-700">{formatDate(file.modified)}</span>
                                            </div>
                                            <div className="mt-4 flex space-x-2">
                                                <Button size="sm" variant="outline" onClick={() => handleViewFile(file)} className="flex-1">
                                                    <Eye className="mr-1 h-4 w-4" />
                                                    View
                                                </Button>
                                                <Button
                                                    size="sm"
                                                    variant="outline"
                                                    onClick={() => handleDeleteFile(file.filename)}
                                                    className="text-red-600 hover:text-red-700"
                                                >
                                                    <Trash2 className="h-4 w-4" />
                                                </Button>
                                            </div>
                                        </div>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    )}
                </div>

                {/* PDF Viewer Modal */}
                {selectedFile && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
                        <div className="mx-4 max-h-[90vh] w-full max-w-4xl overflow-hidden rounded-lg bg-white shadow-xl">
                            <div className="border-b p-4">
                                <div className="flex items-center justify-between">
                                    <h3 className="text-lg font-semibold">{selectedFile.filename}</h3>
                                    <Button variant="outline" size="sm" onClick={() => setSelectedFile(null)}>
                                        Close
                                    </Button>
                                </div>
                            </div>
                            <div className="p-4">
                                <iframe
                                    src={`/uploads/${selectedFile.filename}`}
                                    className="h-[70vh] w-full rounded border"
                                    title={`PDF Viewer - ${selectedFile.filename}`}
                                />
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default Upload;
