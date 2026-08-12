from django.urls import reverse
from django.contrib.gis.geos import Polygon, LineString
from rest_framework import status

from maps.models import Campus, Building, Floor, Space, NavigationEdge
from .base import AuthenticatedAPITestCase


class MapsAPITestCase(AuthenticatedAPITestCase):
    """
    Suite de pruebas de integración para la API REST del módulo de mapas,
    cobertura de serializadores GeoJSON y endpoints de consulta CRUD/Read-Only.
    """

    @classmethod
    def setUpTestData(cls):
        """Creación de la jerarquía espacial base en PostGIS."""
        cls.campus = Campus.objects.create(
            name="Campus Sur API",
            slug="campus-sur-api",
            geometry=Polygon(((0, 0), (0, 100), (100, 100), (100, 0), (0, 0)))
        )
        cls.building = Building.objects.create(
            campus=cls.campus,
            name="Edificio Informática",
            code="ED-INF",
            geometry=Polygon(((10, 10), (10, 90), (90, 90), (90, 10), (10, 10)))
        )
        cls.floor = Floor.objects.create(
            building=cls.building,
            level=1,
            name="Primera Planta",
            geometry=Polygon(((10, 10), (10, 90), (90, 90), (90, 10), (10, 10)))
        )
        cls.space_1 = Space.objects.create(
            floor=cls.floor,
            name="Laboratorio 1.1",
            space_type="LABORATORY",
            geometry=Polygon(((15, 15), (15, 30), (30, 30), (30, 15), (15, 15)))
        )
        cls.space_2 = Space.objects.create(
            floor=cls.floor,
            name="Aula 1.2",
            space_type="CLASSROOM",
            geometry=Polygon(((35, 15), (35, 30), (50, 30), (50, 15), (35, 15)))
        )
        cls.edge = NavigationEdge.objects.create(
            name="Pasillo Lab-Aula",
            source_space=cls.space_1,
            target_space=cls.space_2,
            geometry=LineString((22.5, 22.5), (42.5, 22.5)),
            is_accessible=True
        )

    # -------------------------------------------------------------------------
    # Pruebas de Campus, Building y Floor Endpoints
    # -------------------------------------------------------------------------

    def test_list_campuses(self):
        """Verifica la obtención del listado de campus registrados."""
        url = reverse('campus-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_get_campus_detail_success(self):
        """Verifica la recuperación de los detalles de un campus por su ID."""
        url = reverse('campus-detail', kwargs={'pk': self.campus.id})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Si la respuesta es GeoJSON, el nombre está dentro de 'properties'
        data = response.data
        name = data['properties']['name'] if 'properties' in data else data['name']
        self.assertEqual(name, "Campus Sur API")

    def test_get_campus_detail_not_found(self):
        """[CASO LÍMITE] Verifica respuesta HTTP 404 al consultar un Campus inexistente."""
        url = reverse('campus-detail', kwargs={'pk': 99999})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_buildings_filtered_by_campus(self):
        """Verifica el filtrado de edificios por ID de campus."""
        url = reverse('building-list')
        # Probar con campus_id o campus según la configuración de tu FilterSet
        response = self.client.get(url, {'campus': self.campus.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        features = data['features'] if isinstance(data, dict) and 'features' in data else data
        self.assertEqual(len(features), 1)
        self.assertEqual(features[0]['properties']['code'], "ED-INF")

    # -------------------------------------------------------------------------
    # Pruebas de Cumplimiento GeoJSON (RFC 7946) en Spaces
    # -------------------------------------------------------------------------

    def test_spaces_geojson_format_structure(self):
        """Verifica que el listado de espacios retorne una FeatureCollection GeoJSON válida."""
        url = reverse('space-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(data.get('type'), 'FeatureCollection')
        self.assertIn('features', data)
        self.assertGreaterEqual(len(data['features']), 2)

        first_feature = data['features'][0]
        self.assertEqual(first_feature.get('type'), 'Feature')
        self.assertIn('geometry', first_feature)
        self.assertIn('properties', first_feature)
        self.assertEqual(first_feature['geometry']['type'], 'Polygon')

    def test_spaces_filtering_by_floor(self):
        """Verifica el filtro de recintos por ID de planta."""
        url = reverse('space-list')
        response = self.client.get(url, {'floor_id': self.floor.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data['features']), 2)

    # -------------------------------------------------------------------------
    # Pruebas de NavigationEdge Endpoints
    # -------------------------------------------------------------------------

    def test_list_navigation_edges(self):
        """Verifica la consulta de aristas de navegación en formato GeoJSON/JSON."""
        url = reverse('navigationedge-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)