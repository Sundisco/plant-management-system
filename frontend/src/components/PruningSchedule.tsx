import React, { useState, useEffect } from 'react';
import { Box, Paper, Typography, Tooltip, CircularProgress, Table, TableBody, TableCell, TableHead, TableRow, Select, MenuItem } from '@mui/material';
import { Plant } from '../types/Plant';

interface PruningScheduleProps {
  selectedSection: string | null;
  userPlants: Plant[];
}

interface PlantDetail {
  id: number;
  name: string;
}

interface PruningData {
  section: string;
  months: {
    [key: string]: number;
  };
  details: {
    [key: string]: PlantDetail[];
  };
}

export const PruningSchedule: React.FC<PruningScheduleProps> = ({ selectedSection, userPlants }) => {
  const [sectionFilter, setSectionFilter] = useState<string>(selectedSection || '');
  const [pruningData, setPruningData] = useState<PruningData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  // Get all unique sections from userPlants
  const allSections = Array.from(new Set(userPlants.map(p => p.section).filter((s): s is string => !!s)));

  // Merge pruning months into userPlants
  const mergedPlants = userPlants.map(plant => {
    // Find matching pruningData entry by plant_id or id
    const pruningEntry = pruningData
      .flatMap(section => Object.values(section.details || {}))
      .flat()
      .find(detail => detail.id === plant.id || detail.id === (plant as any).plant_id);
    // Find the months for this plant in pruningData
    let pruningMonths: string[] = [];
    if (pruningEntry) {
      // Find the section that contains this plant
      const section = pruningData.find(sec => Object.values(sec.details || {}).some(arr => arr.some(d => d.id === pruningEntry.id)));
      if (section) {
        // Collect all months where this plant appears
        pruningMonths = Object.entries(section.details)
          .filter(([month, arr]) => arr.some(d => d.id === pruningEntry.id))
          .map(([month]) => month);
      }
    }
    return { ...plant, pruningMonths };
  });

  // Group plants by type, then by month
  const matrix: { [type: string]: typeof mergedPlants[] } = {};
  mergedPlants
    .filter(p => !sectionFilter || p.section === sectionFilter)
    .forEach(plant => {
      const type = plant.type || 'Other';
      if (!matrix[type]) matrix[type] = Array(12).fill(null).map(() => []);
      // Robustly parse pruningMonths as 1-based strings/numbers, convert to 0-based
      const pruningMonths: number[] = Array.isArray((plant as any).pruningMonths)
        ? (plant as any).pruningMonths
            .map((m: string | number) => Number(m) - 1)
            .filter((m: number) => Number.isInteger(m) && m >= 0 && m < 12)
        : [];
      pruningMonths.forEach((monthIdx: number) => {
        matrix[type][monthIdx].push(plant);
      });
    });

  // Find max for color scaling
  const max = Math.max(1, ...Object.values(matrix).flatMap(arr => arr.map(plants => plants.length)));

  useEffect(() => {
    const fetchPruningSchedule = async () => {
      try {
        setLoading(true);
        const userId = 1;
        const response = await fetch(`/api/pruning/schedule/${userId}`);
        const data = await response.json();
        setPruningData(data.pruning_schedule);
        setError(null);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'An error occurred';
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchPruningSchedule();
  }, [userPlants]);

  if (loading) return <Paper sx={{ p: 2, display: 'flex', justifyContent: 'center' }}><CircularProgress /></Paper>;
  if (error) return <Paper sx={{ p: 2 }}><Typography color="error">{error}</Typography></Paper>;
  if (!pruningData.length) {
    return (
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>Pruning Schedule</Typography>
        <Typography color="textSecondary">No pruning data available</Typography>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" sx={{ flex: 1 }}>Pruning Schedule Overview</Typography>
        <Select
          value={sectionFilter}
          onChange={e => setSectionFilter(e.target.value)}
          displayEmpty
          size="small"
          sx={{ minWidth: 140 }}
        >
          <MenuItem value="">All Sections</MenuItem>
          {allSections.map(s => (
            <MenuItem key={s} value={String(s)}>{`Section ${s}`}</MenuItem>
          ))}
        </Select>
      </Box>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Type</TableCell>
            {MONTHS.map(month => (
              <TableCell key={month} align="center">{month}</TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {Object.entries(matrix).map(([type, monthArr]) => (
            <TableRow key={type}>
              <TableCell>{type}</TableCell>
              {monthArr.map((plants, monthIdx) => (
                <TableCell
                  key={monthIdx}
                  align="center"
                  sx={{
                    bgcolor: plants.length
                      ? `rgba(56, 142, 60, ${0.2 + 0.8 * (plants.length / max)})`
                      : 'background.paper',
                    color: plants.length ? 'white' : 'text.secondary',
                    cursor: plants.length ? 'pointer' : 'default',
                    fontWeight: plants.length ? 'bold' : 'normal',
                    borderRadius: 1,
                    transition: 'background 0.2s',
                    minWidth: 36,
                    height: 36
                  }}
                >
                  {plants.length > 0 ? (
                    <Tooltip
                      title={
                        <Box sx={{ p: 1 }}>
                          <Typography variant="body2">
                            {`${plants.length} plant${plants.length > 1 ? 's' : ''} need${plants.length > 1 ? '' : 's'} pruning:`}
                          </Typography>
                          {plants.map(plant => (
                            <Typography key={plant.id} variant="body2" sx={{ pl: 1 }}>
                              • {plant.common_name}
                            </Typography>
                          ))}
                        </Box>
                      }
                      arrow
                    >
                      <span>{plants.length}</span>
                    </Tooltip>
                  ) : ''}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Paper>
  );
}; 