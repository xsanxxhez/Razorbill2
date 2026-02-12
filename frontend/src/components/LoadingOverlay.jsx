import React from 'react';
import './LoadingOverlay.css';

const LoadingOverlay = ({ message }) => {
  return (
    <div className="loading-overlay">
      <div className="loading-content">
        <div className="loading-spinner">
          <div className="spinner-ring"></div>
          <div className="spinner-ring"></div>
          <div className="spinner-ring"></div>
        </div>
        <div className="loading-text">{message || 'Loading data...'}</div>
      </div>
    </div>
  );
};

export default LoadingOverlay;
