'use client';

import { useState } from 'react';
import { RecommendForm } from '@/components/features/recommend/RecommendForm';
import { RecommendationResults } from '@/components/features/recommend/RecommendationResults';
import { useMutation } from '@tanstack/react-query';
import { recommendationService } from '@/services/recommendation';
import type { ProductRequest, RecommendationResponse } from '@/types';
import { PackageSearch } from 'lucide-react';

export default function RecommendPage() {
  const [results, setResults] = useState<RecommendationResponse | null>(null);

  // TanStack Query useMutation for the POST request
  const { mutate, isPending, error } = useMutation({
    mutationFn: (data: ProductRequest) => recommendationService.getRecommendations(data),
    onSuccess: (data) => {
      setResults(data);
    },
  });

  const onSubmit = (data: ProductRequest) => {
    mutate(data);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <PackageSearch className="h-8 w-8 text-primary" />
          AI Material Engine
        </h1>
        <p className="text-muted-foreground mt-2">
          Input your product specifications to receive ML-ranked sustainable packaging recommendations.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-12 items-start">
        <div className="lg:col-span-4 space-y-6">
          <RecommendForm onSubmit={onSubmit} isLoading={isPending} />
        </div>
        
        <div className="lg:col-span-8">
          {error ? (
            <div className="p-6 bg-destructive/10 border border-destructive text-destructive rounded-xl">
              <h3 className="font-semibold">Inference Error</h3>
              <p className="text-sm mt-1">{error.message}</p>
            </div>
          ) : results ? (
            <RecommendationResults data={results} />
          ) : (
            <div className="h-[600px] rounded-xl border border-dashed flex flex-col items-center justify-center text-muted-foreground bg-muted/5 p-8 text-center">
              <PackageSearch className="h-12 w-12 mb-4 opacity-20" />
              <h3 className="font-medium text-lg text-foreground">Awaiting Input</h3>
              <p className="max-w-sm mt-2">
                Fill out the product specifications form and click generate to see AI packaging recommendations.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
