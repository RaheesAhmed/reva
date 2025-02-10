'use client';

import { Card } from "@/components/ui/card";
import { Activity, MessageSquare, Bookmark } from "lucide-react";

interface StatsCardsProps {
  totalQueries: number;
  activeChats: number;
  savedItems: number;
}

export default function StatsCards({ totalQueries, activeChats, savedItems }: StatsCardsProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card className="p-6">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-blue-100 rounded-lg">
            <Activity className="w-6 h-6 text-blue-500" />
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Total Queries</p>
            <h3 className="text-2xl font-bold">{totalQueries}</h3>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-green-100 rounded-lg">
            <MessageSquare className="w-6 h-6 text-green-500" />
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Active Chats</p>
            <h3 className="text-2xl font-bold">{activeChats}</h3>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-yellow-100 rounded-lg">
            <Bookmark className="w-6 h-6 text-yellow-500" />
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Saved Items</p>
            <h3 className="text-2xl font-bold">{savedItems}</h3>
          </div>
        </div>
      </Card>
    </div>
  );
} 