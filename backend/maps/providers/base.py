# maps/providers/base.py
from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any
from maps.models import FloorPlan
from maps.schemas import SpatialExtractionProposal

class AIExtractionProvider(ABC):
    """
    Interfaz Abstracta para los proveedores de extracción (Patrón Adapter).
    Garantiza el cumplimiento estricto de OCP.
    """
    
    @abstractmethod
    def extract_layout(self, floor_plan: FloorPlan) -> Tuple[SpatialExtractionProposal, Dict[str, Any]]:
        """
        Procesa la imagen del FloorPlan y retorna una estructura normalizada 
        junto con el diccionario de metadatos de rendimiento/coste de la IA.
        
        Retorna:
            (SpatialExtractionProposal, ai_metadata_dict)
        """
        pass