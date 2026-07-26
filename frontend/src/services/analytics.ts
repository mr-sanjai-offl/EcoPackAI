import { apiClient } from './api';
import type { 
  AnalyticsOverview, 
  MaterialFrequency, 
  CategoryBreakdown, 
  DailyTrend 
} from '@/types';

/**
 * Analytics API Service
 * 
 * Encapsulates all calls to the /analytics routes.
 */
export const analyticsService = {
  getOverview: async (): Promise<AnalyticsOverview> => {
    const { data } = await apiClient.get('/analytics/overview');
    return data;
  },

  getMaterials: async (): Promise<MaterialFrequency[]> => {
    const { data } = await apiClient.get('/analytics/materials');
    return data;
  },

  getCategories: async (): Promise<CategoryBreakdown[]> => {
    const { data } = await apiClient.get('/analytics/categories');
    return data;
  },

  getTrends: async (): Promise<DailyTrend[]> => {
    const { data } = await apiClient.get('/analytics/trends');
    return data;
  },
  
  // Note: /export endpoint returns a CSV string, so we handle it differently
  downloadExport: () => {
    // Best practice for file downloads: Let the browser handle the navigation to trigger the download prompt
    window.location.href = `${apiClient.defaults.baseURL}/analytics/export`;
  }
};
