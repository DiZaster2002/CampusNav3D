import json
from django.contrib.gis.geos import GEOSGeometry

class SpatialEntityFactory:
    """
    Fábrica estrictamente alineada con OCP. 
    Cerrada a modificación: no contiene condicionales para tipar entidades.
    Abierta a extensión: se pueden registrar nuevos creadores dinámicamente.
    """
    _registry = {}

    @classmethod
    def register(cls, entity_type: str):
        """Decorador para registrar nuevos creadores sin tocar esta clase."""
        def decorator(creator_class):
            cls._registry[entity_type.lower()] = creator_class
            return creator_class
        return decorator

    @classmethod
    def create(cls, entity_type: str, **kwargs):
        # Normalización geoespacial centralizada
        if 'geometry' in kwargs and isinstance(kwargs['geometry'], (str, dict)):
            geom_data = kwargs['geometry']
            if isinstance(geom_data, dict):
                geom_data = json.dumps(geom_data)
            kwargs['geometry'] = GEOSGeometry(geom_data)

        creator = cls._registry.get(entity_type.lower())
        if not creator:
            raise ValueError(f"El tipo de entidad '{entity_type}' no está registrado en la fábrica.")
        
        return creator.execute_creation(**kwargs)


# --- CREADORES REGISTRADOS (Estrategias Polymórficas) ---

class BaseCreator:
    @staticmethod
    def execute_creation(**kwargs):
        raise NotImplementedError

@SpatialEntityFactory.register('campus')
class CampusCreator(BaseCreator):
    @staticmethod
    def execute_creation(**kwargs):
        from maps.models import Campus
        from django.utils.text import slugify
        if 'slug' not in kwargs and 'name' in kwargs:
            kwargs['slug'] = slugify(kwargs['name'])
        return Campus.objects.get_or_create(
            external_id=kwargs.get('external_id'),
            defaults={'name': kwargs.get('name'), 'slug': kwargs.get('slug'), 'geometry': kwargs.get('geometry')}
        )

@SpatialEntityFactory.register('building')
class BuildingCreator(BaseCreator):
    @staticmethod
    def execute_creation(**kwargs):
        from maps.models import Building
        return Building.objects.get_or_create(
            code=kwargs.get('code'),
            external_id=kwargs.get('external_id'),
            defaults={'name': kwargs.get('name'), 'campus': kwargs.get('campus'), 'geometry': kwargs.get('geometry')}
        )

@SpatialEntityFactory.register('floor')
class FloorCreator(BaseCreator):
    @staticmethod
    def execute_creation(**kwargs):
        from maps.models import Floor
        return Floor.objects.get_or_create(
            building=kwargs.get('building'),
            level=kwargs.get('level'),
            defaults={'name': kwargs.get('name'), 'altitude': kwargs.get('altitude', 0.0), 'external_id': kwargs.get('external_id'), 'geometry': kwargs.get('geometry')}
        )

@SpatialEntityFactory.register('space')
class SpaceCreator(BaseCreator):
    @staticmethod
    def execute_creation(**kwargs):
        from maps.models import Space
        return Space.objects.get_or_create(
            floor=kwargs.get('floor'),
            external_id=kwargs.get('external_id'),
            defaults={'name': kwargs.get('name'), 'space_type': kwargs.get('space_type', 'ROOM'), 'geometry': kwargs.get('geometry')}
        )

@SpatialEntityFactory.register('edge')
class EdgeCreator(BaseCreator):
    @staticmethod
    def execute_creation(**kwargs):
        from maps.models import NavigationEdge
        return NavigationEdge.objects.get_or_create(
            source_space=kwargs.get('source_space'),
            target_space=kwargs.get('target_space'),
            defaults={'name': kwargs.get('name', ''), 'geometry': kwargs.get('geometry'), 'is_accessible': kwargs.get('is_accessible', True)}
        )