import { useState, useEffect, useCallback, useRef } from 'react';
import { Box, Paper, Typography, CircularProgress, Card, CardContent, Avatar, IconButton, Tooltip, Grid, Button, Divider, Chip, useTheme, Popover, Snackbar, Alert } from '@mui/material';
import { format, addDays, isAfter, isBefore, differenceInDays } from 'date-fns';
import { API_ENDPOINTS } from '../config';
import { Plant } from '../types/Plant';
import { PlantDetails } from './Garden/PlantDetails';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WaterDropIcon from '@mui/icons-material/WaterDrop';
import { useGarden } from '../contexts/GardenContext';
import RestoreIcon from '@mui/icons-material/Restore';
import SunnyIcon from '@mui/icons-material/WbSunny';
import RainyIcon from '@mui/icons-material/WbCloudy';
import HotIcon from '@mui/icons-material/Thermostat';
import ColdIcon from '@mui/icons-material/Thermostat';
import WindyIcon from '@mui/icons-material/WbTwilight';
import ThermometerIcon from '@mui/icons-material/Thermostat';
import DropletIcon from '@mui/icons-material/Water';
import WindIcon from '@mui/icons-material/WbTwilight';
import './WateringSchedule.css'; // For custom styles

interface Section {
  id: number;
  section_id: string;
  name: string;
  user_id: number;
  glyph: string;
}

interface WeatherData {
  temperature: number;
  precipitation: number;
  wind_speed: number;
  weather_icons: string[];
}

interface WateringSection {
  section: string;
  groups: Array<{
    plants: Array<{
      plant_id: number;
      plant_name: string;
      image_url: string;
      watering_info: {
        frequency_days: number;
        depth_mm: number;
        volume_feet: number;
      };
      last_watered: string | null;
      is_watered: boolean;
      weather_adjusted: boolean;
      next_watering: string;
      weather_info: {
        is_adjusted: boolean;
        original_date: string | null;
      };
    }>;
  }>;
  watering_stats: {
    total_plants: number;
    watered_plants: number;
    percentage: number;
  };
}

interface DaySchedule {
  date: string;
  sections: WateringSection[];
  weather: WeatherData;
}

interface WateringScheduleResponse {
  schedule: DaySchedule[];
  last_updated: string;
}

interface WateringSchedule {
  plant_id: number;
  plant_name: string;
  last_watered?: string;
  next_watering: string;
  section: string;
  watering_frequency: number;
  image_url?: string;
  schedule_id?: string;
  date?: string;
  weather?: WeatherData;
  weather_adjusted: boolean;
  weather_info: {
    is_adjusted: boolean;
    original_date: string | null;
  };
}

interface WateringGroup {
  frequency: number;
  plants: WateringSchedule[];
  nextWatering: string;
}

interface WateringScheduleProps {
  sectionId?: number;
  sections: {
    id: number;
    section_id: string;
    name: string;
    user_id: number;
    glyph: string;
    created_at?: string;
    updated_at?: string;
  }[];
  isNextWeek: boolean;
  setIsNextWeek: (val: boolean) => void;
}

interface SectionStats {
  totalPlants: number;
  plantsByDay: {
    [date: string]: {
      count: number;
      plants: WateringSchedule[];
      overdue: number;
      dueSoon: number;
    };
  };
}

