# Comando de verificación: confirma que NetworkX está disponible e integrado
# en el entorno Django/Docker antes de construir el grafo real (siguiente paso).
import networkx as nx
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Verifica que NetworkX está correctamente instalado e integrado."

    def handle(self, *args, **options):
        graph = nx.Graph()
        graph.add_edge("nodo_a", "nodo_b")
        self.stdout.write(self.style.SUCCESS(
            f"NetworkX {nx.__version__} operativo. "
            f"Grafo de prueba: {graph.number_of_nodes()} nodos, "
            f"{graph.number_of_edges()} aristas."
        ))