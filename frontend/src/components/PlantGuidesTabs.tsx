import React, { useEffect, useState } from 'react';
import { API_ENDPOINTS } from '../config';
import { Tabs, Tab, Box, Typography } from '@mui/material';

interface PlantGuide {
  id: number;
  plant_id: number;
  type: 'watering' | 'sunlight' | 'pruning';
  description: string;
}

interface PlantGuidesTabsProps {
  plantId: number;
}

const categories: { key: PlantGuide['type']; label: string }[] = [
  { key: 'watering', label: 'Watering' },
  { key: 'sunlight', label: 'Sunlight' },
  { key: 'pruning', label: 'Pruning' },
];

const PlantGuidesTabsComponent: React.FC<PlantGuidesTabsProps> = ({ plantId }) => {
  const [guides, setGuides] = useState<PlantGuide[]>([]);
  const [selected, setSelected] = useState<PlantGuide['type']>('watering');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetch(`/api/plant_guides/plant/${plantId}`)
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch plant guides');
        return res.json();
      })
      .then(setGuides)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, [plantId]);

  const guide = guides.find(g => g.type === selected);

  return (
    <div style={{ border: '1px solid #eee', borderRadius: 8, padding: 16, marginTop: 24, minWidth: 260 }}>
      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        {categories.map(cat => (
          <button
            key={cat.key}
            onClick={() => setSelected(cat.key)}
            style={{
              padding: '6px 16px',
              borderRadius: 6,
              border: selected === cat.key ? '2px solid #60a5fa' : '1px solid #ccc',
              background: selected === cat.key ? '#e0f2fe' : '#f9f9f9',
              fontWeight: selected === cat.key ? 600 : 400,
              cursor: 'pointer',
            }}
          >
            {cat.label}
          </button>
        ))}
      </div>
      <div style={{ minHeight: 60 }}>
        {loading && <div>Loading...</div>}
        {error && <div style={{ color: 'red' }}>{error}</div>}
        {!loading && !error && (
          guide ? (
            <div>{guide.description}</div>
          ) : (
            <div style={{ color: '#888' }}>No guide available for this category.</div>
          )
        )}
      </div>
    </div>
  );
};

export default PlantGuidesTabsComponent; 