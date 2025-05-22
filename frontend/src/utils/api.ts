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
    // Log the full request details
    console.log('=== API Request Debug ===');
    console.log('URL:', url);
    console.log('Method:', options.method || 'GET');
    console.log('Headers:', {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...options.headers,
    });
    console.log('Body:', options.body);
    console.log('=======================');
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'ngrok-skip-browser-warning': 'true',
        ...options.headers,
      },
      credentials: 'include',
      mode: 'cors',
    });

    clearTimeout(timeoutId);
    
    // Log the full response details
    console.log('=== API Response Debug ===');
    console.log('Status:', response.status);
    console.log('Status Text:', response.statusText);
    console.log('Headers:', Object.fromEntries(response.headers.entries()));
    console.log('Type:', response.type);
    console.log('URL:', response.url);
    console.log('=======================');

    // Check content type before proceeding
    const contentType = response.headers.get('content-type');
    console.log('Response Content-Type:', contentType);

    if (!response.ok) {
      let errorMessage = API_ERRORS.SERVER_ERROR;
      let errorData: any = null;
      
      // Try to parse response as JSON first
      try {
        const responseText = await response.text();
        console.log('Error Response Text:', responseText);
        
        try {
          errorData = JSON.parse(responseText);
          console.log('Error Response Data:', errorData);
        } catch (e) {
          console.log('Response is not JSON:', e);
          // If it's HTML, log a warning
          if (contentType?.includes('text/html')) {
            console.warn('Received HTML response instead of JSON');
            errorMessage = 'Server returned HTML instead of JSON response';
          }
        }
      } catch (e) {
        console.error('Failed to read response:', e);
      }
      
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

      console.error('API Request Failed:', {
        status: response.status,
        statusText: response.statusText,
        error: errorMessage,
        contentType,
        errorData
      });

      return {
        error: errorMessage,
        status: response.status,
      };
    }

    // For successful responses, ensure we have JSON
    if (!contentType || !contentType.includes('application/json')) {
      console.error('Unexpected content type:', contentType);
      const text = await response.text();
      console.error('Response text:', text);
      return {
        error: `Server returned unexpected content type: ${contentType}`,
        status: response.status,
      };
    }

    const data = await response.json();
    console.log('Response Data:', data);
    
    return {
      data,
      status: response.status,
    };
  } catch (error) {
    console.error('API Request Error:', error);
    
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