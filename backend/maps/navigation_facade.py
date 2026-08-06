from typing import Dict, Any, Optional
from .graph_builder import GraphBuilder
from .routing_strategies import RoutingStrategy, FastestPathStrategy, AccessiblePathStrategy
from .models import Space


class NavigationFacade:
    """
    Fachada principal del subsistema de enrutado e itinerarios interiores (Patrón Façade).
    Simplifica el consumo unificando la selección de estrategia, la extracción del grafo
    y el enriquecimiento con atributos de dominio GIS.
    """

    STRATEGY_MAP: Dict[str, type] = {
        'fastest': FastestPathStrategy,
        'accessible': AccessiblePathStrategy,
    }

    @classmethod
    def get_route(
        cls, 
        start_space_id: int, 
        target_space_id: int, 
        preference: str = 'fastest',
        building_id: Optional[int] = None,
        floor_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Calcula una ruta entre dos espacios y devuelve la secuencia enriquecida con metadatos.

        :param start_space_id: ID del espacio de origen (Space ID).
        :param target_space_id: ID del espacio de destino (Space ID).
        :param preference: Preferencia de enrutado ('fastest' o 'accessible').
        :param building_id: ID opcional para acotar el grafo por edificio.
        :param floor_id: ID opcional para acotar el grafo por planta.
        :return: Diccionario estructurado con el itinerario y detalles semánticos.
        """
        # 1. Seleccionar estrategia de enrutado
        strategy_class = cls.STRATEGY_MAP.get(preference.lower(), FastestPathStrategy)
        strategy: RoutingStrategy = strategy_class()

        # 2. Construir grafo filtrado
        only_accessible = (preference.lower() == 'accessible')
        graph = GraphBuilder.build_graph(
            building_id=building_id,
            floor_id=floor_id,
            only_accessible=only_accessible
        )

        # 3. Delegar cálculo del itinerario
        route_result = strategy.calculate_route(graph, start_space_id, target_space_id)

        # 4. Enriquecer los nodos de la ruta con información del modelo Space
        path_node_ids = route_result.get("path", [])
        if path_node_ids:
            spaces = Space.objects.filter(id__in=path_node_ids).select_related('floor', 'floor__building')
            space_map = {space.id: space for space in spaces}

            detailed_path = []
            for node_id in path_node_ids:
                space = space_map.get(node_id)
                if space:
                    centroid = space.geometry.centroid
                    detailed_path.append({
                        "id": space.id,
                        "name": space.name,
                        "space_type": space.space_type,
                        "building_code": space.floor.building.code,
                        "floor_level": space.floor.level,
                        "coordinates": [centroid.x, centroid.y]
                    })
            route_result["detailed_path"] = detailed_path

        return route_result