const WeatherDisplay: React.FC<{ weather: WeatherData | undefined }> = ({ weather }) => {
  if (!weather) return null;

  // Lower threshold to 30°C
  const isHot = weather.temperature >= 30;

  const getWeatherIcon = (icon: string) => {
    const iconStyle = {
      fontSize: '1.2rem',
      transition: 'all 0.2s ease',
      verticalAlign: 'middle',
      // No background, border, or container
    };
    switch (icon) {
      case "sunny":
        return <SunnyIcon sx={{ ...iconStyle, color: '#FFB300' }} />;
      case "rainy":
        return <RainyIcon sx={{ ...iconStyle, color: '#42A5F5' }} />;
      case "hot":
        return <HotIcon sx={{ ...iconStyle, color: '#EF5350' }} />;
      case "cold":
        return <ColdIcon sx={{ ...iconStyle, color: '#90CAF9' }} />;
      case "windy":
        return <WindyIcon sx={{ ...iconStyle, color: '#78909C' }} />;
      default:
        return <SunnyIcon sx={{ ...iconStyle, color: '#FFB300' }} />;
    }
  };

  const getWeatherIcons = () => {
    if (weather.weather_icons && weather.weather_icons.length > 0) {
      return weather.weather_icons;
    }
    const icons = [];
    if (weather.precipitation > 0) {
      icons.push("rainy");
    } else if (weather.temperature > 25) {
      icons.push("hot");
    } else if (weather.temperature < 10) {
      icons.push("cold");
    } else if (weather.wind_speed > 15) {
      icons.push("windy");
    } else {
      icons.push("sunny");
    }
    return icons;
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', position: 'relative', p: 0, m: 0, background: 'none', border: 'none', boxShadow: 'none' }}>
      <Tooltip
        title={
          <Box sx={{ p: 1 }}>
            <Typography variant="subtitle2" sx={{ mb: 1 }}>Weather Details</Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <ThermometerIcon sx={{ fontSize: '1rem', color: '#EF5350' }} />
                <Typography variant="body2">Temperature: {weather.temperature}°C</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <DropletIcon sx={{ fontSize: '1rem', color: '#42A5F5' }} />
                <Typography variant="body2">Precipitation: {weather.precipitation}mm</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <WindIcon sx={{ fontSize: '1rem', color: '#78909C' }} />
                <Typography variant="body2">Wind: {weather.wind_speed}m/s</Typography>
              </Box>
            </Box>
          </Box>
        }
        arrow
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, p: 0, m: 0, background: 'none', border: 'none', boxShadow: 'none' }}>
          {getWeatherIcons().filter(icon => icon !== 'hot').map((icon, index) => (
            <span key={index} style={{ display: 'inline-flex', alignItems: 'center', background: 'none', border: 'none', boxShadow: 'none', padding: 0, margin: 0 }}>
              {getWeatherIcon(icon)}
            </span>
          ))}
          <Typography 
            variant="body2" 
            sx={{ fontWeight: 500, color: 'text.primary', ml: 0.5 }}
          >
            {weather.temperature}°C
          </Typography>
        </Box>
      </Tooltip>
      {isHot && (
        <Tooltip
          title={
            <Box sx={{ p: 1 }}>
              <Typography variant="subtitle2" color="error.main" sx={{ mb: 1 }}>Hot Weather Alert</Typography>
              <Typography variant="body2">
                Due to high temperatures, all future waterings have been moved earlier to protect plants from heat stress.
              </Typography>
            </Box>
          }
          arrow
        >
          <Box sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: 24,
            height: 24,
            borderRadius: '50%',
            bgcolor: '#EF5350',
            color: 'white',
            fontSize: '1.1rem',
            ml: 1,
            boxShadow: '0 2px 8px rgba(239,83,80,0.15)',
            position: 'absolute',
            top: -10,
            right: -10,
            border: '2px solid #fff',
            zIndex: 2
          }}>
            <span role="img" aria-label="hot">🔥</span>
          </Box>
        </Tooltip>
      )}
    </Box>
  );
};

