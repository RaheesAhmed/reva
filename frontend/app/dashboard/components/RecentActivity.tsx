'use client';

import { Card } from "@/components/ui/card";
import { Activity } from "lucide-react";

interface RecentActivityProps {
  activities: Array<{
    created_at: string;
    tool_used: string;
  }>;
}

export default function RecentActivity({ activities }: RecentActivityProps) {
  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
      <div className="space-y-4">
        {activities.slice(0, 5).map((item, index) => (
          <div key={index} className="flex items-center gap-4 p-4 bg-muted rounded-lg">
            <Activity className="w-5 h-5 text-blue-500" />
            <div>
              <p className="text-sm font-medium">Used {item.tool_used || 'Unknown Tool'}</p>
              <p className="text-sm text-muted-foreground">
                {new Date(item.created_at).toLocaleString()}
              </p>
            </div>
          </div>
        ))}
        {activities.length === 0 && (
          <div className="text-center text-muted-foreground py-8">
            No recent activity
          </div>
        )}
      </div>
    </Card>
  );
} 