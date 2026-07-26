import { apiClient } from './api';
import type { ProductRequest, RecommendationResponse } from '@/types';

/**
 * Recommendation API Service
 */
export const recommendationService = {
  getRecommendations: async (requestData: ProductRequest): Promise<RecommendationResponse> => {
    const { data } = await apiClient.post('/recommend', requestData);
    return data;
  }
};
