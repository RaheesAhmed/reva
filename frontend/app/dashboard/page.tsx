'use client';

import { Suspense, lazy } from 'react';
import { useEffect, useState } from 'react';
import { getUserToken } from '@/lib/auth';
import { Card } from "@/components/ui/card";
import {
  LineChart,
  BarChart,
  Activity,
  MessageSquare,
  Bookmark,
  Bell
} from "lucide-react";
import { 
  BarChart as BarChartComponent,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart as LineChartComponent,
  Line
} from 'recharts';

// Dynamic imports for dashboard components
const StatsCards = lazy(() => import('./components/StatsCards'));
const UsageCharts = lazy(() => import('./components/UsageCharts'));
const RecentActivity = lazy(() => import('./components/RecentActivity'));

interface AnalyticsData {
  tool_usage: Record<string, number>;
  query_timeline: Array<{
    created_at: string;
    tool_used: string;
  }>;
  popular_properties: any[];
  economic_indicators: any[];
}

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

// Loading components for each section
const SectionLoader = () => (
  <Card className="p-6">
    <div className="animate-pulse space-y-4">
      <div className="h-4 bg-muted rounded w-1/4"></div>
      <div className="h-32 bg-muted rounded"></div>
    </div>
  </Card>
);

export default function DashboardPage() {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const token = getUserToken();
        if (!token) {
          throw new Error('Not authenticated');
        }

        const response = await fetch(`${BACKEND_URL}/api/dashboard/analytics`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch analytics data');
        }

        const data = await response.json();
        setAnalyticsData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
        setAnalyticsData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  if (error) {
    return (
      <div className="p-4 bg-destructive/10 text-destructive rounded-lg">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Stats Cards */}
      <Suspense fallback={<SectionLoader />}>
        <StatsCards
          totalQueries={analyticsData?.query_timeline.length || 0}
          activeChats={0}
          savedItems={0}
        />
      </Suspense>

      {/* Charts */}
      <Suspense fallback={<SectionLoader />}>
        <UsageCharts
          toolUsage={analyticsData?.tool_usage || {}}
          queryTimeline={analyticsData?.query_timeline || []}
        />
      </Suspense>

      {/* Recent Activity */}
      <Suspense fallback={<SectionLoader />}>
        <RecentActivity
          activities={analyticsData?.query_timeline || []}
        />
      </Suspense>
    </div>
  );
}