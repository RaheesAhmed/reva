'use client';

import { Card } from "@/components/ui/card";
import {
  BarChart as BarChartComponent,
  LineChart as LineChartComponent,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

interface UsageChartsProps {
  toolUsage: Record<string, number>;
  queryTimeline: Array<{
    created_at: string;
    tool_used: string;
  }>;
}

export default function UsageCharts({ toolUsage, queryTimeline }: UsageChartsProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      {/* Tool Usage Chart */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Tool Usage</h3>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChartComponent
              data={Object.entries(toolUsage).map(([key, value]) => ({
                name: key,
                value: value
              }))}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#3b82f6" />
            </BarChartComponent>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Query Timeline Chart */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Query Timeline</h3>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChartComponent
              data={queryTimeline.map(item => ({
                date: new Date(item.created_at).toLocaleDateString(),
                queries: 1
              }))}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="queries" stroke="#3b82f6" />
            </LineChartComponent>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  );
} 