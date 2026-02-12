import React, { useState } from 'react';
import Layout from './components/Layout';
import Community from './components/Community';
import './App.css';

function App() {
  const [layerData, setLayerData] = useState(null);
  const [viewPosition, setViewPosition] = useState({
    longitude: 37.6173,
    latitude: 55.7558,
    height: 10000
  });
  
  const [visiblePanels, setVisiblePanels] = useState({
    cesium: true,
    leaflet: true,
    chat: true
  });
  
  const [currentLayer, setCurrentLayer] = useState(null);
  
  const handleNewLayer = (data, position) => {
    setLayerData(data);
    setCurrentLayer({
      data: data,
      position: position,
      timestamp: new Date().toISOString()
    });
    
    if (position) {
      setViewPosition({
        longitude: position[0],
        latitude: position[1],
        height: 10000
      });
    }
  };
  
  const togglePanel = (panel) => {
    setVisiblePanels(prev => ({
      ...prev,
      [panel]: !prev[panel]
    }));
  };

  return (
    <div className="App">
      <Layout
        layerData={layerData}
        viewPosition={viewPosition}
        visiblePanels={visiblePanels}
        onNewLayer={handleNewLayer}
        onTogglePanel={togglePanel}
        currentLayer={currentLayer}
      />
      <Community />
    </div>
  );
}

export default App;
