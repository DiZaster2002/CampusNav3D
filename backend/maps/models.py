from django.contrib.gis.db import models

class SpatialComponent:
    """
    Componente Base del Patrón Composite (OCP Compliant).
    Las operaciones del árbol son genéricas y no requieren modificación ante nuevos nodos.
    """
    _child_relation = None  # Debe ser sobrescrito por nodos compuestos

    @property
    def is_leaf(self) -> bool:
        raise NotImplementedError("Los modelos que hereden de SpatialComponent deben implementar 'is_leaf'")

    def get_children(self):
        """Navegación genérica del árbol por reflexión de relaciones Django."""
        if self.is_leaf or not self._child_relation:
            return []
        # Obtiene dinámicamente el related manager asignado en el modelo
        relation = getattr(self, self._child_relation, None)
        return relation.all() if relation else []

    def get_total_area(self) -> float:
        """Operación uniforme compartida por toda la jerarquía."""
        return self.geometry.area

class Campus(models.Model, SpatialComponent):
    """Representa el recinto universitario global."""
    external_id = models.CharField(max_length=100, blank=True, null=True, help_text="ID del campus en planos externos")
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    # Geometría: Polígono que delimita todo el campus exterior
    geometry = models.PolygonField(srid=4326, help_text="Delimitación geográfica exterior del campus (WGS84)")
    created_at = models.DateTimeField(auto_now_add=True)

    _child_relation = 'buildings'  # Mapea de forma limpia al related_name

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

    _child_relation = 'floors'  # Mapea de forma limpia al related_name

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

    _child_relation = 'spaces'  # Mapea de forma limpia al related_name

    @property
    def is_leaf(self) -> bool:
        return False

    class Meta:
        unique_together = ('building', 'level')
        ordering = ['level']

    def __str__(self):
        return f"{self.building.code} - {self.name} - ({self.external_id})"


class Space(models.Model, SpatialComponent):
    """
    Representación semántica y espacial de un espacio interior utilizable.
    Corresponde conceptualmente al 'CellSpace' del estándar IndoorGML 2.0.
    """
    SPACE_TYPES = [
        ('ROOM', 'Aula / Despacho'),
        ('CORRIDOR', 'Pasillo / Zona de Circulación'),
        ('STAIRS', 'Escaleras'),
        ('ELEVATOR', 'Ascensor'),
        ('RESTROOM', 'Servicios / Aseos'),
        ('RESTRICTED', 'Zona Restringida / Técnica'),
    ]

    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='spaces')
    external_id = models.CharField(max_length=100, blank=True, null=True, help_text="ID del espacio en planos externos")
    name = models.CharField(max_length=100, help_text="Ej: Aula 1.1, Despacho 202")
    space_type = models.CharField(max_length=20, choices=SPACE_TYPES, default='ROOM')
    
    # Geometría: Polígono cerrado que representa el área útil interna de la celda
    geometry = models.PolygonField(srid=4326, help_text="Geometría del espacio interior (WGS84)")

    @property
    def is_leaf(self) -> bool:
        return True

    def __str__(self):
        return f"[{self.space_type}] {self.name} - ({self.floor.building.code}) - ({self.external_id})"
    

class NavigationEdge(models.Model):
    """
    Representa una transición (Edge) en el Grafo Dual de IndoorGML.
    Conecta físicamente dos celdas de espacio independientes.
    """
    name = models.CharField(max_length=100, blank=True, help_text="Nombre opcional de la conexión (ej: Pasillo-Aula101)")
    source_space = models.ForeignKey(
        Space, 
        on_delete=models.CASCADE, 
        related_name='outgoing_edges',
        help_text="Espacio de origen (Nodo A)"
    )
    target_space = models.ForeignKey(
        Space, 
        on_delete=models.CASCADE, 
        related_name='incoming_edges',
        help_text="Espacio de destino (Nodo B)"
    )
    # Geometría de tipo Línea para pintar el camino exacto de navegación
    geometry = models.LineStringField(srid=4326)
    
    is_accessible = models.BooleanField(
        default=True, 
        help_text="Indica si este tramo es apto para personas con movilidad reducida (sin escaleras)"
    )

    def __str__(self):
        return f"{self.name or 'Tramo'} ({self.source_space.name} -> {self.target_space.name})"