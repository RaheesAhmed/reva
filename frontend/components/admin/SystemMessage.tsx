'use client';

import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle, Save } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

export function SystemMessage() {
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    fetchSystemMessage();
  }, []);

  const fetchSystemMessage = async () => {
    try {
      setError(null);
      const response = await fetch(`${BACKEND_URL}/admin/system-message`);
      if (!response.ok) throw new Error('Failed to fetch system message');
      const data = await response.json();
      setMessage(data.message);
    } catch (error) {
      const errorMessage = 'Failed to load system message';
      setError(errorMessage);
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const saveSystemMessage = async () => {
    setSaving(true);
    setError(null);
    try {
      const response = await fetch(`${BACKEND_URL}/api/admin/system-message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save system message');
      }
      
      // Refresh the message to get the latest version
      await fetchSystemMessage();
      
      toast({
        title: "Success",
        description: "System message updated successfully",
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to save system message';
      setError(errorMessage);
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <Skeleton className="h-8 w-[200px] mb-2" />
          <Skeleton className="h-4 w-[300px]" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-[200px] w-full" />
        </CardContent>
        <CardFooter>
          <Skeleton className="h-10 w-[100px] ml-auto" />
        </CardFooter>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-2xl font-bold">System Message</CardTitle>
        <CardDescription className="text-muted-foreground">
          Configure the system message that guides the AI assistant's behavior and capabilities.
          This message sets the context and boundaries for all AI interactions.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        <Textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Enter system message..."
          className="min-h-[300px] font-mono text-sm"
        />
      </CardContent>
      <CardFooter className="flex justify-between items-center">
        <p className="text-sm text-muted-foreground">
          Last updated: {new Date().toLocaleDateString()}
        </p>
        <Button 
          onClick={saveSystemMessage} 
          disabled={saving}
          className="ml-auto"
          size="lg"
        >
          {saving ? (
            <>
              <span className="animate-pulse">Saving...</span>
            </>
          ) : (
            <>
              <Save className="mr-2 h-4 w-4" />
              Save Changes
            </>
          )}
        </Button>
      </CardFooter>
    </Card>
  );
}
