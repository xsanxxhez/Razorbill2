import React, { useEffect, useRef } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import './MapLibreViewer.css';

const MapLibreViewer = ({ layerData, viewPosition }) => {
  const mapContainer = useRef(null);
  const map = useRef(null);
  const currentSourceId = useRef(null);
  
  useEffect(() => {
    if (map.current) return;
    
    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        sources: {
          'osm': {
            type: 'raster',
            tiles: [
              'https://a.tile.openstreetmap.org/{z}/{x}/{y}.png',
              'https://b.tile.openstreetmap.org/{z}/{x}/{y}.png',
              'https://c.tile.openstreetmap.org/{z}/{x}/{y}.png'
            ],
            tileSize: 256,
            attribution: '© OpenStreetMap contributors'
          }
        },
        layers: [
          {
            id: 'background',
            type: 'background',
            paint: {
              'background-color': '#1a1a1a'
            }
          },
          {
            id: 'osm-tiles',
            type: 'raster',
            source: 'osm',
            paint: {
              'raster-opacity': 0.8,
              'raster-brightness-min': 0.3,
              'raster-brightness-max': 0.6,
              'raster-contrast': 0.2,
              'raster-saturation': -0.8
            }
          }
        ]
      },
      center: [37.6173, 55.7558],
      zoom: 3,
      pitch: 45,
      bearing: 0
    });
    
    map.current.addControl(new maplibregl.NavigationControl(), 'top-right');
    
    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, []);
  
  useEffect(() => {
    if (!map.current || !map.current.loaded()) return;
    
    const updateLayers = () => {
      if (!layerData || !layerData.features || layerData.features.length === 0) return;
      
      if (currentSourceId.current) {
        const layers = map.current.getStyle().layers;
        layers.forEach(layer => {
          if (layer.id.startsWith('data-')) {
            if (map.current.getLayer(layer.id)) {
              map.current.removeLayer(layer.id);
            }
          }
        });
        
        if (map.current.getSource(currentSourceId.current)) {
          map.current.removeSource(currentSourceId.current);
        }
      }
      
      const sourceId = `data-${Date.now()}`;
      currentSourceId.current = sourceId;
      
      map.current.addSource(sourceId, {
        type: 'geojson',
        data: layerData
      });
      
      const layerType = layerData.metadata?.layer_type;
      
      if (layerType === 'temperature' || layerType === 'weather') {
        map.current.addLayer({
          id: `${sourceId}-fill`,
          type: 'fill',
          source: sourceId,
          paint: {
            'fill-color': [
              'interpolate',
              ['linear'],
              ['coalesce', ['get', 'temperature'], 20],
              -10, '#0033ff',
              0, '#0099ff',
              10, '#00ffff',
              20, '#00ff00',
              30, '#ffff00',
              40, '#ff9900',
              50, '#ff0000'
            ],
            'fill-opacity': 0.7
          }
        });
      } else if (layerType === 'density' || layerType === 'population') {
        map.current.addLayer({
          id: `${sourceId}-fill`,
          type: 'fill',
          source: sourceId,
          paint: {
            'fill-color': [
              'interpolate',
              ['linear'],
              ['coalesce', ['get', 'value'], 0],
              0, '#ffffcc',
              50, '#a1dab4',
              100, '#41b6c4',
              200, '#2c7fb8',
              500, '#253494',
              1000, '#081d58'
            ],
            'fill-opacity': 0.7
          }
        });
        
        map.current.addLayer({
          id: `${sourceId}-outline`,
          type: 'line',
          source: sourceId,
          paint: {
            'line-color': '#ffffff',
            'line-width': 1,
            'line-opacity': 0.5
          }
        });
      } else if (layerType === 'earthquakes') {
        map.current.addLayer({
          id: `${sourceId}-circle`,
          type: 'circle',
          source: sourceId,
          filter: ['==', ['geometry-type'], 'Point'],
          paint: {
            'circle-radius': [
              'interpolate',
              ['linear'],
              ['coalesce', ['get', 'magnitude'], 2],
              2, 5,
              4, 10,
              6, 20,
              8, 40
            ],
            'circle-color': [
              'interpolate',
              ['linear'],
              ['coalesce', ['get', 'magnitude'], 2],
              2, '#ffff00',
              4, '#ffaa00',
              5, '#ff6600',
              6, '#ff0000'
            ],
            'circle-opacity': 0.7,
            'circle-stroke-color': '#ffffff',
            'circle-stroke-width': 2
          }
        });
      } else if (layerType === 'roads') {
        map.current.addLayer({
          id: `${sourceId}-line`,
          type: 'line',
          source: sourceId,
          paint: {
            'line-color': [
              'match',
              ['get', 'highway'],
              'motorway', '#ff0066',
              'trunk', '#ff3366',
              'primary', '#ff6699',
              'secondary', '#ff99cc',
              '#66ccff'
            ],
            'line-width': [
              'match',
              ['get', 'highway'],
              'motorway', 4,
              'trunk', 3,
              'primary', 2.5,
              2
            ],
            'line-opacity': 0.9
          }
        });
      } else if (layerType === 'parks' || layerType === 'forests') {
        map.current.addLayer({
          id: `${sourceId}-fill`,
          type: 'fill',
          source: sourceId,
          paint: {
            'fill-color': '#00ff66',
            'fill-opacity': 0.5
          }
        });
      } else if (layerType === 'water' || layerType === 'rivers') {
        map.current.addLayer({
          id: `${sourceId}-fill`,
          type: 'fill',
          source: sourceId,
          paint: {
            'fill-color': '#00ccff',
            'fill-opacity': 0.6
          }
        });
      } else {
        map.current.addLayer({
          id: `${sourceId}-fill`,
          type: 'fill',
          source: sourceId,
          paint: {
            'fill-color': '#64c8ff',
            'fill-opacity': 0.5
          }
        });
      }
      
      const bounds = new maplibregl.LngLatBounds();
      let hasCoordinates = false;
      
      layerData.features.forEach(feature => {
        try {
          if (feature.geometry.type === 'Point') {
            bounds.extend(feature.geometry.coordinates);
            hasCoordinates = true;
          } else if (feature.geometry.type === 'LineString') {
            feature.geometry.coordinates.forEach(coord => {
              bounds.extend(coord);
              hasCoordinates = true;
            });
          } else if (feature.geometry.type === 'Polygon') {
            feature.geometry.coordinates[0].forEach(coord => {
              bounds.extend(coord);
              hasCoordinates = true;
            });
          } else if (feature.geometry.type === 'MultiPolygon') {
            feature.geometry.coordinates.forEach(polygon => {
              polygon[0].forEach(coord => {
                bounds.extend(coord);
                hasCoordinates = true;
              });
            });
          }
        } catch (e) {
          console.warn('Error processing feature:', e);
        }
      });
      
      if (hasCoordinates && !bounds.isEmpty()) {
        map.current.fitBounds(bounds, {
          padding: 50,
          duration: 1500,
          pitch: layerType === 'temperature' || layerType === 'density' ? 30 : 45
        });
      }
      
      map.current.on('click', `${sourceId}-fill`, (e) => {
        if (!e.features || !e.features[0]) return;
        
        const props = e.features[0].properties;
        const layerType = layerData.metadata?.layer_type;
        
        let html = '<div style="color: #000; font-family: monospace; font-size: 12px;">';
        
        if (layerType === 'temperature' || layerType === 'weather') {
          html += `<strong>🌡️ ${props.temperature}°C</strong>`;
          if (props.wind_speed) html += `<br/>💨 Wind: ${props.wind_speed} km/h`;
        } else if (layerType === 'density' || layerType === 'population') {
          html += `<strong>👥 ${props.formatted || props.value}</strong>`;
          if (props.region) html += `<br/>📍 ${props.region}`;
        } else {
          const entries = Object.entries(props).slice(0, 3);
          html += entries.map(([k, v]) => `<strong>${k}:</strong> ${v}`).join('<br/>');
        }
        
        html += '</div>';
        
        new maplibregl.Popup()
          .setLngLat(e.lngLat)
          .setHTML(html)
          .addTo(map.current);
      });
      
      map.current.on('click', `${sourceId}-circle`, (e) => {
        if (!e.features || !e.features[0]) return;
        
        const props = e.features[0].properties;
        
        let html = '<div style="color: #000; font-family: monospace; font-size: 12px;">';
        html += `<strong>🌍 M ${props.magnitude}</strong>`;
        if (props.location) html += `<br/>📍 ${props.location}`;
        if (props.time_readable) html += `<br/>🕐 ${props.time_readable}`;
        html += '</div>';
        
        new maplibregl.Popup()
          .setLngLat(e.lngLat)
          .setHTML(html)
          .addTo(map.current);
      });
      
      map.current.on('mouseenter', `${sourceId}-fill`, () => {
        map.current.getCanvas().style.cursor = 'pointer';
      });
      
      map.current.on('mouseleave', `${sourceId}-fill`, () => {
        map.current.getCanvas().style.cursor = '';
      });
      
      if (map.current.getLayer(`${sourceId}-circle`)) {
        map.current.on('mouseenter', `${sourceId}-circle`, () => {
          map.current.getCanvas().style.cursor = 'pointer';
        });
        
        map.current.on('mouseleave', `${sourceId}-circle`, () => {
          map.current.getCanvas().style.cursor = '';
        });
      }
    };
    
    if (map.current.loaded()) {
      updateLayers();
    } else {
      map.current.once('load', updateLayers);
    }
    
  }, [layerData]);
  
  useEffect(() => {
    if (!map.current || !viewPosition) return;
    
    map.current.flyTo({
      center: [viewPosition.longitude, viewPosition.latitude],
      zoom: 8,
      duration: 2000
    });
  }, [viewPosition]);
  
  return <div ref={mapContainer} style={{ width: '100%', height: '100%' }} className="maplibre-container" />;
};

export default MapLibreViewer;
