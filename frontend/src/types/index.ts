/**
 * Types mapping directly to FastAPI Pydantic schemas.
 * 
 * Industry Best Practice:
 * Always maintain a Single Source of Truth for types. In a real enterprise 
 * environment, these would be auto-generated from the OpenAPI (Swagger) spec 
 * using tools like Orval or OpenAPI-Generator. For now, we manually map them.
 */

// ==========================================
// REQUEST TYPES
// ==========================================
export interface ProductRequest {
  product_weight_kg: number;
  dimensions_cm: {
    length: number;
    width: number;
    height: number;
  };
  category: string;
  sub_category?: string;
  fragile?: boolean;
  food_grade_required?: boolean;
  max_packaging_cost?: number;
  preferred_material_type?: string;
  sustainability_priority?: "high" | "medium" | "low";
  top_n?: number;
}

// ==========================================
// RESPONSE TYPES
// ==========================================
export interface MaterialRecommendation {
  rank: number;
  material_id: string;
  material_name: string;
  overall_score: number;
  confidence: string;
  predicted_cost_per_kg: number;
  predicted_co2_kg: number;
  strength_score: number;
  sustainability_rating: string;
  reason: string;
}

export interface RecommendationResponse {
  status: string;
  model_version: string;
  inference_time_ms: number;
  total_materials_evaluated: number;
  recommendations: MaterialRecommendation[];
}

export interface AnalyticsOverview {
  total_predictions: number;
  total_co2_saved_kg: number;
  total_cost_saved_usd: number;
  average_co2_per_package: number;
  average_cost_per_package: number;
}

export interface MaterialFrequency {
  material_name: string;
  count: number;
}

export interface CategoryBreakdown {
  category: string;
  count: number;
}

export interface DailyTrend {
  date: string;
  predictions: number;
}
