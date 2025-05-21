import { API_ERRORS, API_TIMEOUTS } from '../config';

interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

export async function apiRequest<T>(
  url: string,
  options: RequestInit = {},
  timeout: number = API_TIMEOUTS.DEFAULT
): Promise<ApiResponse<T>> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let errorMessage = API_ERRORS.SERVER_ERROR;
      
      switch (response.status) {
        case 401:
          errorMessage = API_ERRORS.UNAUTHORIZED;
          break;
        case 403:
          errorMessage = API_ERRORS.FORBIDDEN;
          break;
        case 404:
          errorMessage = API_ERRORS.NOT_FOUND;
          break;
      }

      return {
        error: errorMessage,
        status: response.status,
      };
    }

    const data = await response.json();
    return {
      data,
      status: response.status,
    };
  } catch (error) {
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        return {
          error: 'Request timed out. Please try again.',
          status: 408,
        };
      }
      if (error.name === 'TypeError') {
        return {
          error: API_ERRORS.NETWORK_ERROR,
          status: 0,
        };
      }
    }
    return {
      error: API_ERRORS.SERVER_ERROR,
      status: 500,
    };
  }
}

// Helper functions for common HTTP methods
export const api = {
  get: <T>(url: string, timeout?: number) => 
    apiRequest<T>(url, { method: 'GET' }, timeout),
  
  post: <T>(url: string, data: any, timeout?: number) =>
    apiRequest<T>(url, {
      method: 'POST',
      body: JSON.stringify(data),
    }, timeout),
  
  put: <T>(url: string, data: any, timeout?: number) =>
    apiRequest<T>(url, {
      method: 'PUT',
      body: JSON.stringify(data),
    }, timeout),
  
  delete: <T>(url: string, timeout?: number) =>
    apiRequest<T>(url, { method: 'DELETE' }, timeout),
}; 