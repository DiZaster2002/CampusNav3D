import hashlib
import os
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from .models import Campus, Building, Floor, Space, NavigationEdge, SpatialPlan
from .geometry_utils import CustomGeometryField

# Extensiones y tipos MIME autorizados para planos espaciales
ALLOWED_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.pdf', '.dxf', '.geojson', '.json']
ALLOWED_MIME_TYPES = [
    'image/png',
    'image/jpeg',
    'application/pdf',
    'application/json',
    'application/geo+json',
    'image/vnd.dxf',
    'application/dxf',
    'text/plain',
]

# Límite por defecto de 10 MB si no está definido en settings
MAX_FILE_SIZE = getattr(settings, 'FILE_UPLOAD_MAX_MEMORY_SIZE', 10 * 1024 * 1024)


########## SERIALIZADORES GEOJSON ##########
class CampusSerializer(GeoFeatureModelSerializer):
    """Serializa objetos Campus al estándar GeoJSON."""
    geometry = CustomGeometryField()

    class Meta:
        model = Campus
        geo_field = 'geometry'  # Indica cuál es el campo geométrico espacial
        fields = ('id', 'external_id', 'name', 'slug', 'created_at')


class BuildingSerializer(GeoFeatureModelSerializer):
    """Serializa objetos Building al estándar GeoJSON."""
    geometry = CustomGeometryField()

    class Meta:
        model = Building
        geo_field = 'geometry'
        fields = ('id', 'external_id', 'name', 'code', 'campus')


class FloorSerializer(GeoFeatureModelSerializer):
    """Serializa objetos Floor al estándar GeoJSON."""
    geometry = CustomGeometryField()

    class Meta:
        model = Floor
        geo_field = 'geometry'
        fields = ('id', 'external_id', 'level', 'name', 'altitude', 'building')


class SpaceSerializer(GeoFeatureModelSerializer):
    """Serializa las celdas IndoorGML al estándar GeoJSON."""
    geometry = CustomGeometryField()

    class Meta:
        model = Space
        geo_field = 'geometry'
        fields = ('id', 'external_id', 'name', 'space_type', 'floor')

class NavigationEdgeSerializer(GeoFeatureModelSerializer):
    """Serializa las conexiones del grafo al estándar GeoJSON."""
    class Meta:
        model = NavigationEdge
        geo_field = 'geometry'
        fields = ('id', 'name', 'source_space', 'target_space', 'is_accessible')


