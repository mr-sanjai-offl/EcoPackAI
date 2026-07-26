'use client';

import { KPIOverview } from '@/components/features/analytics/KPIOverview';
import { TrendChart } from '@/components/features/analytics/TrendChart';
import { LayoutDashboard, ArrowRight } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <LayoutDashboard className="h-8 w-8 text-primary" />
            Dashboard
          </h1>
          <p className="text-muted-foreground mt-2">
            Welcome to the EcoPackAI Business Intelligence Platform.
          </p>
        </div>
        
        <Link href="/recommend">
          <Button>
            Run New Inference
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </Link>
      </div>
      
      {/* Reusing our highly-optimized Analytics components for the home dashboard */}
      <KPIOverview />
      
      <div className="grid gap-6 lg:grid-cols-12">
        <div className="lg:col-span-8">
          <TrendChart />
        </div>
        <div className="lg:col-span-4 space-y-6">
          <div className="rounded-xl border bg-card text-card-foreground shadow-sm p-6">
            <h3 className="font-semibold leading-none tracking-tight mb-4">System Status</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">ML API Status</span>
                <span className="flex items-center text-sm font-medium text-emerald-500">
                  <span className="h-2 w-2 rounded-full bg-emerald-500 mr-2 animate-pulse"></span>
                  Operational
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Model Version</span>
                <span className="text-sm font-medium">v1.2.0-xgboost</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Cache Status</span>
                <span className="text-sm font-medium text-emerald-500">Active (60s TTL)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
