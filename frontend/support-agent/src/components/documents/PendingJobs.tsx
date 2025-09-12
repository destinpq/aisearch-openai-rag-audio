import { useState, useEffect } from 'react';
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Loader2, CheckCircle2, XCircle } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface PendingJob {
  id: string;
  filename: string;
  status: string;
  created_at: string;
  updated_at: string;
  total_chunks: number;
  processed_chunks: number;
  indexed_chunks: number;
  error_message?: string;
  metadata?: {
    title: string;
    upload_to_index: boolean;
  };
}

export function PendingJobs() {
  const [pendingJobs, setPendingJobs] = useState<PendingJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Function to fetch pending jobs
  const fetchPendingJobs = async () => {
    try {
      const response = await fetch('/documents/pending', {
        headers: {
          'Accept': 'application/json',
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch pending jobs');
      }
      
      const data = await response.json();
      setPendingJobs(data.documents || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching pending jobs:', error);
      setError(error instanceof Error ? error.message : 'Failed to fetch pending jobs');
      setLoading(false);
    }
  };

  // Fetch pending jobs on component mount and every 5 seconds
  useEffect(() => {
    fetchPendingJobs();
    
    const intervalId = setInterval(() => {
      fetchPendingJobs();
    }, 5000);
    
    return () => clearInterval(intervalId);
  }, []);

  // Calculate progress percentage
  const getProgressValue = (job: PendingJob) => {
    if (!job.total_chunks) return 0;
    
    const processedChunks = job.processed_chunks || 0;
    const indexedChunks = job.metadata?.upload_to_index ? (job.indexed_chunks || 0) : processedChunks;
    
    return (indexedChunks / job.total_chunks) * 100;
  };

  // Format date
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString();
    } catch (e) {
      return dateString;
    }
  };

  if (loading) {
    return (
      <Alert>
        <Loader2 className="h-4 w-4 animate-spin" />
        <AlertTitle>Loading pending jobs...</AlertTitle>
      </Alert>
    );
  }

  if (error) {
    return (
      <Alert className="bg-red-50">
        <XCircle className="h-4 w-4 text-red-600" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (pendingJobs.length === 0) {
    return (
      <Alert>
        <CheckCircle2 className="h-4 w-4 text-green-600" />
        <AlertTitle>No pending jobs</AlertTitle>
        <AlertDescription>All documents have been processed.</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-4">
      {pendingJobs.map(job => (
        <Card key={job.id}>
          <CardHeader className="pb-2">
            <CardTitle>{job.metadata?.title || job.filename}</CardTitle>
            <CardDescription>
              Uploaded at {formatDate(job.created_at)}
              {job.metadata?.upload_to_index && " • Will be indexed for search"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="capitalize font-medium">
                  Status: {job.status}
                </span>
                {job.status === 'processing' && (
                  <span className="text-sm text-gray-500">
                    {job.processed_chunks || 0} of {job.total_chunks || 0} chunks processed
                  </span>
                )}
              </div>
              
              {job.status === 'processing' && job.total_chunks > 0 && (
                <Progress value={getProgressValue(job)} className="w-full" />
              )}
              
              {job.error_message && (
                <p className="text-sm text-red-500">{job.error_message}</p>
              )}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
} 