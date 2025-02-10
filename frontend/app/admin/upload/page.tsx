'use client';

import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Upload, Trash2, FileText, AlertCircle, FolderOpen } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { apiClient } from '@/lib/api-client';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"

interface Document {
  id: string;
  name: string;
  type: string;
  size: number;
  uploaded_at: string;
  status: 'processing' | 'completed' | 'failed';
  vector_count?: number;
  error?: string;
}

export default function UploadPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    let retryCount = 0;
    const maxRetries = 3;

    const tryLoadDocuments = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const docs = await apiClient.listDocuments();
        setDocuments(docs || []);
      } catch (error) {
        console.error('Error loading documents:', error);
        
        // If we haven't exceeded max retries and it's not a cancellation
        if (retryCount < maxRetries && error instanceof Error && !error.message.includes('cancelled')) {
          retryCount++;
          console.log(`Retrying (${retryCount}/${maxRetries})...`);
          await new Promise(resolve => setTimeout(resolve, 1000 * retryCount));
          return tryLoadDocuments();
        }
        
        setError('Failed to load documents. Please try again later.');
        toast({
          title: "Error",
          description: error instanceof Error ? error.message : "Failed to load documents",
          variant: "destructive",
        });
      } finally {
        setIsLoading(false);
      }
    };

    await tryLoadDocuments();
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files?.length) return;

    const file = files[0];
    const maxSize = 10 * 1024 * 1024; // 10MB

    if (file.size > maxSize) {
      toast({
        title: "Error",
        description: "File size must be less than 10MB",
        variant: "destructive",
      });
      return;
    }

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      await apiClient.uploadDocument(formData);
      toast({
        title: "Success",
        description: "Document uploaded successfully",
      });
      loadDocuments(); // Refresh the list
    } catch (error) {
      console.error('Upload error:', error);
      toast({
        title: "Error",
        description: "Failed to upload document. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
      // Reset the input
      event.target.value = '';
    }
  };



  

  return (
    <div className="container mx-auto py-8 space-y-8">
      <Card>
        <CardHeader>
          <CardTitle>Upload Documents</CardTitle>
          <CardDescription>
            Upload documents to be used as knowledge base for the AI assistant.
            Supported formats: PDF, DOCX, TXT (Max size: 10MB)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <Input
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={handleFileUpload}
              disabled={isUploading}
              className="hidden"
              id="file-upload"
            />
            <Label
              htmlFor="file-upload"
              className="cursor-pointer flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Upload className="h-4 w-4" />
              {isUploading ? 'Uploading...' : 'Upload File'}
            </Label>
          </div>
        </CardContent>
      </Card>

      
    </div>
  );
}
