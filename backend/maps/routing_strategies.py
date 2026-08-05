from abc import ABC, abstractmethod
from typing import List, Dict, Any
import networkx as nx


class RoutingStrategy(ABC):
    """
    Interfaz Base del Patrón Strategy para la selección de algoritmos de enrutado.
    Define el contrato que deben cumplir todas las estrategias de navegación.
    """

    @abstractmethod
    def calculate_route(self, graph: nx.DiGraph, start_node: int, target_node: int) -> Dict[str, Any]:
        """
        Calcula la ruta óptima entre dos nodos del grafo.
        
        :param graph: Grafo dirigido de la red de navegación (nx.DiGraph).
        :param start_node: ID del espacio de origen (Space ID).
        :param target_node: ID del espacio de destino (Space ID).
        :return: Diccionario con el resultado de la ruta y métricas.
        """
        pass


class FastestPathStrategy(RoutingStrategy):
    """
    Estrategia de Ruta Más Rápida / Corta.
    Aplica el algoritmo de Dijkstra ponderado por la distancia física de las aristas.
    """

    def calculate_route(self, graph: nx.DiGraph, start_node: int, target_node: int) -> Dict[str, Any]:
        if not graph.has_node(start_node) or not graph.has_node(target_node):
            raise ValueError("El nodo de origen o destino no existe en el grafo de navegación.")

        try:
            path_nodes = nx.shortest_path(graph, source=start_node, target=target_node, weight='weight')
            total_distance = nx.shortest_path_length(graph, source=start_node, target=target_node, weight='weight')

            return {
                "strategy": "fastest",
                "path": path_nodes,
                "total_distance": round(total_distance, 4),
                "node_count": len(path_nodes),
                "is_accessible": False
            }
        except nx.NetworkXNoPath:
            return {
                "strategy": "fastest",
                "path": [],
                "total_distance": 0.0,
                "node_count": 0,
                "error": "No existe un camino navegable entre los espacios indicados."
            }


class AccessiblePathStrategy(RoutingStrategy):
    """
    Estrategia de Ruta Adaptada PMR.
    Filtra el grafo para transitar únicamente por aristas marcadas como accesibles.
    """

    def calculate_route(self, graph: nx.DiGraph, start_node: int, target_node: int) -> Dict[str, Any]:
        if not graph.has_node(start_node) or not graph.has_node(target_node):
            raise ValueError("El nodo de origen o destino no existe en el grafo de navegación.")

        # Filtrar subgrafo compuesto exclusivamente por aristas accesibles
        accessible_edges = [
            (u, v) for u, v, d in graph.edges(data=True)
            if d.get('is_accessible', True)
        ]
        subgraph = graph.edge_subgraph(accessible_edges)

        try:
            path_nodes = nx.shortest_path(subgraph, source=start_node, target=target_node, weight='weight')
            total_distance = nx.shortest_path_length(subgraph, source=start_node, target=target_node, weight='weight')

            return {
                "strategy": "accessible",
                "path": path_nodes,
                "total_distance": round(total_distance, 4),
                "node_count": len(path_nodes),
                "is_accessible": True
            }
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return {
                "strategy": "accessible",
                "path": [],
                "total_distance": 0.0,
                "node_count": 0,
                "error": "No existe una ruta accesible adaptada (PMR) entre los puntos seleccionados."
            }