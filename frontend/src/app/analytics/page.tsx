'use client';

import { BarChart3 } from 'lucide-react';
import { KPIOverview } from '@/components/features/analytics/KPIOverview';
import { TrendChart } from '@/components/features/analytics/TrendChart';
import { CategoryPieChart } from '@/components/features/analytics/CategoryPieChart';
import { MaterialBarChart } from '@/components/features/analytics/MaterialBarChart';

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <BarChart3 className="h-8 w-8 text-primary" />
            Executive Dashboard
          </h1>
          <p className="text-muted-foreground mt-2">
            Business Intelligence overview of AI-driven sustainability metrics.
          </p>
        </div>
      </div>

      {/* Top Level KPIs */}
      <KPIOverview />

      {/* Main Charts Area */}
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="lg:col-span-2">
          <TrendChart />
        </div>
        
        <div className="lg:col-span-1">
          <CategoryPieChart />
        </div>
        
        <div className="lg:col-span-1">
          <MaterialBarChart />
        </div>
      </div>
    </div>
  );
}
