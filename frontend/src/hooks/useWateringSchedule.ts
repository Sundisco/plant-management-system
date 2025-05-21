import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { WateringSchedule } from '../types/Plant';
import { API_ENDPOINTS } from '../config';

const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes in milliseconds

interface CacheEntry {
  data: WateringSchedule[];
  timestamp: number;
}

const scheduleCache: { [key: string]: CacheEntry } = {};

export const useWateringSchedule = () => {
  const { user } = useAuth();
  const [schedule, setSchedule] = useState<WateringSchedule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSchedule = useCallback(async () => {
    if (!user) return;

    try {
      setLoading(true);
      setError(null);

      // Check cache first
      const cacheKey = `schedule_${user.id}`;
      const cachedData = scheduleCache[cacheKey];
      const now = Date.now();

      if (cachedData && now - cachedData.timestamp < CACHE_DURATION) {
        setSchedule(cachedData.data);
        setLoading(false);
        return;
      }

      // Fetch new data if cache is expired or doesn't exist
      const response = await fetch(`${API_ENDPOINTS.BASE_URL}${API_ENDPOINTS.WATERING_SCHEDULE(user.id)}`);
      if (!response.ok) {
        throw new Error('Failed to fetch watering schedule');
      }

      const data = await response.json();
      
      // Update cache
      scheduleCache[cacheKey] = {
        data,
        timestamp: now
      };

      setSchedule(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      // If we have cached data, use it even if expired
      const cacheKey = `schedule_${user.id}`;
      const cachedData = scheduleCache[cacheKey];
      if (cachedData) {
        setSchedule(cachedData.data);
      }
    } finally {
      setLoading(false);
    }
  }, [user]);

  // Refresh cache periodically
  useEffect(() => {
    if (!user) return;

    const interval = setInterval(() => {
      fetchSchedule();
    }, CACHE_DURATION);

    return () => clearInterval(interval);
  }, [user, fetchSchedule]);

  // Initial fetch
  useEffect(() => {
    fetchSchedule();
  }, [fetchSchedule]);

  const refreshSchedule = useCallback(() => {
    if (user) {
      // Clear cache for this user
      const cacheKey = `schedule_${user.id}`;
      delete scheduleCache[cacheKey];
      fetchSchedule();
    }
  }, [user, fetchSchedule]);

  return {
    schedule,
    loading,
    error,
    refreshSchedule
  };
}; 