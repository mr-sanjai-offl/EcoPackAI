'use client';

import { useQuery } from '@tanstack/react-query';
import { analyticsService } from '@/services/analytics';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export function MaterialBarChart() {
  const { data, isLoading } = useQuery({
    queryKey: ['analytics-materials'],
    queryFn: analyticsService.getMaterials,
  });

  if (isLoading) {
    return <Skeleton className="h-[400px] w-full rounded-xl" />;
  }

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Top Recommended Materials</CardTitle>
        <CardDescription>Frequency of materials ranked #1 by the ML model</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[300px] w-full mt-4">
          {(!data || data.length === 0) ? (
            <div className="h-full flex items-center justify-center text-muted-foreground">No data</div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data} layout="vertical" margin={{ top: 0, right: 20, left: 20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="var(--border)" />
                <XAxis type="number" hide />
                <YAxis 
                  dataKey="material_name" 
                  type="category" 
                  axisLine={false} 
                  tickLine={false}
                  tick={{ fontSize: 12, fill: "var(--foreground)" }}
                  width={150}
                />
                <Tooltip 
                  cursor={{ fill: 'var(--muted)' }}
                  contentStyle={{ backgroundColor: 'var(--card)', borderColor: 'var(--border)', borderRadius: '8px' }}
                />
                <Bar 
                  dataKey="count" 
                  fill="var(--primary)" 
                  radius={[0, 4, 4, 0]} 
                  barSize={20}
                />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
