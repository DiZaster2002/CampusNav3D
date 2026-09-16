
import json
from django.contrib.gis.geos import GEOSGeometry, GEOSException
from rest_framework import serializers
from rest_framework_gis.fields import GeometryField


def ensure_valid_wgs84_geometry(value, field_name='geometry'):
    """Parse and validate a geometry value before saving it to a GIS model."""
    if isinstance(value, GEOSGeometry):
        geometry = value
    elif isinstance(value, str):
        try:
            geometry = GEOSGeometry(value)
        except Exception as exc:
            raise ValueError(f'Invalid {field_name} WKT: {exc}') from exc
    else:
        raise ValueError(f'Unsupported {field_name} type: {type(value).__name__}')

    for coord in _iter_coordinates(geometry):
        if len(coord) < 2:
            raise ValueError(f'Invalid {field_name} coordinate: {coord}')

        lon = coord[0]
        lat = coord[1]
        if not (-180 <= lon <= 180 and -90 <= lat <= 90):
            raise ValueError(
                f'{field_name} contains coordinates outside WGS84 bounds: lon={lon}, lat={lat}'
            )

    return geometry

class CustomGeometryField(GeometryField):
    """
    Campo espacial que serializa geometrías PostGIS a GeoJSON en GET
    y valida la topología GeoJSON / límites WGS84 en POST/PUT.
    """

    def to_internal_value(self, value):
        # 1. Validaciones previas de la estructura GeoJSON
        if isinstance(value, dict) and value.get('type') == 'Polygon':
            coords = value.get('coordinates', [])
            if coords:
                outer_ring = coords[0]

                if len(outer_ring) < 4:
                    raise serializers.ValidationError(
                        f"Geometría inválida: Un polígono requiere al menos 4 puntos. Se enviaron {len(outer_ring)}."
                    )

                if outer_ring[0] != outer_ring[-1]:
                    raise serializers.ValidationError(
                        "Geometría abierta: El primer punto debe ser idéntico al último para cerrar el polígono."
                    )

        # 2. Procesamiento estándar de DRF-GIS para convertir a GEOSGeometry
        try:
            geom = super().to_internal_value(value)
        except (serializers.ValidationError, GEOSException, ValueError):
            raise serializers.ValidationError(
                "Formato GeoJSON no reconocido o estructura espacial corrupta."
            )

        # 3. Comprobación de límites geográficos WGS84
        for coord in _iter_coordinates(geom):
            if len(coord) >= 2:
                lon, lat = coord[0], coord[1]
                if not (-180 <= lon <= 180 and -90 <= lat <= 90):
                    raise serializers.ValidationError(
                        f"Coordenadas fuera de límites WGS84: longitud={lon}, latitud={lat}."
                    )

        return geom


def _iter_coordinates(geometry):
    geom_type = geometry.geom_type
    coords = getattr(geometry, 'coords', None)

    if geom_type in {'Point'}:
        if coords:
            yield coords
    elif geom_type in {'LineString', 'LinearRing'}:
        for point in coords:
            yield point
    elif geom_type == 'Polygon':
        for ring in coords:
            for point in ring:
                yield point
    elif geom_type == 'MultiPoint':
        for point in coords:
            yield point
    elif geom_type == 'MultiLineString':
        for line in coords:
            for point in line:
                yield point
    elif geom_type == 'MultiPolygon':
        for polygon in coords:
            for ring in polygon:
                for point in ring:
                    yield point
    elif geom_type == 'GeometryCollection':
        for part in geometry:
            yield from _iter_coordinates(part)
    else:
        raise ValueError(f'Unsupported geometry type: {geom_type}')
