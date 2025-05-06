import React, { useState, useEffect, useMemo } from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts';
import { format } from 'date-fns';

interface Plant {
  plant_id: number;
  plant_name: string;
  watering_info: {
    frequency_days: number;
    depth_mm: number;
    volume_feet: number;
  };
}

interface PlantGroup {
  plants: Plant[];
}

interface Section {
  section: string;
  groups: PlantGroup[];
}

interface DaySchedule {
  date: string;
  sections: Section[];
  weather: {
    temperature: number;
    precipitation: number;
    wind_speed: number;
  };
  weather_icons: string[];
}

const sectionColors: Record<string, string> = {
  A: '#60a5fa', // blue-400
  B: '#34d399', // green-400
  C: '#fbbf24', // yellow-400
  // Add more as needed
};

const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

const WateringSchedule: React.FC = () => {
  const [schedule, setSchedule] = useState<DaySchedule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<{ day: string; section: string; barIdx: number } | null>(null);
  const chartRef = React.useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchSchedule = async () => {
      try {
        const response = await fetch('/api/1');
        if (!response.ok) {
          const errorData = await response.json().catch(() => null);
          throw new Error(errorData?.detail || `Failed to fetch watering schedule: ${response.status}`);
        }
        const data = await response.json();
        if (!data || !data.schedule || !Array.isArray(data.schedule)) {
          throw new Error('Invalid data format received');
        }
        setSchedule(data.schedule);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
        console.error('Error fetching schedule:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchSchedule();
  }, []);

  // Transform data for Recharts
  const chartData = useMemo(() => {
    if (!schedule || schedule.length === 0) return [];
    const sectionNames = Array.from(new Set(schedule.flatMap(day => day.sections.map(s => s.section))));
    return schedule.map((day) => {
      const entry: any = { day: dayNames[new Date(day.date).getDay()] };
      day.sections.forEach(section => {
        entry[section.section] = section.groups.reduce((sum, group) => sum + group.plants.length, 0);
      });
      return entry;
    });
  }, [schedule]);

  // For legend and bars
  const sectionNames = useMemo(() => {
    if (!schedule || schedule.length === 0) return [];
    return Array.from(new Set(schedule.flatMap(day => day.sections.map(s => s.section))));
  }, [schedule]);

  // Find plants for selected day/section
  const selectedPlants = useMemo(() => {
    if (!selected) return [];
    const dayIdx = selected.barIdx;
    const day = schedule[dayIdx];
    if (!day) return [];
    const section = day.sections.find(s => s.section === selected.section);
    if (!section) return [];
    return section.groups.flatMap(g => g.plants);
  }, [selected, schedule]);

  // Calculate popover position (to the right or left of the bar)
  const [popoverStyle, setPopoverStyle] = useState<React.CSSProperties>({});
  useEffect(() => {
    if (selected && chartRef.current) {
      const chartRect = chartRef.current.getBoundingClientRect();
      const barCount = chartData.length;
      const barWidth = chartRect.width / barCount;
      let left = chartRect.left + selected.barIdx * barWidth + barWidth;
      const popoverWidth = 260;
      // If not enough space on the right, show to the left
      if (left + popoverWidth > window.innerWidth) {
        left = chartRect.left + selected.barIdx * barWidth - popoverWidth;
      }
      if (left < 16) left = 16;
      setPopoverStyle({
        position: 'fixed',
        top: chartRect.top + 40, // 40px below the top of the chart
        left: left,
        zIndex: 100,
        width: popoverWidth,
        maxWidth: '90vw',
        background: '#fff',
        boxShadow: '0 4px 24px rgba(0,0,0,0.15)',
        borderRadius: '0.5rem',
        border: '1px solid #e5e7eb',
        padding: '1.5rem',
      });
    }
  }, [selected, chartData.length]);

  // Highlight logic for the selected bar segment
  const getBarStyle = (section: string, idx: number) =>
    selected && selected.section === section && selected.barIdx === idx
      ? { filter: 'drop-shadow(0 0 6px #2563eb)', stroke: '#2563eb', strokeWidth: 2 }
      : {};

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[200px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }
  if (error) {
    return (
      <div className="text-red-500 p-4 text-center">
        Error: {error}
      </div>
    );
  }
  if (!schedule || schedule.length === 0) {
    return (
      <div className="text-gray-500 p-4 text-center">
        No watering schedule available
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Weekly Watering Overview</h2>
      <div ref={chartRef} className="relative">
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
            <XAxis dataKey="day" />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Legend />
            {sectionNames.map(section => (
              <Bar
                key={section}
                dataKey={section}
                stackId="a"
                fill={sectionColors[section] || '#8884d8'}
                onClick={(_, idx) => setSelected({ day: chartData[idx].day, section, barIdx: idx })}
                // Highlight the selected bar segment
                shape={(props: any) => {
                  const { x, y, width, height, ...rest } = props;
                  const idx = props.index;
                  const style = getBarStyle(section, idx);
                  return (
                    <rect
                      x={x}
                      y={y}
                      width={width}
                      height={height}
                      fill={sectionColors[section] || '#8884d8'}
                      style={style}
                      cursor="pointer"
                      {...rest}
                    />
                  );
                }}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
        {selected && (
          <div style={popoverStyle} className="fixed">
            <button
              className="absolute top-2 right-2 text-gray-400 hover:text-gray-600 text-2xl font-bold"
              onClick={() => setSelected(null)}
              aria-label="Close"
            >
              &times;
            </button>
            <h3 className="font-semibold mb-2 text-lg">
              {selected.section} on {selected.day}
            </h3>
            {selectedPlants.length === 0 ? (
              <div className="text-gray-500">No plants need watering.</div>
            ) : (
              <ul className="list-disc pl-5">
                {selectedPlants.map(plant => (
                  <li key={plant.plant_id}>{plant.plant_name}</li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default WateringSchedule; 