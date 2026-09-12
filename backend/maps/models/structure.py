from django.contrib.gis.db import models
from .base import SpatialComponent


class Campus(models.Model, SpatialComponent):
    """Representa el recinto universitario global."""
    external_id = models.CharField(max_length=100, blank=True, null=True, help_text="ID del campus en planos externos")
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    # Geometría: Polígono que delimita todo el campus exterior
    geometry = models.PolygonField(srid=4326, help_text="Delimitación geográfica exterior del campus (WGS84)")
    created_at = models.DateTimeField(auto_now_add=True)

    _child_relation = 'buildings'

    @property
    def is_leaf(self) -> bool:
        return False

    def __str__(self):
        return f"Campus: {self.name} - ({self.external_id})"

    class Meta:
        verbose_name_plural = "Campuses"


class Building(models.Model, SpatialComponent):
    """Representa un edificio físico dentro de un campus."""
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name='buildings')
    external_id = models.CharField(max_length=100, blank=True, null=True, help_text="ID del edificio en planos externos")
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True, help_text="Código identificador del edificio (ej: EPS-I)")
    # Geometría: Polígono del contorno en planta baja del edificio
    geometry = models.PolygonField(srid=4326, help_text="Huella perimetral del edificio (WGS84)")

    _child_relation = 'floors'

    @property
    def is_leaf(self) -> bool:
        return False

    def __str__(self):
        return f"{self.name} - ({self.code}) - ({self.external_id})"


class Floor(models.Model, SpatialComponent):
    """Representa una planta/piso específico de un edificio."""
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='floors')
    external_id = models.CharField(max_length=100, blank=True, null=True, help_text="ID de la planta en planos externos")
    level = models.IntegerField(help_text="Número de planta (0=Baja, 1=Primera, -1=Sótano)")
    name = models.CharField(max_length=50, help_text="Nombre de la planta (ej: Planta Primera)")
    altitude = models.FloatField(default=0.0, help_text="Altitud relativa en metros desde el suelo")
    # Geometría: Huella específica de esta planta (puede diferir de la baja)
    geometry = models.PolygonField(srid=4326, help_text="Contorno geométrico de la planta")

    _child_relation = 'spaces'

    @property
    def is_leaf(self) -> bool:
        return False

    class Meta:
        unique_together = ('building', 'level')
        ordering = ['level']

    def __str__(self):
        return f"{self.building.code} - {self.name} - ({self.external_id})"