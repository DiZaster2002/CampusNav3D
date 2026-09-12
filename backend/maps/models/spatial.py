import hashlib
from django.contrib.gis.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from .base import SpatialComponent
from .structure import Floor


class SpatialPlanStatus(models.TextChoices):
    UPLOADED = 'UPLOADED', 'Cargado / Pendiente'
    PREPROCESSING = 'PREPROCESSING', 'Preprocesando Imagen'
    EXTRACTING = 'EXTRACTING', 'Extrayendo con IA'
    REQUIRES_REVIEW = 'REQUIRES_REVIEW', 'Requiere Revisión Manual'
    PROCESSED = 'PROCESSED', 'Procesado Completamente'
    APPROVED = 'APPROVED', 'Aprobado y Persistido'
    REJECTED = 'REJECTED', 'Rechazado por el Revisor'
    FAILED = 'FAILED', 'Error en el Pipeline'


class SpatialPlan(models.Model):
    """
    Plano físico (imagen/blueprint) aplicable a CUALQUIER componente espacial 
    (Campus, Edificio o Planta) gracias al framework de relaciones genéricas de Django.
    """
    # Relación Genérica (Apunta a Campus, Building o Floor de forma polimórfica)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    spatial_object = GenericForeignKey('content_type', 'object_id')

    # Archivo físico del plano
    image = models.ImageField(upload_to='spatial_plans/%Y/%m/%d/', help_text="Archivo de imagen del plano (PNG/JPG/SVG)")

    # Máquina de Estados Estricta
    status = models.CharField(
        max_length=20, 
        choices=SpatialPlanStatus.choices, 
        default=SpatialPlanStatus.UPLOADED,
        db_index=True
    )

    # Control de Idempotencia (Evita procesar dos veces el mismo archivo exacto)
    file_hash = models.CharField(max_length=64, unique=True, help_text="Hash SHA-256 del archivo")

    # Frontera de Datos: Contrato intermedio guardado tras la validación de Pydantic
    intermediate_proposal = models.JSONField(blank=True, null=True, help_text="Esquema JSON normalizado de la propuesta")

    # Trazabilidad, Auditoría y Control de Costes de la IA
    ai_metadata = models.JSONField(
        default=dict, 
        blank=True, 
        help_text="Métricas de ejecución: {prompt, tokens_used, cost_usd, provider_name}"
    )
    error_log = models.TextField(blank=True, null=True, help_text="Traza detallada del error si el estado es FAILED")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Un objeto espacial (ej: una Planta concreta) solo puede tener UN plano activo asociado
        unique_together = ('content_type', 'object_id')

    def save(self, *args, **kwargs):
        """Idempotencia: Calcula el hash SHA-256 del archivo antes de guardarlo en disco/DB."""
        if self.image and not self.file_hash:
            hasher = hashlib.sha256()
            for chunk in self.image.chunks():
                hasher.update(chunk)
            self.file_hash = hasher.hexdigest()
        super().save(*args, **kwargs)

    def transition_to(self, new_status: SpatialPlanStatus, error_message: str = None):
        """Garante atómico del ciclo de vida de la máquina de estados."""
        self.status = new_status
        if error_message:
            self.error_log = error_message
        self.save(update_fields=['status', 'error_log', 'updated_at'])

    def __str__(self):
        return f"Plano de {self.spatial_object} - Estado: {self.status}"


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