const WateringSchedule: React.FC<WateringScheduleProps> = ({ sectionId, sections, isNextWeek, setIsNextWeek }) => {
  const theme = useTheme();
  const { plants, lastUpdated } = useGarden();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [scheduleData, setScheduleData] = useState<WateringSchedule[]>([]);
  const [rawScheduleData, setRawScheduleData] = useState<WateringScheduleResponse | null>(null);
  const [selectedPlant, setSelectedPlant] = useState<Plant | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedDay, setSelectedDay] = useState<string | null>(null);
  const [selectedSection, setSelectedSection] = useState<string | null>(null);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'warning';
  }>({
    open: false,
    message: '',
    severity: 'success'
  });

  // Generate 7 days for the grid, starting from today or next week
  const gridDays = Array.from({ length: 7 }, (_, i) => 
    addDays(new Date(), isNextWeek ? i + 7 : i)
  );

  // Add a debounce function at the top of the component
  const debounce = (func: Function, wait: number) => {
    let timeout: NodeJS.Timeout;
    return (...args: any[]) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func(...args), wait);
    };
  };

  // Add a ref to track schedule data changes
  const scheduleDataRef = useRef<WateringSchedule[]>([]);

  // Update the refreshSchedule function
  const refreshSchedule = useCallback(async () => {
    try {
      setLoading(true);
      const userId = 1; // TODO: Get from auth context
      console.log('Refreshing watering schedule for user:', userId);
      const response = await fetch(`${API_ENDPOINTS.BASE_URL}/api/watering-schedule/watering-schedule/user/${userId}`);
      const data: WateringScheduleResponse = await response.json();
      console.log('Raw API Response:', data);
      
      // Store the raw schedule data
      setRawScheduleData(data);
      
      if (data?.schedule && Array.isArray(data.schedule)) {
        // Transform the nested schedule data into a flat array of plants
        const transformedData: WateringSchedule[] = [];
        
        data.schedule.forEach(daySchedule => {
          console.log('Processing day schedule:', daySchedule.date);
          daySchedule.sections.forEach(section => {
            console.log('Processing section:', section.section);
            section.groups.forEach(group => {
              console.log('Processing group:', group);
              group.plants.forEach(plant => {
                // Find the section name from the sections prop
                const sectionInfo = sections.find(s => s.section_id === section.section);
                const sectionName = sectionInfo ? sectionInfo.name : 'Unassigned';
                
                // Create plant data with weather information
                const plantData: WateringSchedule = {
                  plant_id: plant.plant_id,
                  plant_name: plant.plant_name,
                  next_watering: daySchedule.date,
                  section: sectionName,
                  watering_frequency: plant.watering_info.frequency_days,
                  image_url: plant.image_url,
                  date: daySchedule.date,
                  weather: daySchedule.weather,
                  weather_adjusted: plant.weather_adjusted,
                  weather_info: plant.weather_info
                };

                // Add last_watered if it exists
                if (plant.last_watered) {
                  plantData.last_watered = plant.last_watered;
                }

                // Add to transformed data
                transformedData.push(plantData);
                console.log('Added plant to schedule:', plantData);
              });
            });
          });
        });

        // Sort plants by next_watering date
        transformedData.sort((a, b) => 
          new Date(a.next_watering).getTime() - new Date(b.next_watering).getTime()
        );

        console.log('Final transformed schedule data:', transformedData);
        // Only update if we have data or if we don't have any local data
        if (transformedData.length > 0 || scheduleDataRef.current.length === 0) {
          setScheduleData(transformedData);
          scheduleDataRef.current = transformedData;
        }
      } else {
        console.log('No schedule data in response or invalid format');
        // Don't clear the schedule data if we have local changes
        if (scheduleDataRef.current.length === 0) {
          setScheduleData([]);
        }
      }
      setError(null);
      } catch (err) {
      console.error('Error refreshing watering schedule:', err);
      // Don't clear the schedule data on error
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
    }
  }, [sections]);

  // Create a debounced version of refreshSchedule
  const debouncedRefresh = useCallback(
    debounce(() => {
      refreshSchedule();
    }, 1000),
    [refreshSchedule]
  );

  // Update the periodic refresh to use the debounced version
  useEffect(() => {
    // Initial refresh
    refreshSchedule();

    // Set up periodic refresh (every 5 minutes instead of 30 seconds)
    const interval = setInterval(() => {
      console.log('Periodic schedule refresh');
      debouncedRefresh();
    }, 300000); // 5 minutes

    return () => clearInterval(interval);
  }, [debouncedRefresh]);

  // Refresh when garden plants change - make this immediate
  useEffect(() => {
    if (lastUpdated) {
      console.log('Garden plants updated, refreshing schedule immediately');
      refreshSchedule(); // Call directly without debounce for immediate updates
    }
  }, [lastUpdated, refreshSchedule]);

  // Add effect to log schedule data changes
  useEffect(() => {
    console.log('Schedule data updated:', scheduleData);
  }, [scheduleData]);

  // Update the handleMarkAsWatered function to use the ref
  const handleMarkAsWatered = async (plant: WateringSchedule) => {
    try {
      const today = format(new Date(), 'yyyy-MM-dd');
      console.log('Marking plant as watered:', plant);
      
      // First, get the current schedule ID
      const scheduleResponse = await fetch(`${API_ENDPOINTS.BASE_URL}/api/watering-schedule/user/1/plant/${plant.plant_id}`, {
        headers: {
          'Accept': 'application/json',
        },
        credentials: 'include'
      });
      
      if (!scheduleResponse.ok) {
        throw new Error('Failed to fetch watering schedule');
      }
      const scheduleData = await scheduleResponse.json();
      console.log('Schedule data for plant:', scheduleData);
      
      // Sort schedules by date and find the most recent uncompleted schedule
      const sortedSchedules = scheduleData.sort((a: any, b: any) => 
        new Date(b.scheduled_date).getTime() - new Date(a.scheduled_date).getTime()
      );
      
      const currentSchedule = sortedSchedules.find((schedule: { 
        scheduled_date: string;
        completed: boolean;
      }) => !schedule.completed);

      if (!currentSchedule) {
        throw new Error('No active watering schedule found');
      }

      console.log('Found schedule to update:', currentSchedule);

      // Update the watering schedule with batch_update flag
      const response = await fetch(`${API_ENDPOINTS.BASE_URL}/api/watering-schedule/${currentSchedule.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ 
          completed: true,
          completion_timestamp: new Date().toISOString(),
          batch_update: true  // Add this flag to prevent immediate weather adjustments
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update watering date');
      }

      console.log('Successfully updated current schedule');

      // Update local state immediately to show the change
      setScheduleData(prevData => {
        const updatedData = prevData.map(p => {
          if (p.plant_id === plant.plant_id && p.next_watering === today) {
            return {
              ...p,
              last_watered: today,
              is_watered: true
            };
          }
          return p;
        });
        scheduleDataRef.current = updatedData;
        return updatedData;
      });

      // Show success feedback
      setSnackbar({
        open: true,
        message: `Successfully marked ${plant.plant_name} as watered`,
        severity: 'success'
      });

      // Close the popover after successful update
      handleClosePopover();

      // Refresh the schedule data after a short delay to allow for batch processing
      setTimeout(() => {
        refreshSchedule();
      }, 1000);
    } catch (error) {
      console.error('Error marking plant as watered:', error);
      setSnackbar({
        open: true,
        message: error instanceof Error ? error.message : 'Failed to update watering status',
        severity: 'error'
      });
    }
  };

  // Add reset function
  const handleResetWatering = async (plant: WateringSchedule) => {
    try {
      console.log('Resetting watering status for plant:', plant);
      
      // Get the current schedule
      const scheduleResponse = await fetch(`${API_ENDPOINTS.BASE_URL}/api/watering-schedule/user/1/plant/${plant.plant_id}`, {
        headers: {
          'Accept': 'application/json',
        },
        credentials: 'include'
      });
      
      if (!scheduleResponse.ok) {
        throw new Error('Failed to fetch watering schedule');
      }
      const scheduleData = await scheduleResponse.json();
      
      // Find the completed schedule for today and the future schedule
      const today = format(new Date(), 'yyyy-MM-dd');
      const completedSchedule = scheduleData.find((schedule: any) => 
        schedule.completed && 
        schedule.completion_timestamp && 
        format(new Date(schedule.completion_timestamp), 'yyyy-MM-dd') === today
      );

      const futureSchedule = scheduleData.find((schedule: any) => 
        !schedule.completed && 
        format(new Date(schedule.scheduled_date), 'yyyy-MM-dd') > today
      );

      if (!completedSchedule) {
        throw new Error('No completed schedule found for today');
      }

      // Update the completed schedule to mark as not completed
      const response = await fetch(`${API_ENDPOINTS.BASE_URL}/api/watering-schedule/${completedSchedule.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ 
          completed: false,
          completion_timestamp: null
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to reset watering status');
      }

      // Delete the future schedule if it exists
      if (futureSchedule) {
        const deleteResponse = await fetch(`${API_ENDPOINTS.BASE_URL}/api/watering-schedule/${futureSchedule.id}`, {
          method: 'DELETE',
          headers: {
            'Accept': 'application/json',
          },
          credentials: 'include'
        });

        if (!deleteResponse.ok) {
          console.warn('Failed to delete future schedule, but continuing with reset');
        }
      }

      // Update local state to maintain the plant's visibility and remove next scheduled watering
      setScheduleData(prevData => {
        const updatedData = prevData.filter(p => {
          // Keep the plant if it's not the future scheduled watering
          if (p.plant_id === plant.plant_id) {
            return p.next_watering === today; // Only keep today's entry
          }
          return true;
        }).map(p => {
          if (p.plant_id === plant.plant_id && p.next_watering === today) {
            // Update today's entry to show as not watered
            return {
              ...p,
              last_watered: undefined,
              is_watered: false
            };
          }
          return p;
        });
        scheduleDataRef.current = updatedData;
        return updatedData;
      });

      // Show success message
      setSnackbar({
        open: true,
        message: `Reset watering status for ${plant.plant_name}`,
        severity: 'success'
      });

      // Close the popover
      handleClosePopover();
    } catch (error) {
      console.error('Error resetting watering status:', error);
      setSnackbar({
        open: true,
        message: error instanceof Error ? error.message : 'Failed to reset watering status',
        severity: 'error'
      });
    }
  };

  const groupPlantsByFrequency = (plants: WateringSchedule[]): WateringGroup[] => {
    const groups: { [key: number]: WateringSchedule[] } = {};
    
    plants.forEach(plant => {
      if (!groups[plant.watering_frequency]) {
        groups[plant.watering_frequency] = [];
      }
      groups[plant.watering_frequency].push(plant);
    });

    return Object.entries(groups).map(([frequency, plants]) => ({
      frequency: parseInt(frequency),
      plants,
      nextWatering: plants[0].next_watering // All plants in group have same next watering
    }));
  };

  const getWateringStatus = (group: WateringGroup) => {
    const today = new Date();
    const nextWatering = new Date(group.nextWatering);
    
    if (isBefore(nextWatering, today)) {
      return { status: 'overdue', color: 'error.main' };
    }
    
    const daysUntilWatering = differenceInDays(nextWatering, today);
    if (daysUntilWatering <= 2) {
      return { status: 'due-soon', color: 'warning.main' };
    }
    
    return { status: 'on-track', color: 'success.main' };
  };

  // Add logging for section plants
  const getSectionPlants = (sectionName: string) => {
    const plants = scheduleData.filter(p => p.section === sectionName);
    console.log(`Plants for section ${sectionName}:`, plants);
    return plants;
  };

  // Add logging for day plants
  const getDayGroups = (plants: WateringSchedule[], day: Date) => {
    const dayStr = format(day, 'yyyy-MM-dd');
    const dayPlants = plants.filter(plant => 
      format(new Date(plant.next_watering), 'yyyy-MM-dd') === dayStr
    );
    const groups = groupPlantsByFrequency(dayPlants);
    console.log(`Groups for day ${dayStr}:`, groups);
    return groups;
  };

  const getSectionStats = (sectionName: string): SectionStats => {
    const sectionPlants = scheduleData.filter(p => p.section === sectionName);
    const stats: SectionStats = {
      totalPlants: sectionPlants.length,
      plantsByDay: {}
    };

    gridDays.forEach(day => {
      const dayStr = format(day, 'yyyy-MM-dd');
      const dayPlants = sectionPlants.filter(plant => 
        format(new Date(plant.next_watering), 'yyyy-MM-dd') === dayStr
      );

      const overdue = dayPlants.filter(plant => 
        isBefore(new Date(plant.next_watering), new Date())
      ).length;

      const dueSoon = dayPlants.filter(plant => {
        const nextWatering = new Date(plant.next_watering);
        const daysUntilWatering = differenceInDays(nextWatering, new Date());
        return daysUntilWatering <= 2 && daysUntilWatering > 0;
      }).length;

      stats.plantsByDay[dayStr] = {
        count: dayPlants.length,
        plants: dayPlants,
        overdue,
        dueSoon
      };
    });

    return stats;
  };

  const getCellColor = (stats: { count: number; overdue: number; dueSoon: number }) => {
    if (stats.overdue > 0) return 'error.main';
    if (stats.dueSoon > 0) return 'warning.main';
    if (stats.count > 0) return 'success.main';
    return 'grey.200';
  };

  const getCellIntensity = (count: number, maxCount: number) => {
    if (count === 0) return 0;
    return Math.min(0.3 + (count / maxCount) * 0.7, 1);
  };

  const handleCellClick = (event: React.MouseEvent<HTMLElement>, day: string, section: string) => {
    setAnchorEl(event.currentTarget);
    setSelectedDay(day);
    setSelectedSection(section);
  };

  const handleClosePopover = () => {
    setAnchorEl(null);
    setSelectedDay(null);
    setSelectedSection(null);
  };

  const handlePlantClick = async (plant: WateringSchedule) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_ENDPOINTS.PLANTS}/${plant.plant_id}`);
      if (!response.ok) {
        throw new Error('Failed to fetch plant details');
      }
      const data = await response.json();
      console.log('Fetched plant data:', data); // Debug log
      setSelectedPlant(data);
      handleClosePopover();
    } catch (error) {
      console.error('Error fetching plant details:', error);
    } finally {
      setLoading(false);
    }
  };

  const getPlantsForDay = (day: string) => {
    return scheduleData.filter(plant => 
      format(new Date(plant.next_watering), 'yyyy-MM-dd') === day
    );
  };

  const getPlantsForDayAndSection = (day: string, section: string) => {
    const plants = scheduleData.filter(plant => {
      const isNextWateringDay = format(new Date(plant.next_watering), 'yyyy-MM-dd') === day;
      const wasWateredToday = plant.last_watered === day;
      const isInSection = plant.section === section;
      // Only show one entry per plant per day
      return isInSection && (
        (isNextWateringDay && !wasWateredToday) ||
        wasWateredToday
      );
    });
    // Remove duplicates by plant_id (keep watered if exists)
    const uniquePlants = Object.values(
      plants.reduce((acc, plant) => {
        if (!acc[plant.plant_id] || plant.last_watered === day) {
          acc[plant.plant_id] = plant;
        }
        return acc;
      }, {} as { [plant_id: number]: WateringSchedule })
    );
    console.log(`Plants for ${day} in ${section}:`, uniquePlants);
    return uniquePlants;
  };

  // Add helper function to check if a date is today
  const isToday = (date: string) => {
    return format(new Date(date), 'yyyy-MM-dd') === format(new Date(), 'yyyy-MM-dd');
  };

  const getSectionCounts = (plants: WateringSchedule[]) => {
    const counts: { [key: string]: number } = {};
    plants.forEach(plant => {
      counts[plant.section] = (counts[plant.section] || 0) + 1;
    });
    return counts;
  };

  const getSectionGlyph = (sectionName: string) => {
    // Find the section by name and return its glyph
    const section = sections.find(s => s.name === sectionName);
    return section?.glyph || '❓';
  };

  const getMaxPlantsPerSection = () => {
    const maxCounts: { [key: string]: number } = {};
    gridDays.forEach(day => {
      const dayStr = format(day, 'yyyy-MM-dd');
      const dayPlants = getPlantsForDay(dayStr);
      const sectionCounts = getSectionCounts(dayPlants);
      
      Object.entries(sectionCounts).forEach(([section, count]) => {
        maxCounts[section] = Math.max(maxCounts[section] || 0, count);
      });
    });
    return maxCounts;
  };

  const getIntensity = (count: number, maxCount: number) => {
    if (count === 0) return 0;
    // Base opacity for any non-zero count
    const baseOpacity = 0.4;
    // Additional opacity based on relative count
    const relativeOpacity = (count / maxCount) * 0.6;
    return baseOpacity + relativeOpacity;
  };

  const getBlockHeight = (count: number, maxCount: number) => {
    if (count === 0) return 0;
    // Minimum height for any non-zero count
    const minHeight = 24;
    // Additional height based on relative count
    const maxAdditionalHeight = 48; // Maximum additional height
    const relativeHeight = (count / maxCount) * maxAdditionalHeight;
    return minHeight + relativeHeight;
  };

  const getWorkloadPattern = (count: number, maxCount: number) => {
    if (count === 0) return 'none';
    const ratio = count / maxCount;
    if (ratio <= 0.25) return 'repeating-linear-gradient(45deg, transparent, transparent 2px, rgba(255,255,255,0.1) 2px, rgba(255,255,255,0.1) 4px)';
    if (ratio <= 0.5) return 'repeating-linear-gradient(45deg, transparent, transparent 1px, rgba(255,255,255,0.15) 1px, rgba(255,255,255,0.15) 2px)';
    if (ratio <= 0.75) return 'repeating-linear-gradient(45deg, transparent, transparent 1px, rgba(255,255,255,0.2) 1px, rgba(255,255,255,0.2) 2px), repeating-linear-gradient(-45deg, transparent, transparent 1px, rgba(255,255,255,0.2) 1px, rgba(255,255,255,0.2) 2px)';
    return 'repeating-linear-gradient(45deg, transparent, transparent 1px, rgba(255,255,255,0.25) 1px, rgba(255,255,255,0.25) 2px), repeating-linear-gradient(-45deg, transparent, transparent 1px, rgba(255,255,255,0.25) 1px, rgba(255,255,255,0.25) 2px)';
  };

  const PlantCard: React.FC<{ plant: any; onMarkAsWatered: (plant: any) => void; onResetWatering: (plant: any) => void }> = ({ 
    plant, 
    onMarkAsWatered, 
    onResetWatering 
  }) => {
    const theme = useTheme();
    const isWatered = plant.is_watered;
    const isWeatherAdjusted = plant.weather_adjusted;

    return (
      <Card 
        sx={{ 
          mb: 1, 
          position: 'relative',
          border: isWeatherAdjusted ? `1px solid ${theme.palette.warning.main}` : 'none'
        }}
      >
        <CardContent sx={{ p: 1, '&:last-child': { pb: 1 } }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Avatar 
              src={plant.image_url} 
              alt={plant.plant_name}
              sx={{ width: 40, height: 40 }}
            />
            <Box sx={{ flex: 1 }}>
              <Typography variant="subtitle2">{plant.plant_name}</Typography>
              <Typography variant="caption" color="text.secondary">
                Every {plant.watering_frequency} days
              </Typography>
            </Box>
            <Box>
              {isWatered ? (
                <Tooltip title="Reset watering status">
                  <IconButton 
                    size="small" 
                    onClick={() => onResetWatering(plant)}
                    color="success"
                  >
                    <CheckCircleIcon />
                  </IconButton>
                </Tooltip>
              ) : (
                <Tooltip title="Mark as watered">
                  <IconButton 
                    size="small" 
                    onClick={() => onMarkAsWatered(plant)}
                    color="primary"
                  >
                    <WaterDropIcon />
                  </IconButton>
                </Tooltip>
              )}
            </Box>
          </Box>
        </CardContent>
      </Card>
    );
  };

  // Lower the threshold for hotWeatherIndex to 30°C
  const hotWeatherIndex = rawScheduleData && rawScheduleData.schedule
    ? rawScheduleData.schedule.findIndex(day => day.weather && day.weather.temperature >= 30)
    : -1;

  if (loading) {
    return (
      <Paper sx={{ p: 2, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Paper>
    );
  }

  if (error) {
    return (
      <Paper sx={{ p: 2 }}>
        <Typography color="error">{error}</Typography>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column', bgcolor: 'background.default' }}>
      {/* Weather Legend */}
      <Box sx={{ 
        display: 'flex', 
        gap: 2, 
        mb: 2, 
        alignItems: 'center',
        flexWrap: 'wrap',
        opacity: 0.8
      }}>
        {!isNextWeek && hotWeatherIndex !== -1 && (
          <>
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: 1,
              bgcolor: 'background.paper',
              color: 'error.main',
              px: 1.5,
              py: 0.75,
              borderRadius: 2,
              border: '1px solid',
              borderColor: 'error.light',
              transition: 'all 0.2s ease',
              '&:hover': {
                opacity: 1,
                bgcolor: 'error.light',
              }
            }}>
              <span role="img" aria-label="hot" style={{ fontSize: '1.1rem' }}>🔥</span>
              <Typography variant="body2" sx={{ fontWeight: 500, fontSize: '0.875rem' }}>
                Hot weather day
              </Typography>
            </Box>
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: 1,
              bgcolor: 'background.paper',
              color: 'warning.dark',
              px: 1.5,
              py: 0.75,
              borderRadius: 2,
              border: '1px dashed',
              borderColor: 'warning.light',
              transition: 'all 0.2s ease',
              '&:hover': {
                opacity: 1,
                bgcolor: 'warning.light',
              }
            }}>
              <span role="img" aria-label="affected" style={{ fontSize: '1.1rem' }}>⚠️</span>
              <Typography variant="body2" sx={{ fontWeight: 500, fontSize: '0.875rem' }}>
                Affected range: Watering moved earlier
              </Typography>
            </Box>
          </>
        )}
        {isNextWeek && (
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 1,
            bgcolor: 'background.paper',
            color: 'info.dark',
            px: 1.5,
            py: 0.75,
            borderRadius: 2,
            border: '1px solid',
            borderColor: 'info.light',
          }}>
            <span role="img" aria-label="info" style={{ fontSize: '1.1rem' }}>ℹ️</span>
            <Typography variant="body2" sx={{ fontWeight: 500, fontSize: '0.875rem' }}>
              Next week view shows scheduled waterings without weather adjustments
            </Typography>
          </Box>
        )}
      </Box>

      {/* Grid Header */}
      <Grid container spacing={0.5} sx={{ mb: 1 }}>
        {gridDays.map((day, index) => (
          <Grid item xs={1.71} key={index}>
            <Typography variant="caption" display="block" sx={{ fontWeight: 'bold' }}>
              {format(day, 'EEE')}
            </Typography>
            <Typography variant="body2" sx={{ color: 'text.secondary' }}>
              {format(day, 'MMM d')}
            </Typography>
          </Grid>
        ))}
      </Grid>

      {/* Plants Grid */}
      <Grid container spacing={0.5}>
        {gridDays.map((day, dayIndex) => {
          const dayStr = format(day, 'yyyy-MM-dd');
          const dayPlants = getPlantsForDay(dayStr);
          const sectionCounts = getSectionCounts(dayPlants);
          const maxCounts = getMaxPlantsPerSection();
          const dayWeather = rawScheduleData?.schedule?.find(s => s.date === dayStr)?.weather;

          // Weather visuals
          const isHotWeather = dayWeather && dayWeather.temperature >= 30;
          // Calculate affected range based on the current week's hot weather day
          const currentWeekHotWeatherIndex = gridDays.findIndex(d => {
            const dStr = format(d, 'yyyy-MM-dd');
            const weather = rawScheduleData?.schedule?.find(s => s.date === dStr)?.weather;
            return weather && weather.temperature >= 30;
          });
          const isAfterHotWeather = currentWeekHotWeatherIndex !== -1 && dayIndex > currentWeekHotWeatherIndex;

          return (
            <Grid item xs={1.71} key={dayIndex}>
              <Box 
                className={`calendar-day${isHotWeather && !isNextWeek ? ' hot-weather' : ''}${isAfterHotWeather && !isNextWeek ? ' affected-range' : ''}`}
                sx={{ 
                  minHeight: 180,
                  p: 0.5,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 0.5,
                  bgcolor: 'background.paper',
                  borderRadius: 2,
                  boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                  border: isAfterHotWeather && !isNextWeek ? '2px dashed orange' : '1px solid',
                  borderColor: isAfterHotWeather && !isNextWeek ? 'warning.main' : 'divider',
                  background: isAfterHotWeather && !isNextWeek 
                    ? 'linear-gradient(135deg, #fff7e6 0%, #fff3e0 100%)' 
                    : 'linear-gradient(135deg, #ffffff 0%, #fafafa 100%)',
                  position: 'relative',
                  opacity: isNextWeek ? 0.9 : 1,
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  '&:hover': {
                    transform: 'translateY(-2px)',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                  }
                }}
              >
                {/* Weather display - only show for current week */}
                {!isNextWeek && dayIndex < 7 && dayWeather && (
                  <Box sx={{ 
                    mb: 1,
                    p: 0.5,
                    borderRadius: 1.5,
                    position: 'relative',
                    display: 'inline-block',
                    background: 'linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.7))',
                    backdropFilter: 'blur(8px)',
                    border: '1px solid',
                    borderColor: 'divider'
                  }}>
                    <WeatherDisplay weather={dayWeather} />
                  </Box>
                )}

                {/* Simplified affected range tooltip - only for current week */}
                {isAfterHotWeather && !isNextWeek && (
                  <Tooltip title="Watering schedule adjusted due to hot weather" arrow>
                    <Box sx={{ position: 'absolute', top: 4, right: 4 }}>
                      {/* Empty box for tooltip trigger */}
                    </Box>
                  </Tooltip>
                )}

                {/* Section plants */}
                {Object.entries(sectionCounts).map(([section, count]) => {
                  const maxCount = maxCounts[section] || 1;
                  const plants = getPlantsForDayAndSection(dayStr, section);
                  const wateredCount = plants.filter(p => p.last_watered === dayStr).length;
                  const progress = (wateredCount / count) * 100;

                  return (
                    <Tooltip
                      key={section}
                      title={`${section}: ${wateredCount}/${count} plants watered`}
                      arrow
                    >
                      <Box
                        onClick={(e) => handleCellClick(e, dayStr, section)}
                        sx={{
                          position: 'relative',
                          height: 24,
                          bgcolor: count === 0 ? 'grey.100' : 'info.main',
                          borderRadius: 1.5,
                          cursor: 'pointer',
                          overflow: 'hidden',
                          transition: 'all 0.2s ease',
                          '&:hover': {
                            opacity: 0.9,
                            transform: 'scale(1.02)',
                          }
                        }}
                      >
                        {/* Progress fill */}
                        <Box
                          sx={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            bottom: 0,
                            width: `${progress}%`,
                            bgcolor: 'success.main',
                            background: 'linear-gradient(90deg, rgba(76, 175, 80, 0.9), rgba(76, 175, 80, 0.7))',
                            transition: 'width 0.3s ease-in-out'
                          }}
                        />
                        {/* Section content */}
                        <Box
                          sx={{
                            position: 'relative',
                            zIndex: 1,
                            height: '100%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            px: 1.5,
                            textShadow: '0 1px 2px rgba(0,0,0,0.2)'
                          }}
                        >
                          <Typography
                            variant="caption"
                            sx={{
                              color: 'white',
                              fontWeight: 600,
                              fontSize: '0.875rem'
                            }}
                          >
                            {getSectionGlyph(section)}
                          </Typography>
                          <Typography
                            variant="caption"
                            sx={{
                              color: 'white',
                              fontWeight: 600,
                              fontSize: '0.875rem'
                            }}
                          >
                            {wateredCount}/{count}
                          </Typography>
                        </Box>
                      </Box>
                    </Tooltip>
                  );
                })}
              </Box>
            </Grid>
          );
        })}
      </Grid>

      {/* Plants Popover */}
      {Boolean(anchorEl) && selectedDay && selectedSection && (
        <Popover
          open={Boolean(anchorEl)}
          anchorEl={anchorEl}
          onClose={handleClosePopover}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'center',
          }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'center',
          }}
          slotProps={{
            paper: {
              sx: {
                maxWidth: 400,
                maxHeight: 400,
                overflow: 'auto',
                borderRadius: 2,
                boxShadow: 3
              }
            }
          }}
        >
          <Box sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                {getSectionGlyph(selectedSection)} {selectedSection}
              </Typography>
              <Typography variant="subtitle1" color="text.secondary">
                {format(new Date(selectedDay), 'MMMM d, yyyy')}
              </Typography>
            </Box>
            {getPlantsForDayAndSection(selectedDay, selectedSection).map((plant) => {
              const isWatered = plant.last_watered === selectedDay;
              return (
                <Card
                  key={`${plant.plant_id}_${plant.next_watering}`}
                  sx={{
                    mb: 1,
                    cursor: 'pointer',
                    borderLeft: `4px solid ${isWatered ? 'success.main' : 'primary.main'}`,
                    border: plant.weather_adjusted ? `1px solid ${theme.palette.warning.main}` : 'none',
                    transition: 'all 0.2s ease-in-out',
                    bgcolor: isWatered 
                      ? 'linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(76, 175, 80, 0.05))' 
                      : 'background.paper',
                    '&:hover': { 
                      bgcolor: isWatered 
                        ? 'linear-gradient(135deg, rgba(76, 175, 80, 0.15), rgba(76, 175, 80, 0.1))' 
                        : 'action.hover',
                      transform: 'translateX(4px)',
                      boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                    },
                    borderRadius: 1.5,
                    overflow: 'hidden'
                  }}
                  onClick={() => handlePlantClick(plant)}
                >
                  <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                      <Avatar
                        src={plant.image_url}
                        alt={plant.plant_name}
                        sx={{ 
                          width: 32, 
                          height: 32,
                          bgcolor: isWatered ? 'success.main' : 'primary.main',
                          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                          border: '2px solid',
                          borderColor: isWatered ? 'success.light' : 'primary.light'
                        }}
                      >
                        {isWatered ? '💧' : '🌿'}
                      </Avatar>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 0.5 }}>
                          {plant.plant_name}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="caption" color="text.secondary">
                            Every {plant.watering_frequency} days
                          </Typography>
                          {plant.weather_adjusted && plant.weather_info?.original_date && (
                            <Tooltip title={`Adjusted from ${format(new Date(plant.weather_info.original_date), 'MMM d')} due to weather conditions`}>
                              <Chip 
                                size="small" 
                                label="Weather Adjusted" 
                                color="warning" 
                                sx={{ 
                                  height: 20,
                                  '& .MuiChip-label': {
                                    px: 1,
                                    fontSize: '0.75rem'
                                  }
                                }}
                              />
                            </Tooltip>
                          )}
                        </Box>
                      </Box>
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        {isWatered ? (
                          <IconButton 
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleResetWatering(plant);
                            }}
                            sx={{
                              color: 'error.main',
                              bgcolor: 'error.light',
                              '&:hover': {
                                bgcolor: 'error.main',
                                color: 'error.contrastText'
                              }
                            }}
                          >
                            <RestoreIcon />
                          </IconButton>
                        ) : (
                          <Tooltip title={!isToday(selectedDay!) ? "Can only mark plants as watered for today" : "Mark as watered"}>
                            <span>
                              <IconButton 
                                size="small"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  if (isToday(selectedDay!)) {
                                    handleMarkAsWatered(plant);
                                  }
                                }}
                                sx={{
                                  color: isToday(selectedDay!) ? 'primary.main' : 'action.disabled',
                                  bgcolor: isToday(selectedDay!) ? 'primary.light' : 'transparent',
                                  '&:hover': {
                                    bgcolor: isToday(selectedDay!) ? 'primary.main' : 'transparent',
                                    color: isToday(selectedDay!) ? 'primary.contrastText' : 'action.disabled'
                                  }
                                }}
                                disabled={!isToday(selectedDay!)}
                              >
                                <WaterDropIcon />
                              </IconButton>
                            </span>
                          </Tooltip>
                        )}
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              );
            })}
          </Box>
        </Popover>
      )}

      {/* Plant Details Dialog */}
      {selectedPlant && (
        <PlantDetails
          plant={selectedPlant}
          open={!!selectedPlant}
          onClose={() => setSelectedPlant(null)}
          sections={sections}
        />
      )}

      {/* Loading Overlay */}
      {loading && (
        <Box
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            bgcolor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999
          }}
        >
          <CircularProgress />
        </Box>
      )}

      {/* Snackbar for feedback */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={() => setSnackbar(prev => ({ ...prev, open: false }))} 
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Paper>
  );
};

export default WateringSchedule; 
