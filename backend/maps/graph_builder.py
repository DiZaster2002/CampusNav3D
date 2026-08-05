import networkx as nx
from typing import Optional
from django.contrib.gis.db.models.functions import Distance
from .models import Space, NavigationEdge


class GraphBuilder:
    """
    Servicio encargado de construir y abstraer la representación de la red 
    de navegación interior como un Grafo Dirigido de NetworkX (nx.DiGraph).
    """

    @staticmethod
    def build_graph(
        building_id: Optional[int] = None, 
        floor_id: Optional[int] = None, 
        only_accessible: bool = False
    ) -> nx.DiGraph:
        """
        Construye un grafo dirigido a partir de las entidades de la BD.
        
        :param building_id: ID opcional para filtrar el grafo por edificio.
        :param floor_id: ID opcional para filtrar el grafo por planta específica.
        :param only_accessible: Si es True, filtra únicamente aristas accesibles (PMR).
        :return: Objeto nx.DiGraph poblado con nodos (Space) y aristas (NavigationEdge).
        """
        graph = nx.DiGraph()

        # 1. Filtrado base de espacios (Nodos)
        spaces_queryset = Space.objects.select_related('floor', 'floor__building').all()
        
        if floor_id:
            spaces_queryset = spaces_queryset.filter(floor_id=floor_id)
        elif building_id:
            spaces_queryset = spaces_queryset.filter(floor__building_id=building_id)

        # Mapeo rápido de IDs de espacios válidos en el contexto
        valid_space_ids = set(spaces_queryset.values_list('id', flat=True))

        # 2. Agregar Nodos al Grafo
        for space in spaces_queryset:
            centroid = space.geometry.centroid
            graph.add_node(
                space.id,
                name=space.name,
                space_type=space.space_type,
                external_id=space.external_id,
                floor_id=space.floor_id,
                building_id=space.floor.building_id,
                building_code=space.floor.building.code,
                coordinates=(centroid.x, centroid.y)
            )

        # 3. Filtrado base de conexiones (Aristas)
        edges_queryset = NavigationEdge.objects.select_related(
            'source_space', 'target_space'
        ).filter(
            source_space_id__in=valid_space_ids,
            target_space_id__in=valid_space_ids
        )

        if only_accessible:
            edges_queryset = edges_queryset.filter(is_accessible=True)

        # 4. Agregar Aristas al Grafo con pesos calculados
        for edge in edges_queryset:
            # Cálculo de la longitud geográfica/métrica del tramo en grados/metros
            # Si la geometría de la arista existe, usamos su longitud; de lo contrario, distancia entre centroides
            weight = edge.geometry.length if edge.geometry else 1.0

            graph.add_edge(
                edge.source_space_id,
                edge.target_space_id,
                edge_id=edge.id,
                name=edge.name,
                weight=weight,
                is_accessible=edge.is_accessible,
                geometry_wkt=edge.geometry.wkt if edge.geometry else None
            )

        return graph