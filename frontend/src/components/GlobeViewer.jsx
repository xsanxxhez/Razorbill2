import React, { useEffect, useRef } from 'react';
import Globe from 'globe.gl';
import * as THREE from 'three';
import './GlobeViewer.css';

const GlobeViewer = ({ layerData, viewPosition }) => {
  const globeEl = useRef(null);
  const globeInstance = useRef(null);
  
  useEffect(() => {
    if (!globeEl.current) return;
    
    const globe = Globe()
      .globeImageUrl('//unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
      .backgroundImageUrl('//unpkg.com/three-globe/example/img/night-sky.png')
      .pointOfView({ lat: 55.7558, lng: 37.6173, altitude: 2.5 })
      .showAtmosphere(true)
      .atmosphereColor('rgba(100, 200, 255, 0.5)')
      .atmosphereAltitude(0.15);
    
    globe(globeEl.current);
    globeInstance.current = globe;
    
    globe.controls().autoRotate = false;
    globe.controls().autoRotateSpeed = 0.5;
    globe.controls().enableDamping = true;
    globe.controls().dampingFactor = 0.1;
    globe.controls().minDistance = 200;
    globe.controls().maxDistance = 800;
    
    return () => {
      if (globeInstance.current) {
        globeInstance.current = null;
      }
    };
  }, []);
  
  useEffect(() => {
    if (!globeInstance.current || !layerData || !layerData.features) return;
    
    const globe = globeInstance.current;
    const layerType = layerData.metadata?.layer_type;
    
    globe.polygonsData([]);
    globe.pointsData([]);
    globe.pathsData([]);
    globe.arcsData([]);
    
    if (layerType === 'temperature' || layerType === 'weather' || layerType === 'density' || layerType === 'population') {
      const polygons = layerData.features.map(feature => ({
        ...feature,
        value: feature.properties?.temperature || feature.properties?.value || 0
      }));
      
      globe.polygonsData(polygons)
        .polygonCapColor(d => {
          const value = d.value;
          if (layerType === 'temperature' || layerType === 'weather') {
            if (value < 0) return 'rgba(0, 153, 255, 0.7)';
            if (value < 10) return 'rgba(0, 255, 255, 0.7)';
            if (value < 20) return 'rgba(0, 255, 0, 0.7)';
            if (value < 30) return 'rgba(255, 255, 0, 0.7)';
            return 'rgba(255, 153, 0, 0.7)';
          } else {
            if (value < 50) return 'rgba(161, 218, 180, 0.7)';
            if (value < 100) return 'rgba(65, 182, 196, 0.7)';
            if (value < 200) return 'rgba(44, 127, 184, 0.7)';
            return 'rgba(37, 52, 148, 0.7)';
          }
        })
        .polygonSideColor(() => 'rgba(100, 100, 100, 0.3)')
        .polygonStrokeColor(() => 'rgba(255, 255, 255, 0.5)')
        .polygonAltitude(d => {
          const value = d.value;
          if (layerType === 'temperature' || layerType === 'weather') {
            return Math.abs(value) * 0.0005;
          } else {
            return value * 0.00001;
          }
        })
        .polygonLabel(d => {
          const props = d.properties;
          if (layerType === 'temperature' || layerType === 'weather') {
            return `<div style="background: rgba(0,0,0,0.8); padding: 8px; border-radius: 4px;">
              <strong>🌡️ ${props.temperature}°C</strong>
              ${props.wind_speed ? '<br/>💨 Wind: ' + props.wind_speed + ' km/h' : ''}
            </div>`;
          } else {
            return `<div style="background: rgba(0,0,0,0.8); padding: 8px; border-radius: 4px;">
              <strong>👥 ${props.formatted || props.value}</strong>
              ${props.region ? '<br/>📍 ' + props.region : ''}
            </div>`;
          }
        });
    } else if (layerType === 'earthquakes') {
      const points = layerData.features
        .filter(f => f.geometry.type === 'Point')
        .map(f => ({
          lat: f.geometry.coordinates[1],
          lng: f.geometry.coordinates[0],
          magnitude: f.properties.magnitude || 0,
          location: f.properties.location,
          time: f.properties.time_readable
        }));
      
      globe.pointsData(points)
        .pointLat('lat')
        .pointLng('lng')
        .pointColor(d => {
          const mag = d.magnitude;
          if (mag > 6) return 'rgba(255, 0, 0, 0.9)';
          if (mag > 5) return 'rgba(255, 102, 0, 0.9)';
          if (mag > 4) return 'rgba(255, 170, 0, 0.9)';
          return 'rgba(255, 255, 0, 0.9)';
        })
        .pointAltitude(d => d.magnitude * 0.01)
        .pointRadius(d => d.magnitude * 0.5)
        .pointLabel(d => `<div style="background: rgba(255,0,0,0.8); padding: 8px; border-radius: 4px;">
          <strong>🌍 M ${d.magnitude}</strong>
          <br/>📍 ${d.location}
          <br/>🕐 ${d.time}
        </div>`);
    } else if (layerType === 'roads') {
      const paths = layerData.features
        .filter(f => f.geometry.type === 'LineString')
        .map(f => ({
          coords: f.geometry.coordinates.map(c => [c[1], c[0]]),
          highway: f.properties.highway || 'residential'
        }));
      
      globe.pathsData(paths)
        .pathPoints('coords')
        .pathPointLat(p => p[0])
        .pathPointLng(p => p[1])
        .pathColor(d => {
          if (d.highway === 'motorway') return 'rgba(255, 0, 102, 0.8)';
          if (d.highway === 'trunk') return 'rgba(255, 51, 102, 0.8)';
          if (d.highway === 'primary') return 'rgba(255, 102, 153, 0.8)';
          return 'rgba(102, 204, 255, 0.8)';
        })
        .pathStroke(d => {
          if (d.highway === 'motorway') return 3;
          if (d.highway === 'trunk') return 2.5;
          return 2;
        });
    } else if (layerType === 'parks' || layerType === 'forests') {
      const polygons = layerData.features;
      
      globe.polygonsData(polygons)
        .polygonCapColor(() => 'rgba(0, 255, 102, 0.6)')
        .polygonSideColor(() => 'rgba(0, 204, 68, 0.3)')
        .polygonStrokeColor(() => 'rgba(0, 204, 68, 0.5)')
        .polygonAltitude(0.001);
    } else if (layerType === 'water' || layerType === 'rivers') {
      const polygons = layerData.features;
      
      globe.polygonsData(polygons)
        .polygonCapColor(() => 'rgba(0, 204, 255, 0.6)')
        .polygonSideColor(() => 'rgba(0, 153, 255, 0.3)')
        .polygonStrokeColor(() => 'rgba(0, 153, 255, 0.5)')
        .polygonAltitude(0.001);
    }
    
    if (layerData.metadata?.center) {
      const [lng, lat] = layerData.metadata.center;
      globe.pointOfView({ lat, lng, altitude: 1.5 }, 2000);
    }
    
  }, [layerData]);
  
  useEffect(() => {
    if (!globeInstance.current || !viewPosition) return;
    
    globeInstance.current.pointOfView({
      lat: viewPosition.latitude,
      lng: viewPosition.longitude,
      altitude: 1.5
    }, 2000);
  }, [viewPosition]);
  
  return (
    <div 
      ref={globeEl} 
      style={{ width: '100%', height: '100%', background: '#000' }}
      className="globe-container"
    />
  );
};

export default GlobeViewer;
