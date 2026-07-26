'use client';

import { FileText, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { analyticsService } from '@/services/analytics';

export default function ReportsPage() {
  const handleExport = () => {
    analyticsService.downloadExport();
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <FileText className="h-8 w-8 text-primary" />
          Sustainability Reports
        </h1>
        <p className="text-muted-foreground mt-2">
          Generate and download compliance and executive summary reports.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Executive Summary</CardTitle>
            <CardDescription>
              Complete CSV export of the last 1,000 AI recommendations, 
              including carbon footprint and cost projections.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={handleExport} className="w-full">
              <Download className="mr-2 h-4 w-4" />
              Download CSV
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
