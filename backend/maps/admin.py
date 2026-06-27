from django.contrib.gis import admin
from .models import Campus, Building, Floor, Space

@admin.register(Campus)
class CampusAdmin(admin.GISModelAdmin):
    """Panel de administración para la gestión de recintos del campus."""
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    # Configuración del mapa interactivo
    gis_widget_kwargs = {
        'attrs': {
            'default_zoom': 16,
            'default_lon': -3.703790,  # Coordenadas por defecto (Madrid, España)
            'default_lat': 40.416775,
        }
    }

@admin.register(Building)
class BuildingAdmin(admin.GISModelAdmin):
    """Panel de administración para los edificios del campus."""
    list_display = ('name', 'code', 'campus')
    search_fields = ('name', 'code')
    list_filter = ('campus',)

@admin.register(Floor)
class FloorAdmin(admin.GISModelAdmin):
    """Panel de administración para la gestión de las plantas."""
    list_display = ('name', 'level', 'building', 'altitude')
    list_filter = ('building',)
    ordering = ('building', 'level')

@admin.register(Space)
class SpaceAdmin(admin.GISModelAdmin):
    """Panel de administración para las celdas de espacio (IndoorGML CellSpace)."""
    list_display = ('name', 'space_type', 'floor')
    list_filter = ('space_type', 'floor__building', 'floor')
    search_fields = ('name', 'external_id')