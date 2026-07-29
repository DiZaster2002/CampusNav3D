# maps/providers/base.py
from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any
from maps.models import SpatialPlan
from maps.schemas import SpatialExtractionProposal

class AIExtractionProvider(ABC):
    """
    Interfaz Abstracta para los proveedores de extracción (Patrón Adapter).
    Garantiza el cumplimiento estricto de OCP.
    """
    
    @abstractmethod
    def extract_layout(self, spatial_plan: SpatialPlan) -> Tuple[SpatialExtractionProposal, Dict[str, Any]]:
        """
        Procesa la imagen del SpatialPlan y retorna una estructura normalizada 
        junto con el diccionario de metadatos de rendimiento/coste de la IA.
        
        Retorna:
            (SpatialExtractionProposal, ai_metadata_dict)
        """
        pass