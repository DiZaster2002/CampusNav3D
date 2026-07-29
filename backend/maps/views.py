from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Campus, Building, Floor, Space, NavigationEdge, SpatialPlan, SpatialPlanStatus
from .serializers import (
    CampusSerializer,
    BuildingSerializer,
    FloorSerializer,
    SpaceSerializer,
    NavigationEdgeSerializer,
    SpatialPlanUploadSerializer,
    SpatialPlanStatusSerializer,
    SpatialPlanApproveSerializer,
    SpatialPlanListSerializer
)
from .tasks import process_spatial_plan_task
from django.contrib.gis.geos import Polygon
from django.shortcuts import get_object_or_404  
from django.db import transaction
from rest_framework.views import APIView         

######## VIEWSETS GEOJSON ########
class CampusViewSet(viewsets.ModelViewSet):
    queryset = Campus.objects.all()
    serializer_class = CampusSerializer

class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer

class FloorViewSet(viewsets.ModelViewSet):
    queryset = Floor.objects.all()
    serializer_class = FloorSerializer

class SpaceViewSet(viewsets.ModelViewSet):
    queryset = Space.objects.all()
    serializer_class = SpaceSerializer

class NavigationEdgeViewSet(viewsets.ModelViewSet):
    queryset = NavigationEdge.objects.all()
    serializer_class = NavigationEdgeSerializer


##### VIEWSETS PIPELINE ########
class SpatialPlanUploadView(generics.CreateAPIView):
    """
    POST /api/plans/upload/
    Recibe la imagen del plano y encola de forma explícita la tarea en Celery.
    Responde HTTP 202 Accepted de inmediato.
    """
    queryset = SpatialPlan.objects.all()
    serializer_class = SpatialPlanUploadSerializer
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        ai_provider = serializer.validated_data.get('ai_provider', 'mock')
        
        # Persistir el objeto con estado UPLOADED
        spatial_plan = serializer.save(
            content_type=serializer.validated_data['content_type'],
            object_id=serializer.validated_data['target_id']
        )

        # 🚀 DISPARO EXPLÍCITO DE LA TAREA ASÍNCRONA
        process_spatial_plan_task.delay(spatial_plan.id, provider_name=ai_provider)

        return Response(
            {
                "message": "Plano subido con éxito. Procesamiento iniciado en segundo plano.",
                "plan_id": spatial_plan.id,
                "status": spatial_plan.status,
                "status_url": f"/api/plans/{spatial_plan.id}/status/"
            },
            status=status.HTTP_202_ACCEPTED
        )

class SpatialPlanApproveView(APIView):
    """
    POST /api/plans/<id>/approve/
    Convierte el draft_data (o la versión editada) en objetos GIS reales (Space)
    y marca el plano como APPROVED.
    """
    @transaction.atomic
    def post(self, request, pk):
        plan = get_object_or_404(SpatialPlan, pk=pk)

        if plan.status != SpatialPlanStatus.REQUIRES_REVIEW:
            return Response(
                {"detail": f"El plano no se encuentra en estado REQUIRES_REVIEW (estado actual: {plan.status})."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SpatialPlanApproveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Usar borrador editado desde el frontend si existe, o el borrador original generado por la IA
        edited_draft_data = serializer.validated_data.get('edited_draft_data')
        intermediate_proposal = edited_draft_data or plan.intermediate_proposal

        if not intermediate_proposal:
            return Response(
                {"detail": "No existen datos de borrador (intermediate_proposal) asociados a este plano."},
                status=status.HTTP_400_BAD_REQUEST
            )

        spaces_data = intermediate_proposal.get('spaces', [])

        # VALIDACIÓN DE GEOMETRÍA: Asegurarse de que hay al menos un espacio válido
        if not spaces_data or len(spaces_data) == 0:
            return Response(
                {"detail": "No se puede aprobar un plano sin geometría. La propuesta no contiene ningún espacio/recinto válido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        created_spaces = []
        target_obj = plan.spatial_object

        # 🚀 Persistencia de Espacios (Space) en PostGIS
        for space_info in spaces_data:
            coords = space_info.get('coordinates', [])
            if len(coords) >= 3:
                # Garantizar polígono cerrado para PostGIS
                if coords[0] != coords[-1]:
                    coords.append(coords[0])

                try: 
                    poly = Polygon(coords)
                    
                    space = Space.objects.create(
                        floor=target_obj if isinstance(target_obj, Floor) else None,
                        name=space_info.get('name', 'Espacio Detectado'),
                        space_type=space_info.get('type', 'ROOM'),
                        geometry=poly
                    )
                    created_spaces.append(space.id)

                except Exception as e:
                    return Response(
                        {"detail": f"Error al crear el espacio: {str(e)}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        plan.status = SpatialPlanStatus.APPROVED
        plan.save(update_fields=['status', 'intermediate_proposal'])

        return Response({
            "message": "Plano aprobado y entidades GIS creadas exitosamente.",
            "plan_id": plan.id,
            "status": plan.status,
            "created_spaces_count": len(created_spaces),
            "space_ids": created_spaces
        }, status=status.HTTP_200_OK)


class SpatialPlanRejectView(APIView):
    """
    POST /api/plans/<id>/reject/
    Marca un plano como FAILED/Rechazado indicando el motivo.
    """
    @transaction.atomic
    def post(self, request, pk):
        plan = get_object_or_404(SpatialPlan, pk=pk)

        if plan.status != SpatialPlanStatus.REQUIRES_REVIEW:
            return Response(
                {"detail": f"El plano no se puede rechazar en su estado actual ({plan.status})."},
                status=status.HTTP_400_BAD_REQUEST
            )

        reason = request.data.get('reason', 'Sin motivo especificado')
        plan.status = SpatialPlanStatus.REJECTED
        plan.error_log = f"Rechazado manualmente: {reason}"
        plan.save(update_fields=['status', 'error_log'])

        return Response({
            "message": "Plano rechazado.",
            "plan_id": plan.id,
            "status": plan.status,
            "reason": reason
        }, status=status.HTTP_200_OK)

class SpatialPlanListView(generics.ListAPIView):
    """
    GET /api/plans/
    Devuelve la lista completa de planos registrados y sus estados actuales.
    """
    queryset = SpatialPlan.objects.all().order_by('-created_at')
    serializer_class = SpatialPlanListSerializer

class SpatialPlanStatusView(generics.RetrieveAPIView):
    """
    GET /api/plans/<id>/status/
    Endpoint ligero para que el Frontend haga Polling sobre el progreso.
    """
    queryset = SpatialPlan.objects.all()
    serializer_class = SpatialPlanStatusSerializer
    lookup_field = 'pk'
