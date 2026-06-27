from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Campus, Building, Floor, Space

class CampusSerializer(GeoFeatureModelSerializer):
    """Serializa objetos Campus al estándar GeoJSON."""
    class Meta:
        model = Campus
        geo_field = 'geometry'  # Indica cuál es el campo geométrico espacial
        fields = ('id', 'name', 'slug', 'created_at')


class BuildingSerializer(GeoFeatureModelSerializer):
    """Serializa objetos Building al estándar GeoJSON."""
    class Meta:
        model = Building
        geo_field = 'geometry'
        fields = ('id', 'name', 'code', 'campus')


class FloorSerializer(GeoFeatureModelSerializer):
    """Serializa objetos Floor al estándar GeoJSON."""
    class Meta:
        model = Floor
        geo_field = 'geometry'
        fields = ('id', 'level', 'name', 'altitude', 'building')


class SpaceSerializer(GeoFeatureModelSerializer):
    """Serializa las celdas IndoorGML al estándar GeoJSON."""
    class Meta:
        model = Space
        geo_field = 'geometry'
        fields = ('id', 'external_id', 'name', 'space_type', 'floor')