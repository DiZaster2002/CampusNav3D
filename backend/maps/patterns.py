from abc import ABC, abstractmethod

from django.contrib.gis.geos import GEOSGeometry
from django.utils.text import slugify

from .models import Building, Campus, Floor, NavigationEdge, Space


class SpatialImportStep(ABC):
    """Contrato explícito para cada paso de importación espacial."""

    @abstractmethod
    def process(self, payload, context):
        """Procesa una porción del manifiesto y añade resultados al contexto."""


class CampusImportStep(SpatialImportStep):
    """Responsable exclusivo de crear o recuperar un Campus."""

    def process(self, payload, context):
        campus_data = payload['campus']
        campus, created = Campus.objects.get_or_create(
            slug=slugify(campus_data['name']),
            external_id=campus_data['external_id'],
            defaults={
                'name': campus_data['name'],
                'geometry': GEOSGeometry(campus_data['geometry']),
            },
        )
        context['campus'] = campus
        context['campus_created'] = created
        return campus


class BuildingImportStep(SpatialImportStep):
    """Responsable exclusivo de crear o recuperar un Building."""

    def process(self, payload, context):
        campus = context.get('campus')
        if campus is None:
            raise ValueError('Campus is required before importing a building.')

        building_data = payload['building']
        building, created = Building.objects.get_or_create(
            code=building_data['code'],
            external_id=building_data['external_id'],
            defaults={
                'name': building_data['name'],
                'campus': campus,
                'geometry': GEOSGeometry(building_data['geometry']),
            },
        )
        context['building'] = building
        context['building_created'] = created
        return building


class FloorImportStep(SpatialImportStep):
    """Responsable exclusivo de crear o recuperar una Floor."""

    def process(self, payload, context):
        building = context.get('building')
        if building is None:
            raise ValueError('Building is required before importing a floor.')

        floor_data = payload['floor']
        floor, created = Floor.objects.get_or_create(
            building=building,
            level=floor_data['level'],
            external_id=floor_data['external_id'],
            defaults={
                'name': floor_data['name'],
                'altitude': floor_data['altitude'],
                'geometry': GEOSGeometry(floor_data['geometry']),
            },
        )
        context['floor'] = floor
        context['floor_created'] = created
        return floor


class SpaceImportStep(SpatialImportStep):
    """Responsable exclusivo de crear o recuperar espacios del mapa."""

    def process(self, payload, context):
        floor = context.get('floor')
        if floor is None:
            raise ValueError('Floor is required before importing spaces.')

        spaces_map = {}
        for space_data in payload.get('spaces', []):
            space, created = Space.objects.get_or_create(
                floor=floor,
                external_id=space_data['external_id'],
                defaults={
                    'name': space_data['name'],
                    'space_type': space_data['space_type'],
                    'geometry': GEOSGeometry(space_data['geometry']),
                },
            )
            spaces_map[space.external_id] = space
            context.setdefault('space_creations', {})[space.external_id] = created

        context['spaces'] = spaces_map
        return spaces_map


class NavigationEdgeImportStep(SpatialImportStep):
    """Responsable exclusivo de crear o recuperar aristas de navegación."""

    def process(self, payload, context):
        spaces_map = context.get('spaces', {})
        if not spaces_map:
            raise ValueError('Spaces are required before importing navigation edges.')

        edges = []
        for edge_data in payload.get('edges', []):
            source = spaces_map.get(edge_data['source_external_id'])
            target = spaces_map.get(edge_data['target_external_id'])

            if not source or not target:
                continue

            edge, created = NavigationEdge.objects.get_or_create(
                source_space=source,
                target_space=target,
                defaults={
                    'name': edge_data['name'],
                    'geometry': GEOSGeometry(edge_data['geometry']),
                    'is_accessible': True,
                },
            )
            edges.append((edge, created))

        context['edges'] = edges
        return edges


class ImportComposite(SpatialImportStep):
    """Componente compuesto que ejecuta varios pasos de importación en secuencia."""

    def __init__(self, steps=None):
        self._steps = []
        if steps:
            for step in steps:
                self.add(step)

    def add(self, step):
        self._steps.append(step)

    def process(self, payload, context):
        for step in self._steps:
            step.process(payload, context)
        return context


class SpatialEntityFactory:
    """Factory explícita para construir handlers de importación por tipo de entidad."""

    def __init__(self, handlers=None):
        self._handlers = handlers or {
            'campus': CampusImportStep(),
            'building': BuildingImportStep(),
            'floor': FloorImportStep(),
            'spaces': SpaceImportStep(),
            'edges': NavigationEdgeImportStep(),
        }

    def register_handler(self, entity_type, handler):
        self._handlers[entity_type] = handler

    def create_handler(self, entity_type):
        handler = self._handlers.get(entity_type)
        if handler is None:
            raise ValueError(f'No handler registered for entity type: {entity_type}')
        return handler
