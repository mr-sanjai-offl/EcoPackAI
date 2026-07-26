'use client';

import { useQuery } from '@tanstack/react-query';
import { analyticsService } from '@/services/analytics';
import { Card, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Activity, Leaf, DollarSign, Package } from 'lucide-react';

export function KPIOverview() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['analytics-overview'],
    queryFn: analyticsService.getOverview,
  });

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <Skeleton key={i} className="h-32 rounded-xl" />
        ))}
      </div>
    );
  }

  if (isError || !data) {
    return <div className="text-destructive">Failed to load KPIs.</div>;
  }

  const kpis = [
    {
      title: "Total Predictions",
      value: data.total_predictions.toLocaleString(),
      icon: <Activity className="h-4 w-4 text-muted-foreground" />,
      subtext: "Since inception",
    },
    {
      title: "Total CO₂ Saved",
      value: `${data.total_co2_saved_kg.toLocaleString()} kg`,
      icon: <Leaf className="h-4 w-4 text-emerald-500" />,
      subtext: "vs standard plastic baseline",
    },
    {
      title: "Cost Savings",
      value: `$${data.total_cost_saved_usd.toLocaleString()}`,
      icon: <DollarSign className="h-4 w-4 text-amber-500" />,
      subtext: "Estimated material cost reduction",
    },
    {
      title: "Avg CO₂ / Package",
      value: `${data.average_co2_per_package} kg`,
      icon: <Package className="h-4 w-4 text-blue-500" />,
      subtext: "Across all recommended materials",
    }
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {kpis.map((kpi, i) => (
        <Card key={i} className="bg-card">
          <CardContent className="p-6 flex flex-col justify-between h-full">
            <div className="flex flex-row items-center justify-between pb-2 space-y-0">
              <h3 className="tracking-tight text-sm font-medium">{kpi.title}</h3>
              {kpi.icon}
            </div>
            <div>
              <div className="text-2xl font-bold">{kpi.value}</div>
              <p className="text-xs text-muted-foreground mt-1">{kpi.subtext}</p>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
