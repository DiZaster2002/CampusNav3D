from rest_framework import viewsets
from .models import Campus, Building, Floor, Space, NavigationEdge
from .serializers import CampusSerializer, BuildingSerializer, FloorSerializer, SpaceSerializer, NavigationEdgeSerializer

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