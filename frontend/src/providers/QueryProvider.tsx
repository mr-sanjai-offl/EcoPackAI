'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';

/**
 * TanStack Query Provider
 * 
 * Must be a Client Component ('use client') because QueryClient uses React Context 
 * under the hood, which isn't supported in Next.js Server Components.
 */
export function QueryProvider({ children }: { children: React.ReactNode }) {
  // We initialize the client in state so it doesn't get recreated on every render
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // How long data is considered "fresh" before triggering a background refetch
            staleTime: 60 * 1000, 
            // Don't refetch on window focus automatically (can be annoying in dashboards)
            refetchOnWindowFocus: false,
            // Retry failed requests once before showing an error
            retry: 1,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
