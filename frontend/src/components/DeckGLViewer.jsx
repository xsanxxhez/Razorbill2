import React, { useState, useEffect } from 'react';
import DeckGL from '@deck.gl/react';
import { GeoJsonLayer, ScatterplotLayer, ColumnLayer } from '@deck.gl/layers';
import './DeckGLViewer.css';

const INITIAL_VIEW_STATE = {
  longitude: 37.6173,
  latitude: 55.7558,
  zoom: 3,
  pitch: 45,
  bearing: 0,
  maxZoom: 20,
  minZoom: 0
};

const DeckGLViewer = ({ layerData, viewPosition }) => {
  const [viewState, setViewState] = useState(INITIAL_VIEW_STATE);
  const [layers, setLayers] = useState([]);
  
  useEffect(() => {
    if (!layerData || !layerData.features || layerData.features.length === 0) {
      setLayers([]);
      return;
    }
    
    const layerType = layerData.metadata?.layer_type;
    const newLayers = [];
    
    if (layerType === 'temperature' || layerType === 'weather') {
      newLayers.push(
        new GeoJsonLayer({
          id: 'temperature-polygons',
          data: layerData,
          filled: true,
          stroked: true,
          extruded: true,
          wireframe: false,
          getFillColor: f => {
            const temp = f.properties.temperature || 20;
            if (temp < -10) return [0, 51, 255, 200];
            if (temp < 0) return [0, 153, 255, 200];
            if (temp < 10) return [0, 255, 255, 200];
            if (temp < 20) return [0, 255, 0, 200];
            if (temp < 30) return [255, 255, 0, 200];
            if (temp < 40) return [255, 153, 0, 200];
            return [255, 0, 0, 200];
          },
          getLineColor: [255, 255, 255, 100],
          getLineWidth: 100,
          getElevation: f => Math.abs(f.properties.temperature || 0) * 5000,
          elevationScale: 1,
          pickable: true,
          autoHighlight: true,
          highlightColor: [255, 255, 255, 100]
        })
      );
    } else if (layerType === 'density' || layerType === 'population') {
      newLayers.push(
        new GeoJsonLayer({
          id: 'density-polygons',
          data: layerData,
          filled: true,
          stroked: true,
          extruded: true,
          wireframe: false,
          getFillColor: f => {
            const value = f.properties.value || 0;
            if (value < 10) return [255, 255, 204, 220];
            if (value < 50) return [161, 218, 180, 220];
            if (value < 100) return [65, 182, 196, 220];
            if (value < 200) return [44, 127, 184, 220];
            if (value < 500) return [37, 52, 148, 220];
            return [8, 29, 88, 220];
          },
          getLineColor: [255, 255, 255, 150],
          getLineWidth: 200,
          getElevation: f => (f.properties.value || 0) * 100,
          elevationScale: 1,
          pickable: true,
          autoHighlight: true,
          highlightColor: [255, 255, 255, 100]
        })
      );
    } else if (layerType === 'earthquakes') {
      const points = layerData.features
        .filter(f => f.geometry.type === 'Point')
        .map(f => ({
          position: f.geometry.coordinates,
          magnitude: f.properties.magnitude || 0,
          location: f.properties.location,
          time: f.properties.time_readable
        }));
      
      newLayers.push(
        new ScatterplotLayer({
          id: 'earthquakes-scatter',
          data: points,
          pickable: true,
          opacity: 0.8,
          stroked: true,
          filled: true,
          radiusScale: 1000,
          radiusMinPixels: 5,
          radiusMaxPixels: 100,
          lineWidthMinPixels: 2,
          getPosition: d => d.position,
          getRadius: d => Math.pow(10, d.magnitude) * 50,
          getFillColor: d => {
            const mag = d.magnitude;
            if (mag > 6) return [255, 0, 0, 220];
            if (mag > 5) return [255, 102, 0, 220];
            if (mag > 4) return [255, 170, 0, 220];
            return [255, 255, 0, 220];
          },
          getLineColor: [255, 255, 255, 255]
        }),
        new ColumnLayer({
          id: 'earthquakes-columns',
          data: points,
          diskResolution: 20,
          radius: 15000,
          extruded: true,
          pickable: true,
          elevationScale: 8000,
          getPosition: d => d.position,
          getFillColor: d => {
            const mag = d.magnitude;
            if (mag > 6) return [255, 0, 0, 200];
            if (mag > 5) return [255, 102, 0, 200];
            if (mag > 4) return [255, 170, 0, 200];
            return [255, 255, 0, 200];
          },
          getLineColor: [255, 255, 255, 100],
          getElevation: d => d.magnitude * 5000
        })
      );
    } else if (layerType === 'roads') {
      newLayers.push(
        new GeoJsonLayer({
          id: 'roads-lines',
          data: layerData,
          filled: false,
          stroked: true,
          getLineColor: f => {
            const highway = f.properties.highway || 'residential';
            if (highway === 'motorway') return [255, 0, 102, 255];
            if (highway === 'trunk') return [255, 51, 102, 255];
            if (highway === 'primary') return [255, 102, 153, 255];
            if (highway === 'secondary') return [255, 153, 204, 255];
            return [102, 204, 255, 255];
          },
          getLineWidth: f => {
            const highway = f.properties.highway || 'residential';
            if (highway === 'motorway') return 8;
            if (highway === 'trunk') return 6;
            if (highway === 'primary') return 4;
            return 2;
          },
          lineWidthMinPixels: 2,
          lineWidthMaxPixels: 10,
          pickable: true
        })
      );
    } else if (layerType === 'parks' || layerType === 'forests') {
      newLayers.push(
        new GeoJsonLayer({
          id: 'parks-polygons',
          data: layerData,
          filled: true,
          stroked: true,
          getFillColor: [0, 255, 102, 180],
          getLineColor: [0, 204, 68, 255],
          getLineWidth: 2,
          lineWidthMinPixels: 1,
          pickable: true
        })
      );
    } else if (layerType === 'water' || layerType === 'rivers') {
      newLayers.push(
        new GeoJsonLayer({
          id: 'water-polygons',
          data: layerData,
          filled: true,
          stroked: true,
          getFillColor: [0, 204, 255, 180],
          getLineColor: [0, 153, 255, 255],
          getLineWidth: 2,
          lineWidthMinPixels: 1,
          pickable: true
        })
      );
    } else {
      newLayers.push(
        new GeoJsonLayer({
          id: 'default-layer',
          data: layerData,
          filled: true,
          stroked: true,
          getFillColor: [100, 200, 255, 180],
          getLineColor: [255, 255, 255, 100],
          getLineWidth: 1,
          lineWidthMinPixels: 1,
          pickable: true
        })
      );
    }
    
    setLayers(newLayers);
    
    if (layerData.metadata?.center) {
      const [lon, lat] = layerData.metadata.center;
      setViewState(prev => ({
        ...prev,
        longitude: lon,
        latitude: lat,
        zoom: 8,
        transitionDuration: 1500
      }));
    }
  }, [layerData]);
  
  useEffect(() => {
    if (viewPosition) {
      setViewState(prev => ({
        ...prev,
        longitude: viewPosition.longitude,
        latitude: viewPosition.latitude,
        zoom: 9,
        transitionDuration: 1500
      }));
    }
  }, [viewPosition]);
  
  const getTooltip = ({ object }) => {
    if (!object) return null;
    
    const props = object.properties || object;
    const layerType = layerData?.metadata?.layer_type;
    
    if (layerType === 'temperature' || layerType === 'weather') {
      return {
        html: `<div style="background: rgba(0,0,0,0.9); color: #fff; padding: 10px; border-radius: 6px; font-family: monospace; font-size: 13px;">
          <strong>🌡️ ${props.temperature || object.temperature}°C</strong>
          ${props.wind_speed ? '<br/>💨 Wind: ' + props.wind_speed + ' km/h' : ''}
        </div>`
      };
    } else if (layerType === 'density' || layerType === 'population') {
      return {
        html: `<div style="background: rgba(0,0,0,0.9); color: #fff; padding: 10px; border-radius: 6px; font-family: monospace; font-size: 13px;">
          <strong>👥 ${props.formatted || props.value}</strong>
          ${props.region ? '<br/>📍 ' + props.region : ''}
        </div>`
      };
    } else if (layerType === 'earthquakes') {
      const mag = props.magnitude || object.magnitude;
      return {
        html: `<div style="background: rgba(255,0,0,0.9); color: #fff; padding: 10px; border-radius: 6px; font-family: monospace; font-size: 13px;">
          <strong>🌍 Magnitude ${mag}</strong>
          ${props.location || object.location ? '<br/>📍 ' + (props.location || object.location) : ''}
          ${props.time || object.time ? '<br/>🕐 ' + (props.time || object.time) : ''}
        </div>`
      };
    }
    
    return null;
  };
  
  return (
    <div style={{ position: 'relative', width: '100%', height: '100%', background: '#000' }}>
      <DeckGL
        initialViewState={INITIAL_VIEW_STATE}
        viewState={viewState}
        onViewStateChange={({ viewState }) => setViewState(viewState)}
        controller={true}
        layers={layers}
        getTooltip={getTooltip}
        parameters={{
          clearColor: [0, 0, 0, 1],
          depthTest: true,
          blend: true,
          blendFunc: ['SRC_ALPHA', 'ONE_MINUS_SRC_ALPHA']
        }}
        glOptions={{
          webgl2: false,
          powerPreference: 'high-performance'
        }}
      />
    </div>
  );
};

export default DeckGLViewer;
