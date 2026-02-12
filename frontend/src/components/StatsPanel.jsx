import React from 'react';
import './StatsPanel.css';

const StatsPanel = ({ layerData }) => {
  if (!layerData || !layerData.metadata) return null;
  
  const meta = layerData.metadata;
  
  return (
    <div className="stats-panel">
      <div className="stat-item">
        <span className="stat-label">SOURCE</span>
        <span className="stat-value">{meta.source}</span>
      </div>
      <div className="stat-item">
        <span className="stat-label">FEATURES</span>
        <span className="stat-value">{meta.feature_count}</span>
      </div>
      <div className="stat-item">
        <span className="stat-label">TYPE</span>
        <span className="stat-value">{meta.layer_type}</span>
      </div>
    </div>
  );
};

export default StatsPanel;
