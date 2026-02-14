import React, { useEffect, useRef } from 'react';
import * as Cesium from 'cesium';
import 'cesium/Build/Cesium/Widgets/widgets.css';
import './CesiumViewer.css';

const CESIUM_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI1NmM3YzI1Ny1lYzJmLTQ4NDctODkxYy1lOGIxYzBjM2Y1MGUiLCJpZCI6MzU1OTI4LCJpYXQiOjE3NjE5MzkwNTB9.weoUsRzbGeeHVwQJvIj4yzpN8LX-jgTn1RmN363xCW4";

const CesiumViewer = ({ layerData, viewPosition }) => {
  const cesiumContainer = useRef(null);
  const viewerRef = useRef(null);
  const dataSourceRef = useRef(null);
  const isInitialized = useRef(false);

  // Initialize Cesium viewer once
  useEffect(() => {
    if (isInitialized.current || !cesiumContainer.current) return;

    isInitialized.current = true;

    try {
      Cesium.Ion.defaultAccessToken = CESIUM_TOKEN;

      viewerRef.current = new Cesium.Viewer(cesiumContainer.current, {
        animation: false,
        timeline: false,
        baseLayerPicker: true,
        geocoder: false,
        homeButton: true,
        sceneModePicker: true,
        navigationHelpButton: false,
        fullscreenButton: true,
        terrain: Cesium.Terrain.fromWorldTerrain({
          requestWaterMask: true,
          requestVertexNormals: true
        })
      });

      viewerRef.current.scene.globe.enableLighting = true;
      viewerRef.current.scene.globe.depthTestAgainstTerrain = true;

      viewerRef.current.camera.setView({
        destination: Cesium.Cartesian3.fromDegrees(37.6173, 55.7558, 15000000),
      });

      console.log('✅ Cesium initialized');
    } catch (error) {
      console.error('❌ Cesium initialization failed:', error);
      isInitialized.current = false;
    }

    return () => {
      if (viewerRef.current && !viewerRef.current.isDestroyed()) {
        console.log('🗑️ Cleaning up Cesium');
        viewerRef.current.destroy();
        viewerRef.current = null;
        isInitialized.current = false;
      }
    };
  }, []);

  // Handle layer data updates
  useEffect(() => {
    if (!viewerRef.current || !layerData) return;

    // Remove previous data source
    if (dataSourceRef.current) {
      viewerRef.current.dataSources.remove(dataSourceRef.current);
      dataSourceRef.current = null;
    }

    const layerType = layerData.metadata?.layer_type;

    const promise = Cesium.GeoJsonDataSource.load(layerData, {
      stroke: Cesium.Color.WHITE.withAlpha(0.8),
      strokeWidth: 3,
      fill: Cesium.Color.CYAN.withAlpha(0.6),
      clampToGround: true
    });

    promise.then(dataSource => {
      if (!viewerRef.current) return;

      viewerRef.current.dataSources.add(dataSource);
      dataSourceRef.current = dataSource;

      const entities = dataSource.entities.values;

      entities.forEach(entity => {
        const properties = entity.properties;

        // WEATHER GRID (rectangles/hexagons with temperature)
        if (layerType === 'weather' || layerType === 'temperature') {
          const temp = properties?.temperature?._value || 20;
          const type = properties?.type?._value;
          let color;

          if (temp < 0) color = Cesium.Color.BLUE;
          else if (temp < 10) color = Cesium.Color.CYAN;
          else if (temp < 20) color = Cesium.Color.GREEN;
          else if (temp < 30) color = Cesium.Color.YELLOW;
          else color = Cesium.Color.ORANGE;

          if (entity.polygon && type === 'weather_cell') {
            entity.polygon.material = color.withAlpha(0.7);
            entity.polygon.extrudedHeight = Math.abs(temp) * 1000;
            entity.polygon.outline = true;
            entity.polygon.outlineColor = Cesium.Color.WHITE;
            entity.polygon.outlineWidth = 1;
          }

          if (entity.point) {
            entity.point.pixelSize = 20;
            entity.point.color = color;
            entity.point.outlineColor = Cesium.Color.WHITE;
            entity.point.outlineWidth = 2;
          }

          entity.description = `
            <div style="font-family: monospace; padding: 10px;">
              <strong>Temperature:</strong> ${temp}°C<br/>
              ${properties?.wind_speed?._value ? `<strong>Wind:</strong> ${properties.wind_speed._value} km/h` : ''}
            </div>
          `;
        }

        // COUNTRY BOUNDARIES (polygons with area/perimeter)
        else if (layerType === 'country') {
          const type = properties?.type?._value;

          // Country boundary polygon
          if (entity.polygon && type === 'boundary') {
            entity.polygon.material = Cesium.Color.CYAN.withAlpha(0.3);
            entity.polygon.outline = true;
            entity.polygon.outlineColor = Cesium.Color.WHITE;
            entity.polygon.outlineWidth = 3;
            entity.polygon.extrudedHeight = 0;
          }

          // Country center marker
          if (entity.point && type === 'marker') {
            entity.point.pixelSize = 30;
            entity.point.color = Cesium.Color.CYAN;
            entity.point.outlineColor = Cesium.Color.WHITE;
            entity.point.outlineWidth = 3;
          }

          const name = properties?.name?._value || 'Country';
          const area = properties?.area?._value || 0;
          const perimeter = properties?.perimeter?._value || 0;
          const population = properties?.population?._value || 0;
          const capital = properties?.capital?._value || '';
          const flag = properties?.flag?._value || '';

          entity.description = `
            <div style="font-family: monospace; padding: 10px;">
              ${flag ? `<div style="font-size: 40px; margin-bottom: 10px;">${flag}</div>` : ''}
              <strong>${name}</strong><br/>
              ${capital ? `<strong>Capital:</strong> ${capital}<br/>` : ''}
              ${area ? `<strong>Area:</strong> ${area.toLocaleString()} km²<br/>` : ''}
              ${perimeter ? `<strong>Perimeter:</strong> ~${perimeter.toLocaleString()} km<br/>` : ''}
              ${population ? `<strong>Population:</strong> ${population.toLocaleString()}` : ''}
            </div>
          `;
        }

        // EARTHQUAKES (elevated points)
        else if (layerType === 'earthquakes') {
          const mag = properties?.magnitude?._value || properties?.mag?._value || 0;
          let color;

          if (mag > 6) color = Cesium.Color.RED;
          else if (mag > 5) color = Cesium.Color.ORANGE;
          else if (mag > 4) color = Cesium.Color.YELLOW;
          else color = Cesium.Color.WHITE;

          if (entity.point) {
            entity.point.pixelSize = mag * 5;
            entity.point.color = color;
            entity.point.outlineColor = Cesium.Color.WHITE;
            entity.point.outlineWidth = 2;
          }

          if (entity.position) {
            const cartographic = Cesium.Cartographic.fromCartesian(entity.position._value);
            const newPosition = Cesium.Cartesian3.fromRadians(
              cartographic.longitude,
              cartographic.latitude,
              mag * 10000
            );
            entity.position = newPosition;
          }

          entity.description = `
            <div style="font-family: monospace; padding: 10px;">
              <strong>Magnitude:</strong> ${mag}<br/>
              ${properties?.place?._value ? `<strong>Location:</strong> ${properties.place._value}` : ''}
            </div>
          `;
        }

        // POPULATION DENSITY (extruded polygons)
        else if (layerType === 'density' || layerType === 'population') {
          const value = properties?.value?._value || 0;
          let color;

          if (value < 50) color = Cesium.Color.LIGHTGREEN;
          else if (value < 100) color = Cesium.Color.YELLOW;
          else if (value < 200) color = Cesium.Color.ORANGE;
          else color = Cesium.Color.RED;

          if (entity.polygon) {
            entity.polygon.material = color.withAlpha(0.7);
            entity.polygon.extrudedHeight = value * 50;
            entity.polygon.outline = true;
            entity.polygon.outlineColor = Cesium.Color.WHITE;
          }

          entity.description = `
            <div style="font-family: monospace; padding: 10px;">
              <strong>${properties?.formatted?._value || value}</strong><br/>
              ${properties?.region?._value ? `<strong>Region:</strong> ${properties.region._value}` : ''}
            </div>
          `;
        }

        // ROADS (polylines with different colors)
        else if (layerType === 'roads') {
          const highway = properties?.highway?._value || 'residential';
          let color, width;

          if (highway === 'motorway') {
            color = Cesium.Color.RED;
            width = 5;
          } else if (highway === 'trunk') {
            color = Cesium.Color.ORANGE;
            width = 4;
          } else if (highway === 'primary') {
            color = Cesium.Color.YELLOW;
            width = 3;
          } else {
            color = Cesium.Color.WHITE;
            width = 2;
          }

          if (entity.polyline) {
            entity.polyline.material = color;
            entity.polyline.width = width;
            entity.polyline.clampToGround = true;
          }
        }

        // PARKS/FORESTS (green polygons)
        else if (layerType === 'parks' || layerType === 'forests') {
          if (entity.polygon) {
            entity.polygon.material = Cesium.Color.GREEN.withAlpha(0.6);
            entity.polygon.outline = true;
            entity.polygon.outlineColor = Cesium.Color.DARKGREEN;
          }
        }

        // WATER/RIVERS (blue polygons)
        else if (layerType === 'water' || layerType === 'rivers') {
          if (entity.polygon) {
            entity.polygon.material = Cesium.Color.BLUE.withAlpha(0.6);
            entity.polygon.outline = true;
            entity.polygon.outlineColor = Cesium.Color.DARKBLUE;
          }
        }

        // LOCATION MARKER (simple point)
        else if (layerType === 'location') {
          if (entity.point) {
            entity.point.pixelSize = 30;
            entity.point.color = Cesium.Color.CYAN;
            entity.point.outlineColor = Cesium.Color.WHITE;
            entity.point.outlineWidth = 3;
          }

          const name = properties?.name?._value || properties?.display_name?._value || 'Location';

          entity.description = `
            <div style="font-family: monospace; padding: 10px;">
              <strong>${name}</strong>
            </div>
          `;
        }
      });

      // Fly to the data
      viewerRef.current.flyTo(dataSource, {
        duration: 2,
        offset: new Cesium.HeadingPitchRange(
          0,
          Cesium.Math.toRadians(-45),
          layerType === 'roads' ? 50000 : layerType === 'weather' ? 200000 : 500000
        )
      });
    }).catch(error => {
      console.error('❌ GeoJSON loading error:', error);
    });

  }, [layerData]);

  // Handle camera positioning
  useEffect(() => {
    if (!viewerRef.current || !viewPosition) return;

    const lon = viewPosition.longitude;
    const lat = viewPosition.latitude;

    if (typeof lon === 'number' && typeof lat === 'number' &&
        !isNaN(lon) && !isNaN(lat)) {
      viewerRef.current.camera.flyTo({
        destination: Cesium.Cartesian3.fromDegrees(lon, lat, 500000),
        duration: 2
      });
    } else {
      console.warn('⚠️ Invalid viewPosition:', viewPosition);
    }
  }, [viewPosition]);

  return (
    <div
      ref={cesiumContainer}
      style={{ width: '100%', height: '100%' }}
      className="cesium-container"
    />
  );
};

export default CesiumViewer;
