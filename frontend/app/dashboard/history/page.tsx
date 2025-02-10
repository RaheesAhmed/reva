'use client';

import { useEffect, useState } from 'react';
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import {
  MessageSquare,
  ChevronLeft,
  ChevronRight,
  Search
} from "lucide-react";
import { getUserToken } from '@/lib/auth';

interface ChatHistory {
  id: string;
  message: string;
  tool_used: string;
  response: string;
  created_at: string;
  metadata: any;
}

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

export default function HistoryPage() {
  const [history, setHistory] = useState<ChatHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [toolFilter, setToolFilter] = useState<string>('all');

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const token = getUserToken();
      if (!token) {
        throw new Error('Not authenticated');
      }

      const response = await fetch(
        `${BACKEND_URL}/api/dashboard/history?page=${page}&search=${searchTerm}&tool=${toolFilter}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch history');
      }

      const data = await response.json();
      setHistory(data.data || []);
      setTotalPages(Math.ceil((data.total || 0) / data.limit));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setHistory([]);
      setTotalPages(1);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [page, searchTerm, toolFilter]);

  if (loading) {
    return <div className="flex items-center justify-center h-96">Loading...</div>;
  }

  if (error) {
    return (
      <div className="p-4 bg-destructive/10 text-destructive rounded-lg">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold">Chat History</h2>
        <div className="flex gap-4">
          <div className="relative w-64">
            <Input
              placeholder="Search conversations..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
            <Search className="w-4 h-4 absolute left-3 top-3 text-muted-foreground" />
          </div>
          <Select
            value={toolFilter}
            onValueChange={setToolFilter}
          >
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Filter by tool" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Tools</SelectItem>
              <SelectItem value="search">Web Search</SelectItem>
              <SelectItem value="economic-data">Economic Data</SelectItem>
              <SelectItem value="property-analysis">Property Analysis</SelectItem>
              <SelectItem value="market-analysis">Market Analysis</SelectItem>
              <SelectItem value="value-proposition">Value Proposition</SelectItem>
              <SelectItem value="document-search">Document Search</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="space-y-4">
        {history.map((item) => (
          <Card key={item.id} className="p-6">
            <div className="flex items-start gap-4">
              <div className="p-2 bg-blue-100 rounded-lg">
                <MessageSquare className="w-5 h-5 text-blue-500" />
              </div>
              <div className="flex-1 space-y-2">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-medium">{item.tool_used || 'Chat'}</p>
                    <p className="text-sm text-muted-foreground">
                      {new Date(item.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="space-y-2">
                  <p className="text-sm font-medium">Query:</p>
                  <p className="text-sm bg-muted p-3 rounded-lg">{item.message}</p>
                  <p className="text-sm font-medium">Response:</p>
                  <p className="text-sm bg-muted p-3 rounded-lg">{item.response}</p>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Pagination */}
      <div className="flex justify-center items-center gap-4">
        <Button
          variant="outline"
          size="icon"
          onClick={() => setPage(p => Math.max(1, p - 1))}
          disabled={page === 1}
        >
          <ChevronLeft className="w-4 h-4" />
        </Button>
        <span className="text-sm">
          Page {page} of {totalPages}
        </span>
        <Button
          variant="outline"
          size="icon"
          onClick={() => setPage(p => Math.min(totalPages, p + 1))}
          disabled={page === totalPages}
        >
          <ChevronRight className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
} 