########### SERIALIZADORES PIPELINE ##########
class SpatialPlanUploadSerializer(serializers.ModelSerializer):
    """Serializador para la carga inicial de un plano espacial."""
    
    # Permitir al cliente especificar el tipo de entidad objetivo (campus, building, floor)
    model_type = serializers.CharField(write_only=True, help_text="Nombre del modelo objetivo (ej: 'campus', 'building', 'floor')")
    target_id = serializers.IntegerField(write_only=True, help_text="ID del objeto objetivo")
    ai_provider = serializers.CharField(write_only=True, default='mock', required=False)

    class Meta:
        model = SpatialPlan
        fields = ['id', 'image', 'model_type', 'target_id', 'ai_provider', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_image(self, value):
        """
        Validaciones de seguridad a nivel de campo: tamaño, extensión,
        tipo MIME e inspección de contenido (scripts o ejecutables).
        """
        # 1. Validación de Tamaño Máximo
        if value.size > MAX_FILE_SIZE:
            max_mb = MAX_FILE_SIZE / (1024 * 1024)
            raise serializers.ValidationError(
                f"El archivo supera el tamaño máximo permitido de {max_mb:.1f} MB."
            )

        # 2. Validación de Extensión
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                f"Extensión '{ext}' no permitida. Formatos aceptados: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # 3. Validación de Tipo MIME (si el cliente lo proporciona)
        content_type = getattr(value, 'content_type', '').lower()
        if content_type and content_type not in ALLOWED_MIME_TYPES:
            raise serializers.ValidationError(
                f"Tipo de contenido '{content_type}' no válido para un plano espacial."
            )

        # 4. Inspección de Cabecera contra Scripts Disfrazados (RCE Prevention)
        file_head = value.read(1024)
        value.seek(0)  # Restaurar siempre el puntero de lectura para usos posteriores

        danger_patterns = [
            b'<?php', b'<script', b'#!/bin/', b'#!/usr/bin',
            b'eval(', b'system(', b'passthru(', b'exec('
        ]
        
        head_lower = file_head.lower()
        if any(pattern in head_lower for pattern in danger_patterns):
            raise serializers.ValidationError(
                "El archivo contiene firmas o código ejecutable no permitido."
            )

        return value

    def validate(self, attrs):
        model_name = attrs.get('model_type').lower()
        target_id = attrs.get('target_id')
        image = attrs.get('image')

        try:
            content_type = ContentType.objects.get(app_label='maps', model=model_name)
        except ContentType.DoesNotExist:
            raise serializers.ValidationError({"model_type": f"El modelo '{model_name}' no es válido en la app maps."})

        # Verificar que el objeto destino realmente exista
        model_class = content_type.model_class()
        if not model_class.objects.filter(id=target_id).exists():
            raise serializers.ValidationError({"target_id": f"No existe un {model_name} con ID {target_id}."})

        # VALIDACIÓN DE ENTIDAD ÚNICA: Comprobar si el objeto ya tiene plano asignado
        if SpatialPlan.objects.filter(content_type=content_type, object_id=target_id).exists():
            existing_plan = SpatialPlan.objects.get(content_type=content_type, object_id=target_id)
            raise serializers.ValidationError({
                "target_id": f"El objeto {model_name} con ID {target_id} ya tiene un plano asociado (Plano ID {existing_plan.id})."
            })

        attrs['content_type'] = content_type

        # DETECCIÓN DE DUPLICADOS: Calcular hash antes de guardar
        if image:
            hasher = hashlib.sha256()
            for chunk in image.chunks():
                hasher.update(chunk)
            file_hash = hasher.hexdigest()

            # Si el hash ya existe en la base de datos, rechazamos la petición limpiamente
            if SpatialPlan.objects.filter(file_hash=file_hash).exists():
                existing_plan = SpatialPlan.objects.get(file_hash=file_hash)
                raise serializers.ValidationError({
                    "image": f"Este archivo ya ha sido subido anteriormente. Puedes consultar su estado en /api/plans/{existing_plan.id}/status/"
                })

        return attrs

    def create(self, validated_data):
        # Limpiar campos extra que no pertenecen directamente al modelo SpatialPlan
        validated_data.pop('model_type')
        validated_data.pop('target_id')
        validated_data.pop('ai_provider', None)
        
        return SpatialPlan.objects.create(**validated_data)

class SpatialPlanApproveSerializer(serializers.Serializer):
    """Serializador para aprobar y persistir los datos vectoriales generados."""
    edited_draft_data = serializers.JSONField(
        required=False,
        help_text="Datos vectoriales opcionalmente editados en el visor 2D/3D. Si no se envían, se usa plan.intermediate_proposal."
    )

class SpatialPlanListSerializer(serializers.ModelSerializer):
    """Serializador resumido para listar todos los planos registrados."""
    class Meta:
        model = SpatialPlan
        fields = ['id', 'status', 'file_hash', 'error_log', 'created_at', 'updated_at']


class SpatialPlanStatusSerializer(serializers.ModelSerializer):
    """Serializador de lectura para el polling de estado y resultados."""
    
    class Meta:
        model = SpatialPlan
        fields = [
            'id', 
            'status', 
            'file_hash', 
            'intermediate_proposal', 
            'ai_metadata', 
            'error_log', 
            'created_at',
            'updated_at'
        ]

class RouteQuerySerializer(serializers.Serializer):
    """
    Validador de parámetros de consulta GET para peticiones de navegación.
    """
    start_space_id = serializers.IntegerField(required=True, min_value=1)
    target_space_id = serializers.IntegerField(required=True, min_value=1)
    preference = serializers.ChoiceField(
        choices=['fastest', 'accessible'], 
        default='fastest', 
        required=False
    )
    building_id = serializers.IntegerField(required=False, allow_null=True)
    floor_id = serializers.IntegerField(required=False, allow_null=True)