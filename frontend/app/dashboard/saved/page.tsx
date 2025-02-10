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
import {
  Bookmark,
  Tag,
  Trash2,
  Search
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { getUserToken } from '@/lib/auth';

interface SavedItem {
  id: string;
  title: string;
  item_type: string;
  content: any;
  tags: string[];
  created_at: string;
}

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

export default function SavedItemsPage() {
  const [items, setItems] = useState<SavedItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('all');

  const fetchSavedItems = async () => {
    try {
      setLoading(true);
      const token = getUserToken();
      if (!token) {
        throw new Error('Not authenticated');
      }

      const response = await fetch(
        `${BACKEND_URL}/api/dashboard/saved-items${typeFilter !== 'all' ? `?item_type=${typeFilter}` : ''}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch saved items');
      }

      const data = await response.json();
      setItems(data.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const deleteItem = async (id: string) => {
    try {
      const token = getUserToken();
      if (!token) {
        throw new Error('Not authenticated');
      }

      const response = await fetch(`${BACKEND_URL}/api/dashboard/saved-items/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to delete item');
      }

      // Remove item from state
      setItems(items.filter(item => item.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  useEffect(() => {
    fetchSavedItems();
  }, [typeFilter]);

  const filteredItems = items.filter(item =>
    item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (item.tags && item.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase())))
  );

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
        <h2 className="text-3xl font-bold">Saved Items</h2>
        <div className="flex gap-4">
          <div className="relative w-64">
            <Input
              placeholder="Search saved items..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
            <Search className="w-4 h-4 absolute left-3 top-3 text-muted-foreground" />
          </div>
          <Select
            value={typeFilter}
            onValueChange={setTypeFilter}
          >
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Filter by type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="property">Properties</SelectItem>
              <SelectItem value="analysis">Analysis</SelectItem>
              <SelectItem value="document">Documents</SelectItem>
              <SelectItem value="search">Search Results</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredItems.map((item) => (
          <Card key={item.id} className="p-6">
            <div className="flex flex-col h-full">
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-2">
                  <Bookmark className="w-5 h-5 text-blue-500" />
                  <h3 className="font-semibold">{item.title}</h3>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => deleteItem(item.id)}
                  className="text-destructive hover:text-destructive/90"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>

              <div className="flex-1 mb-4">
                <p className="text-sm text-muted-foreground mb-2">
                  {new Date(item.created_at).toLocaleDateString()}
                </p>
                <div className="bg-muted rounded-lg p-3">
                  <pre className="text-sm whitespace-pre-wrap">
                    {JSON.stringify(item.content, null, 2)}
                  </pre>
                </div>
              </div>

              {item.tags && item.tags.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {item.tags.map((tag, index) => (
                    <div
                      key={index}
                      className="flex items-center gap-1 text-xs bg-secondary px-2 py-1 rounded-full"
                    >
                      <Tag className="w-3 h-3" />
                      <span>{tag}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </Card>
        ))}
      </div>

      {filteredItems.length === 0 && (
        <div className="text-center py-12">
          <Bookmark className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium mb-2">No saved items found</h3>
          <p className="text-muted-foreground">
            {searchTerm || typeFilter !== 'all'
              ? "Try adjusting your search or filters"
              : "Start saving items to see them here"}
          </p>
        </div>
      )}
    </div>
  );
} 