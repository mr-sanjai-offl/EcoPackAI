'use client';

import { useQuery } from '@tanstack/react-query';
import { analyticsService } from '@/services/analytics';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

export function CategoryPieChart() {
  const { data, isLoading } = useQuery({
    queryKey: ['analytics-categories'],
    queryFn: analyticsService.getCategories,
  });

  if (isLoading) {
    return <Skeleton className="h-[400px] w-full rounded-xl" />;
  }

  // Pre-defined color palette for categories
  const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ec4899'];

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Usage by Category</CardTitle>
        <CardDescription>Product categories generating the most requests</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[300px] w-full">
          {(!data || data.length === 0) ? (
            <div className="h-full flex items-center justify-center text-muted-foreground">No data</div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  innerRadius={70}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="count"
                  nameKey="category"
                >
                  {data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: 'var(--card)', borderColor: 'var(--border)', borderRadius: '8px' }}
                />
                <Legend verticalAlign="bottom" height={36} iconType="circle" />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
