import React, { useState, useEffect } from 'react';
import CesiumViewer from './CesiumViewer';
import LeafletMap from './LeafletMap';
import ChatPanel from './ChatPanel';
import LoadingOverlay from './LoadingOverlay';
import Notification from './Notification';
import './Layout.css';

const Layout = ({ layerData, viewPosition, visiblePanels, onNewLayer, onTogglePanel, currentLayer }) => {
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState(null);
  const panelCount = Object.values(visiblePanels).filter(Boolean).length;
  
  return (
    <div className="layout-container">
      {loading && <LoadingOverlay message="Fetching data..." />}
      {notification && (
        <Notification
          message={notification.message}
          type={notification.type}
          onClose={() => setNotification(null)}
        />
      )}
      
      <div className="header">
        <div className="logo-section">
          <div className="logo-glow"></div>
          <div className="logo">
            <span className="logo-text">RAZORBILL</span>
            <span className="logo-sub">INTELLIGENCE</span>
          </div>
        </div>
        
        <div className="header-info">
          {layerData && (
            <div className="layer-info-compact">
              <span className="info-text">{layerData.metadata?.location}</span>
              <span className="info-separator">•</span>
              <span className="info-text">{layerData.metadata?.layer_type}</span>
              <span className="info-separator">•</span>
              <span className="info-text">{layerData.metadata?.feature_count} objects</span>
            </div>
          )}
        </div>
      </div>
      
      <div className="workspace">
        <div className="sidebar">
          <div className="sidebar-section">
            <div className="section-title">WORKSPACE</div>
            <div className="view-controls">
              <button 
                className={`view-btn ${visiblePanels.cesium ? 'active' : ''}`}
                onClick={() => onTogglePanel('cesium')}
              >
                <span className="view-label">3D CESIUM</span>
                <span className="view-status">{visiblePanels.cesium ? 'ON' : 'OFF'}</span>
              </button>
              <button 
                className={`view-btn ${visiblePanels.leaflet ? 'active' : ''}`}
                onClick={() => onTogglePanel('leaflet')}
              >
                <span className="view-label">2D MAP</span>
                <span className="view-status">{visiblePanels.leaflet ? 'ON' : 'OFF'}</span>
              </button>
              <button 
                className={`view-btn ${visiblePanels.chat ? 'active' : ''}`}
                onClick={() => onTogglePanel('chat')}
              >
                <span className="view-label">AI CONSOLE</span>
                <span className="view-status">{visiblePanels.chat ? 'ON' : 'OFF'}</span>
              </button>
            </div>
          </div>
          
          <div className="sidebar-section">
            <div className="section-title">STATUS</div>
            <div className="status-list">
              <div className="status-item">
                <span className="status-label">Sync</span>
                <span className="status-value active">LIVE</span>
              </div>
              <div className="status-item">
                <span className="status-label">Views</span>
                <span className="status-value">{panelCount}</span>
              </div>
              <div className="status-item">
                <span className="status-label">Objects</span>
                <span className="status-value">{layerData?.features?.length || 0}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div className={`panels panels-${panelCount}`}>
          {visiblePanels.cesium && (
            <div className="panel">
              <div className="panel-header">
                <div className="panel-title-group">
                  <span className="panel-title">3D CESIUM GLOBE</span>
                </div>
                <div className="panel-controls">
                  <div className="panel-status">
                    <span className="status-dot active"></span>
                    <span>SYNCHRONIZED</span>
                  </div>
                </div>
              </div>
              <CesiumViewer 
                layerData={layerData}
                viewPosition={viewPosition}
              />
            </div>
          )}
          
          {visiblePanels.leaflet && (
            <div className="panel">
              <div className="panel-header">
                <div className="panel-title-group">
                  <span className="panel-title">2D MAP VIEW</span>
                </div>
                <div className="panel-controls">
                  <div className="panel-status">
                    <span className="status-dot active"></span>
                    <span>SYNCHRONIZED</span>
                  </div>
                </div>
              </div>
              <LeafletMap 
                layerData={layerData}
                viewPosition={viewPosition}
              />
            </div>
          )}
          
          {visiblePanels.chat && (
            <div className="panel">
              <div className="panel-header">
                <div className="panel-title-group">
                  <span className="panel-title">AI CONSOLE</span>
                </div>
                <div className="panel-controls">
                  <div className="panel-status">
                    <span className="status-dot active"></span>
                    <span>ONLINE</span>
                  </div>
                </div>
              </div>
              <ChatPanel 
                onNewLayer={onNewLayer}
                onLoading={setLoading}
                onNotification={setNotification}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Layout;
