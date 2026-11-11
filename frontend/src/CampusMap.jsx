import { useEffect, useRef, useState } from 'react';
import { Map, NavigationControl, LngLatBounds } from 'maplibre-gl';

export const CampusMap = ({ geojson }) => {
  const mapContainer = useRef(null);
  const mapInstance = useRef(null);
  const [is3D, setIs3D] = useState(false);

  useEffect(() => {
    if (!mapContainer.current) return;

    // Inicialización en vista 2D cenital estricta
    const map = new Map({
      container: mapContainer.current,
      style: 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
      center: [-5.4475, 36.1309],
      zoom: 18, // Zoom elevado adecuado para interiores
      pitch: 0,
      bearing: 0,
    });

    mapInstance.current = map;
    map.addControl(new NavigationControl(), 'top-right');

    map.on('load', () => {
      if (geojson && geojson.features && geojson.features.length > 0) {
        // 1. Inyectar la fuente GeoJSON del plano de interior
        map.addSource('indoor-plan-source', {
          type: 'geojson',
          data: geojson,
        });

        // 2. Capa 2D: Relleno de Habitaciones/Estancias
        map.addLayer({
          id: 'indoor-rooms-fill',
          type: 'fill',
          source: 'indoor-plan-source',
          paint: {
            'fill-color': [
              'match',
              ['get', 'category'],
              'classroom', '#e3f2fd',
              'lab', '#e8f5e9',
              'office', '#fff3e0',
              'corridor', '#f5f5f5',
              '#e0e0e0' // Color por defecto para estancias no categorizadas
            ],
            'fill-opacity': 0.8,
          },
        });

        // 3. Capa 2D: Muros / Delineación de tabiques
        map.addLayer({
          id: 'indoor-walls-line',
          type: 'line',
          source: 'indoor-plan-source',
          paint: {
            'line-color': '#333333',
            'line-width': 2,
          },
        });

        // 4. Capa de Etiquetas (Nombres/Números de Aula)
        map.addLayer({
          id: 'indoor-room-labels',
          type: 'symbol',
          source: 'indoor-plan-source',
          layout: {
            'text-field': ['coalesce', ['get', 'name'], ['get', 'room_number'], ''],
            'text-size': 12,
            'text-anchor': 'center',
          },
          paint: {
            'text-color': '#111111',
            'text-halo-color': '#ffffff',
            'text-halo-width': 1,
          },
        });

        // 5. Capa 3D: Extrusión de Muros y Volúmenes de Interior
        map.addLayer({
          id: 'indoor-3d-extrusion',
          type: 'fill-extrusion',
          source: 'indoor-plan-source',
          layout: {
            visibility: 'none',
          },
          paint: {
            'fill-extrusion-color': [
              'match',
              ['get', 'category'],
              'classroom', '#90caf9',
              'lab', '#a5d6a7',
              'office', '#ffe0b2',
              '#cccccc'
            ],
            'fill-extrusion-opacity': 0.9,
            'fill-extrusion-height': ['coalesce', ['get', 'height'], 3.0], // Altura estándar de planta en metros
            'fill-extrusion-base': ['coalesce', ['get', 'min_height'], 0],
          },
        });

        // Ajustar la cámara automáticamente a la extensión del plano de interior
        const bounds = new LngLatBounds();
        geojson.features.forEach((feature) => {
          if (feature.geometry) {
            if (feature.geometry.type === 'Point') {
              bounds.extend(feature.geometry.coordinates);
            } else if (feature.geometry.type === 'Polygon') {
              feature.geometry.coordinates[0].forEach((coord) => bounds.extend(coord));
            } else if (feature.geometry.type === 'MultiPolygon') {
              feature.geometry.coordinates.forEach((poly) => poly[0].forEach((coord) => bounds.extend(coord)));
            }
          }
        });

        if (!bounds.isEmpty()) {
          map.fitBounds(bounds, { padding: 40, maxZoom: 20 });
        }
      }
    });

    return () => map.remove();
  }, [geojson]);

  const toggle3DMode = () => {
    const map = mapInstance.current;
    if (!map) return;

    if (is3D) {
      map.easeTo({ pitch: 0, bearing: 0, duration: 700 });
      map.setLayoutProperty('indoor-3d-extrusion', 'visibility', 'none');
      map.setLayoutProperty('indoor-rooms-fill', 'visibility', 'visible');
      map.setLayoutProperty('indoor-walls-line', 'visibility', 'visible');
      map.setLayoutProperty('indoor-room-labels', 'visibility', 'visible');
      setIs3D(false);
    } else {
      map.easeTo({ pitch: 60, bearing: -20, duration: 700 });
      map.setLayoutProperty('indoor-rooms-fill', 'visibility', 'none');
      map.setLayoutProperty('indoor-walls-line', 'visibility', 'none');
      map.setLayoutProperty('indoor-room-labels', 'visibility', 'none');
      map.setLayoutProperty('indoor-3d-extrusion', 'visibility', 'visible');
      setIs3D(true);
    }
  };

  return (
    <div style={{ position: 'relative', width: '100%', height: 'calc(100vh - 90px)' }}>
      <button
        onClick={toggle3DMode}
        style={{
          position: 'absolute',
          top: '15px',
          left: '15px',
          zIndex: 10,
          padding: '10px 18px',
          backgroundColor: is3D ? '#007bff' : '#ffffff',
          color: is3D ? '#ffffff' : '#333333',
          border: '1px solid #ccc',
          borderRadius: '20px',
          boxShadow: '0 2px 6px rgba(0,0,0,0.2)',
          cursor: 'pointer',
          fontWeight: 'bold',
          fontSize: '14px',
        }}
      >
        {is3D ? '🏢 Vista 3D (Extrusión Muros)' : '🗺️ Vista 2D (Plano Interior)'}
      </button>

      <div ref={mapContainer} style={{ width: '100%', height: '100%', borderRadius: '8px' }} />
    </div>
  );
};