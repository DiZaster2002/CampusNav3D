from django.contrib.gis.geos import GEOSGeometry


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
