import React, { useState, useEffect } from 'react';
import './Community.css';

const Community = () => {
  const [communityLayers, setCommunityLayers] = useState([]);
  const [myLayers, setMyLayers] = useState([]);
  
  useEffect(() => {
    loadLayers();
  }, []);
  
  const loadLayers = () => {
    const community = JSON.parse(localStorage.getItem('communityLayers') || '[]');
    const personal = JSON.parse(localStorage.getItem('myLayers') || '[]');
    setCommunityLayers(community);
    setMyLayers(personal);
  };
  
  const likeLayer = (id, isCommunity) => {
    const key = isCommunity ? 'communityLayers' : 'myLayers';
    const layers = JSON.parse(localStorage.getItem(key) || '[]');
    const updated = layers.map(layer => 
      layer.id === id ? { ...layer, likes: (layer.likes || 0) + 1 } : layer
    );
    localStorage.setItem(key, JSON.stringify(updated));
    loadLayers();
  };
  
  const deleteLayer = (id, isCommunity) => {
    const key = isCommunity ? 'communityLayers' : 'myLayers';
    const layers = JSON.parse(localStorage.getItem(key) || '[]');
    const updated = layers.filter(layer => layer.id !== id);
    localStorage.setItem(key, JSON.stringify(updated));
    loadLayers();
  };
  
  const LayerCard = ({ layer, isCommunity }) => (
    <div className="layer-card">
      <div className="card-header">
        <span className="card-title">{layer.name}</span>
        <span className="card-badge">{layer.location}</span>
      </div>
      <div className="card-meta">
        <span>{layer.author}</span>
        <span>{new Date(layer.timestamp).toLocaleDateString()}</span>
      </div>
      <div className="card-actions">
        <button className="card-btn" onClick={() => likeLayer(layer.id, isCommunity)}>
          LIKE {layer.likes || 0}
        </button>
        <button className="card-btn">VIEW</button>
        {!isCommunity && (
          <button className="card-btn delete" onClick={() => deleteLayer(layer.id, false)}>
            DELETE
          </button>
        )}
      </div>
    </div>
  );
  
  return (
    <div className="community-container">
      <section className="community-section">
        <div className="section-header">
          <h2 className="section-title">COMMUNITY LAYERS</h2>
          <span className="section-count">{communityLayers.length} LAYERS</span>
        </div>
        
        <div className="layers-grid">
          {communityLayers.length === 0 ? (
            <div className="empty-state">
              <p>No community layers yet</p>
            </div>
          ) : (
            communityLayers.map(layer => (
              <LayerCard key={layer.id} layer={layer} isCommunity={true} />
            ))
          )}
        </div>
      </section>
      
      <section className="community-section">
        <div className="section-header">
          <h2 className="section-title">MY LAYERS</h2>
          <span className="section-count">{myLayers.length} SAVED</span>
        </div>
        
        <div className="layers-grid">
          {myLayers.length === 0 ? (
            <div className="empty-state">
              <p>No saved layers</p>
            </div>
          ) : (
            myLayers.map(layer => (
              <LayerCard key={layer.id} layer={layer} isCommunity={false} />
            ))
          )}
        </div>
      </section>
    </div>
  );
};

export default Community;
