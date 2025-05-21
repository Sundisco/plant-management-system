import { useState, useEffect } from 'react';
import { useAuth } from './useAuth';
import { WateringSchedule } from '../types/watering';
import { API_ENDPOINTS } from '../config';

const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes in milliseconds

interface CacheEntry {
  data: WateringSchedule[];
  timestamp: number;
}

const scheduleCache: { [key: string]: CacheEntry } = {};

export const useWateringSchedule = (sectionId?: number) => {
  const { user } = useAuth();
  const [schedule, setSchedule] = useState<WateringSchedule>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSchedule = async () => {
      if (!user?.id) return;
      try {
        const response = await fetch(`${API_ENDPOINTS.BASE_URL}${API_ENDPOINTS.WATERING_SCHEDULE(user.id)}`);
        if (!response.ok) throw new Error('Failed to fetch watering schedule');
        const data = await response.json();
        setSchedule(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch watering schedule');
      } finally {
        setLoading(false);
      }
    };

    fetchSchedule();
  }, [user?.id, sectionId]);

  return { schedule, loading, error };
}; 