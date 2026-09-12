from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView

from .models import Campus, Building, Floor, Space, NavigationEdge, SpatialPlan
from .serializers import (
    CampusSerializer,
    BuildingSerializer,
    FloorSerializer,
    SpaceSerializer,
    NavigationEdgeSerializer,
    SpatialPlanUploadSerializer,
    SpatialPlanStatusSerializer,
    SpatialPlanApproveSerializer,
    SpatialPlanListSerializer,
    RouteQuerySerializer
)
from .services import PlanService, ApprovalService
from .navigation_facade import NavigationFacade


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


##### VIEWSETS / APIVIEWS PIPELINE ########
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

        spatial_plan = PlanService.upload_and_enqueue_plan(serializer)

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
    POST /api/plans//approve/
    Convierte el draft_data (o la versión editada) en objetos GIS reales (Space)
    y marca el plano como APPROVED.
    """
    def post(self, request, pk):
        serializer = SpatialPlanApproveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        edited_draft_data = serializer.validated_data.get('edited_draft_data')

        try:
            plan, created_spaces = ApprovalService.approve_plan(
                plan_id=pk,
                edited_draft_data=edited_draft_data
            )
            return Response({
                "message": "Plano aprobado y entidades GIS creadas exitosamente.",
                "plan_id": plan.id,
                "status": plan.status,
                "created_spaces_count": len(created_spaces),
                "space_ids": created_spaces
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SpatialPlanRejectView(APIView):
    """
    POST /api/plans//reject/
    Marca un plano como REJECTED indicando el motivo.
    """
    def post(self, request, pk):
        reason = request.data.get('reason', 'Sin motivo especificado')

        try:
            plan = PlanService.reject_plan(plan_id=pk, reason=reason)
            return Response({
                "message": "Plano rechazado.",
                "plan_id": plan.id,
                "status": plan.status,
                "reason": reason
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SpatialPlanListView(generics.ListAPIView):
    """
    GET /api/plans/
    Devuelve la lista completa de planos registrados y sus estados actuales.
    """
    queryset = SpatialPlan.objects.all().order_by('-created_at')
    serializer_class = SpatialPlanListSerializer


class SpatialPlanStatusView(generics.RetrieveAPIView):
    """
    GET /api/plans//status/
    Endpoint ligero para que el Frontend haga Polling sobre el progreso.
    """
    queryset = SpatialPlan.objects.all()
    serializer_class = SpatialPlanStatusSerializer
    lookup_field = 'pk'


class RouteAPIView(APIView):
    """
    Endpoint REST para el cálculo de itinerarios interiores.
    
    GET /api/route/?start_space_id=1&target_space_id=5&preference=accessible
    """
    def get(self, request, *args, **kwargs):
        serializer = RouteQuerySerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data

        try:
            route_data = NavigationFacade.get_route(
                start_space_id=validated_data['start_space_id'],
                target_space_id=validated_data['target_space_id'],
                preference=validated_data.get('preference', 'fastest'),
                building_id=validated_data.get('building_id'),
                floor_id=validated_data.get('floor_id')
            )

            if "error" in route_data and not route_data["path"]:
                return Response(route_data, status=status.HTTP_404_NOT_FOUND)

            return Response(route_data, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"detail": "Error interno durante el cálculo de la ruta.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )