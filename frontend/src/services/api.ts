import axios from 'axios';

/**
 * Base Axios Instance
 * 
 * Industry Best Practice:
 * Never scatter `axios.get('http://localhost...')` throughout your components.
 * By centralizing the instance here, we can:
 * 1. Change the baseURL based on environment variables (.env)
 * 2. Add request interceptors (e.g., automatically attach JWT auth tokens)
 * 3. Add response interceptors (e.g., globally handle 401 Unauthorized errors)
 */
export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  // 10 second timeout because ML inference could take a moment in edge cases
  timeout: 10000, 
});

// Example of a global response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // We could trigger a toast notification here globally
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);
