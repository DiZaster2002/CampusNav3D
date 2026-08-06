from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CampusViewSet,
    BuildingViewSet,
    FloorViewSet,
    SpaceViewSet,
    NavigationEdgeViewSet,
    SpatialPlanUploadView,
    SpatialPlanStatusView,
    SpatialPlanApproveView,
    SpatialPlanRejectView,
    SpatialPlanListView,
    RouteAPIView
)

router = DefaultRouter()
router.register(r'campuses', CampusViewSet)
router.register(r'buildings', BuildingViewSet)
router.register(r'floors', FloorViewSet)
router.register(r'spaces', SpaceViewSet)
router.register(r'edges', NavigationEdgeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('plans/', SpatialPlanListView.as_view(), name='spatialplan-list'),
    path('plans/upload/', SpatialPlanUploadView.as_view(), name='plan-upload'),
    path('plans/<int:pk>/status/', SpatialPlanStatusView.as_view(), name='plan-status'),
    path('plans/<int:pk>/approve/', SpatialPlanApproveView.as_view(), name='plan-approve'), 
    path('plans/<int:pk>/reject/', SpatialPlanRejectView.as_view(), name='plan-reject'),  
    path('route/', RouteAPIView.as_view(), name='navigation-route'),
]
