import { useState, useRef, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Upload, FileText, CheckCircle, AlertCircle, Loader2 } from "lucide-react";

interface UploadStatus {
  status: 'idle' | 'uploading' | 'processing' | 'completed' | 'failed';
  filename?: string;
  message?: string;
  documentId?: string;
  progress?: {
    total_chunks: number;
    processed_chunks: number;
    indexed_chunks: number;
  };
}

export function PDFUploader() {
  const [uploadToIndex, setUploadToIndex] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>({ status: 'idle' });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const statusCheckInterval = useRef<number>();

  const checkDocumentStatus = async (documentId: string) => {
    try {
      console.log('Checking status for document:', documentId);
      const response = await fetch(`/document/${documentId}`, {
        headers: {
          'Accept': 'application/json',
        }
      });
      
      console.log('Status check response:', response.status);
      let responseText;
      try {
        responseText = await response.text();
        console.log('Raw status response:', responseText);
        
        if (!response.ok) {
          throw new Error('Failed to fetch status');
        }
        
        const data = JSON.parse(responseText);
        console.log('Parsed status data:', data);
        
        setUploadStatus(prev => ({
          ...prev,
          status: data.status === 'completed' ? 'completed' : 
                  data.status === 'failed' ? 'failed' : 'processing',
          message: data.error_message,
          progress: {
            total_chunks: data.total_chunks,
            processed_chunks: data.processed_chunks,
            indexed_chunks: data.indexed_chunks
          }
        }));
        
        if (data.status === 'completed' || data.status === 'failed') {
          console.log('Processing completed with status:', data.status);
          if (statusCheckInterval.current) {
            clearInterval(statusCheckInterval.current);
          }
        }
      } catch (parseError) {
        console.error('Error parsing status response:', parseError);
        console.log('Status response text that failed to parse:', responseText);
        throw new Error('Failed to parse status response');
      }
    } catch (error) {
      console.error('Error checking document status:', error);
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setUploadStatus({ status: 'idle' });
    } else {
      setSelectedFile(null);
      setUploadStatus({ 
        status: 'failed', 
        message: 'Please select a valid PDF file' 
      });
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploadStatus({ status: 'uploading', filename: selectedFile.name });
    console.log('Starting upload for file:', selectedFile.name, 'with upload_to_index:', uploadToIndex);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      // First test the server connection
      console.log('Testing server connection...');
      try {
        const testResponse = await fetch('/process-pdf/test');
        const testData = await testResponse.json();
        console.log('Test response:', testData);
      } catch (error) {
        console.error('Server test failed:', error);
        throw new Error('Server connection test failed. Is the backend running?');
      }

      const url = `/process-pdf?upload_to_index=${uploadToIndex}`;
      console.log('Sending request to:', url);
      console.log('FormData contents:', {
        file: selectedFile.name,
        size: selectedFile.size,
        type: selectedFile.type,
        formDataEntries: Array.from(formData.entries()).map(([key, value]) => ({
          key,
          type: value instanceof File ? 'File' : typeof value,
          name: value instanceof File ? value.name : undefined,
          size: value instanceof File ? value.size : undefined
        }))
      });

      const response = await fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json',
        },
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', Object.fromEntries(response.headers.entries()));
      
      let responseText;
      try {
        responseText = await response.text();
        console.log('Raw response:', responseText);
        
        if (!response.ok) {
          throw new Error(`Upload failed: ${responseText}`);
        }
        
        const data = JSON.parse(responseText);
        console.log('Parsed response data:', data);
        
        setUploadStatus(prev => ({
          ...prev,
          documentId: data.document_id,
          status: 'processing',
          message: data.message
        }));

        // Start polling for status
        if (statusCheckInterval.current) {
          clearInterval(statusCheckInterval.current);
        }
        
        statusCheckInterval.current = window.setInterval(
          () => checkDocumentStatus(data.document_id),
          2000
        );
      } catch (parseError) {
        console.error('Error parsing response:', parseError);
        console.log('Response text that failed to parse:', responseText);
        throw new Error('Failed to parse server response');
      }

    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus({
        status: 'failed',
        message: error instanceof Error ? error.message : 'Failed to upload file'
      });
    }
  };

  const resetUpload = () => {
    setSelectedFile(null);
    setUploadStatus({ status: 'idle' });
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    if (statusCheckInterval.current) {
      clearInterval(statusCheckInterval.current);
    }
  };

  // const getProgressValue = () => {
  //   const { progress } = uploadStatus;
  //   if (!progress || !progress.total_chunks) return 0;
    
  //   const processedChunks = progress.processed_chunks || 0;
  //   const indexedChunks = uploadToIndex ? (progress.indexed_chunks || 0) : processedChunks;
    
  //   return (indexedChunks / progress.total_chunks) * 100;
  // };

  // Clean up interval on unmount
  useEffect(() => {
    return () => {
      if (statusCheckInterval.current) {
        clearInterval(statusCheckInterval.current);
      }
    };
  }, []);

  return (
    <Card className="border border-gray-200">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center">
          <FileText className="mr-2 h-5 w-5 text-purple-500" />
          Upload PDF Document
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {uploadStatus.status === 'idle' && (
            <>
              <div className="flex items-center space-x-4">
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileChange}
                  ref={fileInputRef}
                  className="hidden"
                />
                
                <Button 
                  onClick={() => fileInputRef.current?.click()}
                  variant="outline"
                  className="flex-none"
                >
                  <FileText className="mr-2 h-4 w-4" />
                  Select PDF
                </Button>
                
                <div className="flex-1 truncate text-sm">
                  {selectedFile ? (
                    <span className="font-medium">{selectedFile.name}</span>
                  ) : (
                    <span className="text-gray-500">No file selected</span>
                  )}
                </div>
              </div>

              <div className="flex items-center space-x-2 pt-2">
                <Switch
                  id="upload-to-index"
                  checked={uploadToIndex}
                  onCheckedChange={setUploadToIndex}
                />
                <Label htmlFor="upload-to-index" className="text-sm">Add to search index</Label>
              </div>
            </>
          )}

          {uploadStatus.status === 'uploading' && (
            <div className="space-y-2">
              <div className="flex items-center">
                <Upload className="mr-2 h-4 w-4 animate-pulse text-blue-500" />
                <span>Uploading {uploadStatus.filename}...</span>
              </div>
              <Progress value={50} className="w-full" />
            </div>
          )}

          {uploadStatus.status === 'processing' && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <Loader2 className="mr-2 h-4 w-4 animate-spin text-blue-500" />
                  <span>Processing {uploadStatus.filename}</span>
                </div>
                <span className="text-xs text-gray-500">
                  {uploadStatus.progress?.processed_chunks || 0} of {uploadStatus.progress?.total_chunks || 0} chunks
                </span>
              </div>
              <Progress 
                value={uploadStatus.progress?.total_chunks 
                  ? ((uploadStatus.progress.processed_chunks || 0) / uploadStatus.progress.total_chunks) * 100 
                  : 0} 
                className="w-full" 
              />
            </div>
          )}

          {uploadStatus.status === 'completed' && (
            <div className="space-y-3">
              <div className="flex items-center text-green-600">
                <CheckCircle className="mr-2 h-5 w-5" />
                <span>Successfully processed {uploadStatus.filename}</span>
              </div>
              <Button onClick={resetUpload} variant="outline" size="sm" className="mt-1">
                Upload Another
              </Button>
            </div>
          )}

          {uploadStatus.status === 'failed' && (
            <div className="space-y-3">
              <div className="flex items-center text-red-600">
                <AlertCircle className="mr-2 h-5 w-5" />
                <span>Failed to process {uploadStatus.filename}</span>
              </div>
              {uploadStatus.message && (
                <p className="text-sm text-red-500 bg-red-50 p-2 rounded">{uploadStatus.message}</p>
              )}
              <Button onClick={resetUpload} variant="outline" size="sm" className="mt-1">
                Try Again
              </Button>
            </div>
          )}
        </div>
      </CardContent>
      
      {selectedFile && uploadStatus.status === 'idle' && (
        <CardFooter className="pt-0">
          <Button 
            onClick={handleUpload}
            className="w-full bg-purple-600 hover:bg-purple-700"
          >
            <Upload className="mr-2 h-4 w-4" />
            Upload PDF
          </Button>
        </CardFooter>
      )}
    </Card>
  );
} 