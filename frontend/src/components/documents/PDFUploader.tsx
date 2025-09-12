import { useState, useRef, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Upload, FileText, CheckCircle, AlertCircle, Loader2 } from "lucide-react";

interface FileUploadStatus {
  status: 'idle' | 'uploading' | 'processing' | 'completed' | 'failed';
  filename: string;
  message?: string;
  documentId?: string;
  progress?: {
    total_chunks: number;
    processed_chunks: number;
    indexed_chunks: number;
  };
  file: File;
}

interface UploadStatus {
  overall: 'idle' | 'uploading' | 'processing' | 'completed' | 'failed';
  files: FileUploadStatus[];
  message?: string;
}

export function PDFUploader() {
  const [uploadToIndex, setUploadToIndex] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>({
    overall: 'idle',
    files: []
  });
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isBatchMode, setIsBatchMode] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const statusCheckIntervals = useRef<{[key: string]: number}>({});

  const checkDocumentStatus = async (documentId: string, filename: string) => {
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

        // Update the specific file status
        setUploadStatus(prev => ({
          ...prev,
          files: prev.files.map(file =>
            file.filename === filename ? {
              ...file,
              status: data.status === 'completed' ? 'completed' :
                     data.status === 'failed' ? 'failed' : 'processing',
              message: data.error_message,
              progress: {
                total_chunks: data.total_chunks,
                processed_chunks: data.processed_chunks,
                indexed_chunks: data.indexed_chunks
              }
            } : file
          ),
          overall: prev.files.every(f => f.status === 'completed') ? 'completed' :
                  prev.files.some(f => f.status === 'failed') ? 'failed' :
                  prev.files.some(f => f.status === 'processing' || f.status === 'uploading') ? 'processing' : 'idle'
        }));

        if (data.status === 'completed' || data.status === 'failed') {
          console.log('Processing completed with status:', data.status);
          if (statusCheckIntervals.current[documentId]) {
            clearInterval(statusCheckIntervals.current[documentId]);
            delete statusCheckIntervals.current[documentId];
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
    const files = Array.from(event.target.files || []);
    const validFiles = files.filter(file => file.type === 'application/pdf');

    if (validFiles.length > 0) {
      setSelectedFiles(validFiles);
      setUploadStatus({
        overall: 'idle',
        files: validFiles.map(file => ({
          status: 'idle',
          filename: file.name,
          file: file
        }))
      });
    } else {
      setSelectedFiles([]);
      setUploadStatus({
        overall: 'failed',
        files: [],
        message: files.length > 0 ? 'Please select valid PDF files only' : 'No files selected'
      });
    }
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;

    // Test server connection first
    try {
      console.log('Testing server connection...');
      const testResponse = await fetch('/process-pdf/test');
      const testData = await testResponse.json();
      console.log('Test response:', testData);
    } catch (error) {
      console.error('Server test failed:', error);
      setUploadStatus({
        overall: 'failed',
        files: [],
        message: 'Server connection test failed. Is the backend running?'
      });
      return;
    }

    // Initialize upload status for all files
    setUploadStatus(prev => ({
      ...prev,
      overall: 'uploading',
      files: prev.files.map(file => ({ ...file, status: 'uploading' }))
    }));

    console.log(`Starting concurrent upload for ${selectedFiles.length} files with upload_to_index:`, uploadToIndex);

    // Process all files concurrently
    const uploadPromises = selectedFiles.map(async (file) => {
      const formData = new FormData();
      formData.append('file', file);

      try {
        console.log(`Uploading file: ${file.name}`);
        const url = `/process-pdf?upload_to_index=${uploadToIndex}`;

        const response = await fetch(url, {
          method: 'POST',
          body: formData,
          headers: {
            'Accept': 'application/json',
          },
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`Upload failed: ${errorText}`);
        }

        const data = await response.json();
        console.log(`Successfully uploaded ${file.name}, document ID: ${data.document_id}`);

        // Update file status to processing
        setUploadStatus(prev => ({
          ...prev,
          files: prev.files.map(f =>
            f.filename === file.name ? {
              ...f,
              status: 'processing',
              documentId: data.document_id,
              message: data.message
            } : f
          )
        }));

        // Start polling for this file's status
        const intervalId = window.setInterval(
          () => checkDocumentStatus(data.document_id, file.name),
          2000
        );
        statusCheckIntervals.current[data.document_id] = intervalId;

        return { success: true, filename: file.name, documentId: data.document_id };
      } catch (error) {
        console.error(`Upload error for ${file.name}:`, error);

        // Update file status to failed
        setUploadStatus(prev => ({
          ...prev,
          files: prev.files.map(f =>
            f.filename === file.name ? {
              ...f,
              status: 'failed',
              message: error instanceof Error ? error.message : 'Failed to upload file'
            } : f
          )
        }));

        return { success: false, filename: file.name, error: error instanceof Error ? error.message : 'Upload failed' };
      }
    });

    // Wait for all uploads to complete
    const results = await Promise.allSettled(uploadPromises);
    const successfulUploads = results.filter(result =>
      result.status === 'fulfilled' && result.value.success
    ).length;

    console.log(`Upload summary: ${successfulUploads}/${selectedFiles.length} files uploaded successfully`);

    // Update overall status
    setUploadStatus(prev => ({
      ...prev,
      overall: successfulUploads === selectedFiles.length ? 'processing' :
              successfulUploads > 0 ? 'processing' : 'failed',
      message: `${successfulUploads}/${selectedFiles.length} files uploaded successfully`
    }));
  };

  const handleBatchUpload = async () => {
    if (selectedFiles.length === 0) return;

    // Test server connection first
    try {
      console.log('Testing server connection...');
      const testResponse = await fetch('/process-pdf/test');
      const testData = await testResponse.json();
      console.log('Test response:', testData);
    } catch (error) {
      console.error('Server test failed:', error);
      setUploadStatus({
        overall: 'failed',
        files: [],
        message: 'Server connection test failed. Is the backend running?'
      });
      return;
    }

    // Initialize upload status for all files
    setUploadStatus(prev => ({
      ...prev,
      overall: 'uploading',
      files: prev.files.map(file => ({ ...file, status: 'uploading' }))
    }));

    console.log(`Starting batch upload for ${selectedFiles.length} files with upload_to_index:`, uploadToIndex);

    try {
      // Prepare FormData for batch upload
      const formData = new FormData();
      selectedFiles.forEach(file => {
        formData.append('files', file);
      });

      const url = `/process-batch-pdfs?upload_to_index=${uploadToIndex}`;
      console.log('Sending batch request to:', url);

      const response = await fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Batch upload failed: ${errorText}`);
      }

      const data = await response.json();
      console.log('Batch upload response:', data);

      // Update status based on batch results
      const successfulUploads = data.successful_uploads || 0;
      const totalFiles = data.total_files || selectedFiles.length;

      if (successfulUploads === totalFiles) {
        setUploadStatus({
          overall: 'processing',
          files: data.results?.map((result: any) => ({
            status: 'processing',
            filename: result.filename,
            documentId: result.document_id,
            message: result.message,
            file: selectedFiles.find(f => f.name === result.filename)!
          })) || [],
          message: data.message
        });

        // Start polling for status of all successful uploads
        data.results?.forEach((result: any) => {
          const intervalId = window.setInterval(
            () => checkDocumentStatus(result.document_id, result.filename),
            2000
          );
          statusCheckIntervals.current[result.document_id] = intervalId;
        });
      } else {
        setUploadStatus({
          overall: 'failed',
          files: [],
          message: `Batch upload partially failed: ${successfulUploads}/${totalFiles} files uploaded successfully`
        });
      }

    } catch (error) {
      console.error('Batch upload error:', error);
      setUploadStatus({
        overall: 'failed',
        files: [],
        message: error instanceof Error ? error.message : 'Failed to upload files in batch'
      });
    }
  };

  const resetUpload = () => {
    setSelectedFiles([]);
    setUploadStatus({ overall: 'idle', files: [] });
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    // Clear all status check intervals
    Object.values(statusCheckIntervals.current).forEach(intervalId => {
      clearInterval(intervalId);
    });
    statusCheckIntervals.current = {};
  };

  // const getProgressValue = () => {
  //   const { progress } = uploadStatus;
  //   if (!progress || !progress.total_chunks) return 0;
    
  //   const processedChunks = progress.processed_chunks || 0;
  //   const indexedChunks = uploadToIndex ? (progress.indexed_chunks || 0) : processedChunks;
    
  //   return (indexedChunks / progress.total_chunks) * 100;
  // };

  // Clean up intervals on unmount
  useEffect(() => {
    return () => {
      Object.values(statusCheckIntervals.current).forEach(intervalId => {
        clearInterval(intervalId);
      });
    };
  }, []);

  return (
    <Card className="border border-gray-200">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center">
          <FileText className="mr-2 h-5 w-5 text-purple-500" />
          Upload PDF Documents
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {uploadStatus.overall === 'idle' && (
            <>
              <div className="space-y-2">
                <input
                  type="file"
                  accept=".pdf"
                  multiple
                  onChange={handleFileChange}
                  ref={fileInputRef}
                  className="hidden"
                />

                <Button
                  onClick={() => fileInputRef.current?.click()}
                  variant="outline"
                  className="w-full"
                >
                  <FileText className="mr-2 h-4 w-4" />
                  Select PDF Files
                </Button>

                {selectedFiles.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-sm font-medium">Selected files:</p>
                    <div className="max-h-32 overflow-y-auto space-y-1">
                      {selectedFiles.map((file, index) => (
                        <div key={index} className="flex items-center justify-between text-sm bg-gray-50 p-2 rounded">
                          <span className="truncate flex-1 mr-2">{file.name}</span>
                          <span className="text-gray-500 text-xs">
                            {(file.size / 1024 / 1024).toFixed(1)} MB
                          </span>
                        </div>
                      ))}
                    </div>
                    <p className="text-xs text-gray-500">
                      {selectedFiles.length} file{selectedFiles.length !== 1 ? 's' : ''} selected
                    </p>
                  </div>
                )}
              </div>

              <div className="flex items-center justify-between pt-2">
                <div className="flex items-center space-x-2">
                  <Switch
                    id="upload-to-index"
                    checked={uploadToIndex}
                    onCheckedChange={setUploadToIndex}
                  />
                  <Label htmlFor="upload-to-index" className="text-sm">Add to search index</Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Switch
                    id="batch-mode"
                    checked={isBatchMode}
                    onCheckedChange={setIsBatchMode}
                  />
                  <Label htmlFor="batch-mode" className="text-sm">Batch mode</Label>
                </div>
              </div>
            </>
          )}

          {uploadStatus.overall === 'uploading' && (
            <div className="space-y-3">
              <div className="flex items-center">
                <Upload className="mr-2 h-4 w-4 animate-pulse text-blue-500" />
                <span>Uploading {selectedFiles.length} files...</span>
              </div>
              <div className="space-y-2">
                {uploadStatus.files.map((file, index) => (
                  <div key={index} className="flex items-center justify-between text-sm">
                    <span className="truncate flex-1 mr-2">{file.filename}</span>
                    <div className="flex items-center">
                      {file.status === 'uploading' && <Upload className="h-3 w-3 animate-pulse text-blue-500 mr-1" />}
                      {file.status === 'processing' && <Loader2 className="h-3 w-3 animate-spin text-blue-500 mr-1" />}
                      {file.status === 'completed' && <CheckCircle className="h-3 w-3 text-green-500 mr-1" />}
                      {file.status === 'failed' && <AlertCircle className="h-3 w-3 text-red-500 mr-1" />}
                      <span className="text-xs">
                        {file.status === 'uploading' && 'Uploading...'}
                        {file.status === 'processing' && 'Processing...'}
                        {file.status === 'completed' && 'Done'}
                        {file.status === 'failed' && 'Failed'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {uploadStatus.overall === 'processing' && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <Loader2 className="mr-2 h-4 w-4 animate-spin text-blue-500" />
                  <span>Processing files...</span>
                </div>
                <span className="text-xs text-gray-500">
                  {uploadStatus.files.filter(f => f.status === 'completed').length} of {uploadStatus.files.length} completed
                </span>
              </div>

              <div className="space-y-3">
                {uploadStatus.files.map((file, index) => (
                  <div key={index} className="border rounded-lg p-3 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-sm truncate flex-1 mr-2">{file.filename}</span>
                      <div className="flex items-center">
                        {file.status === 'processing' && <Loader2 className="h-3 w-3 animate-spin text-blue-500 mr-1" />}
                        {file.status === 'completed' && <CheckCircle className="h-3 w-3 text-green-500 mr-1" />}
                        {file.status === 'failed' && <AlertCircle className="h-3 w-3 text-red-500 mr-1" />}
                        <span className="text-xs">
                          {file.status === 'processing' && 'Processing'}
                          {file.status === 'completed' && 'Completed'}
                          {file.status === 'failed' && 'Failed'}
                        </span>
                      </div>
                    </div>

                    {file.status === 'processing' && file.progress && (
                      <div className="space-y-1">
                        <Progress
                          value={file.progress.total_chunks
                            ? ((file.progress.processed_chunks || 0) / file.progress.total_chunks) * 100
                            : 0}
                          className="w-full h-2"
                        />
                        <p className="text-xs text-gray-500">
                          {file.progress.processed_chunks || 0} of {file.progress.total_chunks || 0} chunks processed
                          {uploadToIndex && ` • ${file.progress.indexed_chunks || 0} indexed`}
                        </p>
                      </div>
                    )}

                    {file.status === 'failed' && file.message && (
                      <p className="text-xs text-red-600 bg-red-50 p-2 rounded">{file.message}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {uploadStatus.overall === 'completed' && (
            <div className="space-y-3">
              <div className="flex items-center text-green-600">
                <CheckCircle className="mr-2 h-5 w-5" />
                <span>All files processed successfully</span>
              </div>
              <div className="text-sm text-gray-600">
                {uploadStatus.files.filter(f => f.status === 'completed').length} of {uploadStatus.files.length} files completed
              </div>
              <Button onClick={resetUpload} variant="outline" size="sm" className="mt-1">
                Upload More Files
              </Button>
            </div>
          )}

          {uploadStatus.overall === 'failed' && (
            <div className="space-y-3">
              <div className="flex items-center text-red-600">
                <AlertCircle className="mr-2 h-5 w-5" />
                <span>Upload failed</span>
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

      {selectedFiles.length > 0 && uploadStatus.overall === 'idle' && (
        <CardFooter className="pt-0">
          <Button
            onClick={isBatchMode ? handleBatchUpload : handleUpload}
            className="w-full bg-purple-600 hover:bg-purple-700"
          >
            <Upload className="mr-2 h-4 w-4" />
            {isBatchMode ? 'Batch Upload' : 'Upload'} {selectedFiles.length} PDF{selectedFiles.length !== 1 ? 's' : ''}
          </Button>
        </CardFooter>
      )}
    </Card>
  );
} 