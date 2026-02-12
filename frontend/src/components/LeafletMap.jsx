import React, { useEffect, useRef, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap, Circle, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './LeafletMap.css';

const MapController = ({ center, layerData }) => {
  const map = useMap();
  
  useEffect(() => {
    if (!layerData || !layerData.features || layerData.features.length === 0) return;
    
    try {
      const geojsonLayer = L.geoJSON(layerData);
      const bounds = geojsonLayer.getBounds();
      
      if (bounds.isValid()) {
        map.flyToBounds(bounds, {
          padding: [50, 50],
          maxZoom: 12,
          duration: 1.5
        });
      } else if (center && Array.isArray(center) && center.length === 2) {
        map.flyTo([center[1], center[0]], 6, {
          duration: 1.5
        });
      }
    } catch (error) {
      if (center && Array.isArray(center) && center.length === 2) {
        map.flyTo([center[1], center[0]], 6, {
          duration: 1.5
        });
      }
    }
  }, [layerData, center, map]);
  
  return null;
};

const AnimatedMarkers = ({ features, layerType }) => {
  const [visible, setVisible] = useState(false);
  
  useEffect(() => {
    setVisible(false);
    const timer = setTimeout(() => setVisible(true), 100);
    return () => clearTimeout(timer);
  }, [features]);
  
  if (!visible || layerType !== 'earthquakes') return null;
  
  return features.filter(f => f.geometry.type === 'Point').slice(0, 50).map((feature, idx) => {
    const coords = feature.geometry.coordinates;
    const mag = feature.properties.magnitude || 0;
    const radius = Math.max(mag * 5000, 5000);
    const color = mag > 6 ? '#ff0000' : mag > 5 ? '#ff6600' : mag > 4 ? '#ffaa00' : '#ffff00';
    
    return (
      <Circle
        key={idx}
        center={[coords[1], coords[0]]}
        radius={radius}
        pathOptions={{
          fillColor: color,
          fillOpacity: 0.4,
          color: color,
          weight: 2
        }}
      >
        <Popup>
          <div className="earthquake-popup">
            <strong>Magnitude: {mag}</strong><br/>
            {feature.properties.location}<br/>
            {feature.properties.time_readable}
          </div>
        </Popup>
      </Circle>
    );
  });
};

const LeafletMap = ({ layerData, viewPosition }) => {
  const [geoJsonKey, setGeoJsonKey] = useState(0);
  
  const center = viewPosition 
    ? [viewPosition.latitude, viewPosition.longitude]
    : [55.7558, 37.6173];
  
  useEffect(() => {
    setGeoJsonKey(prev => prev + 1);
  }, [layerData]);
  
  const getColor = (value, layerType) => {
    if (layerType === 'temperature' || layerType === 'weather') {
      const temp = value || 20;
      if (temp < -10) return '#0033ff';
      if (temp < 0) return '#0099ff';
      if (temp < 10) return '#00ffff';
      if (temp < 20) return '#00ff00';
      if (temp < 30) return '#ffff00';
      if (temp < 40) return '#ff9900';
      return '#ff0000';
    }
    
    if (layerType === 'density' || layerType === 'population') {
      if (value < 10) return '#ffffcc';
      if (value < 50) return '#a1dab4';
      if (value < 100) return '#41b6c4';
      if (value < 200) return '#2c7fb8';
      if (value < 500) return '#253494';
      return '#081d58';
    }
    
    return '#64c8ff';
  };
  
  const getStyle = (feature) => {
    const layerType = layerData?.metadata?.layer_type;
    
    let value = 0;
    if (layerType === 'temperature' || layerType === 'weather') {
      value = feature.properties?.temperature || 20;
    } else if (layerType === 'density') {
      value = feature.properties?.value || 0;
    } else if (layerType === 'earthquakes') {
      const mag = feature.properties?.magnitude || 0;
      const color = mag > 6 ? '#ff0000' : mag > 5 ? '#ff6600' : mag > 4 ? '#ffaa00' : '#ffff00';
      return {
        radius: Math.max(mag * 2, 3),
        fillColor: color,
        color: '#fff',
        weight: 2,
        fillOpacity: 0.8
      };
    }
    
    const fillColor = getColor(value, layerType);
    
    if (layerType === 'roads') {
      const highway = feature.properties?.highway || 'residential';
      const roadColors = {
        'motorway': '#ff0066',
        'trunk': '#ff3366',
        'primary': '#ff6699',
        'secondary': '#ff99cc',
        'tertiary': '#66ccff'
      };
      return {
        color: roadColors[highway] || '#99ccff',
        weight: 3,
        opacity: 0.9
      };
    }
    
    if (layerType === 'water' || layerType === 'rivers') {
      return {
        fillColor: '#00ccff',
        fillOpacity: 0.6,
        color: '#0099ff',
        weight: 2
      };
    }
    
    if (layerType === 'parks' || layerType === 'forests') {
      return {
        fillColor: '#00ff66',
        fillOpacity: 0.5,
        color: '#00cc44',
        weight: 1
      };
    }
    
    return {
      fillColor: fillColor,
      fillOpacity: 0.7,
      color: '#fff',
      weight: 1,
      opacity: 0.9
    };
  };
  
  const onEachFeature = (feature, layer) => {
    if (feature.properties) {
      const props = feature.properties;
      const layerType = layerData?.metadata?.layer_type;
      
      let content = '<div class="feature-popup">';
      
      if (layerType === 'temperature' || layerType === 'weather') {
        content += `<strong>🌡️ ${props.temperature}°C</strong>`;
        if (props.wind_speed) content += `<br/>💨 Wind: ${props.wind_speed} km/h`;
      } else if (layerType === 'density' || layerType === 'population') {
        content += `<strong>👥 ${props.formatted || props.value}</strong>`;
        if (props.region) content += `<br/>📍 ${props.region}`;
      } else if (layerType === 'earthquakes') {
        content += `<strong>🌍 M ${props.magnitude}</strong>`;
        content += `<br/>📍 ${props.location}`;
        content += `<br/>🕐 ${props.time_readable}`;
      } else {
        const entries = Object.entries(props).slice(0, 3);
        content += entries.map(([k, v]) => `<strong>${k}:</strong> ${v}`).join('<br/>');
      }
      
      content += '</div>';
      layer.bindPopup(content);
    }
  };
  
  if (!layerData || !layerData.features || layerData.features.length === 0) {
    return (
      <MapContainer
        center={center}
        zoom={6}
        style={{ width: '100%', height: '100%' }}
        className="leaflet-container"
      >
        <TileLayer
          url="https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png"
          attribution='&copy; Stadia Maps'
        />
        <MapController center={center} layerData={null} />
      </MapContainer>
    );
  }
  
  return (
    <MapContainer
      center={center}
      zoom={6}
      style={{ width: '100%', height: '100%' }}
      className="leaflet-container"
    >
      <TileLayer
        url="https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png"
        attribution='&copy; Stadia Maps'
      />
      
      <MapController center={center} layerData={layerData} />
      
      <GeoJSON
        key={geoJsonKey}
        data={layerData}
        style={getStyle}
        onEachFeature={onEachFeature}
        pointToLayer={(feature, latlng) => {
          return L.circleMarker(latlng, getStyle(feature));
        }}
      />
      
      <AnimatedMarkers 
        features={layerData.features}
        layerType={layerData.metadata?.layer_type}
      />
    </MapContainer>
  );
};

export default LeafletMap;
