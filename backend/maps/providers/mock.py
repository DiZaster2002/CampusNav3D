import uuid
import time
from typing import Tuple, Dict, Any
from maps.providers.base import AIExtractionProvider
from maps.models import SpatialPlan
from maps.schemas import SpatialExtractionProposal, WallContourProposal, Point2D

class MockProceduralAdapter(AIExtractionProvider):
    """
    Adaptador de línea base determinista (sin IA real).
    Retorna un esquema hardcodeado para validar el pipeline asíncrono y la integración con Pydantic.
    """
    def extract_layout(self, spatial_plan: SpatialPlan) -> Tuple[SpatialExtractionProposal, Dict[str, Any]]:
        # Simulamos un tiempo de procesamiento pesado (ej: 3 segundos)
        time.sleep(3)
        
        # Generamos una propuesta que cumple estrictamente con el contrato de Pydantic
        proposal = SpatialExtractionProposal(
            campus_external_id="mock_campus_01",
            building_code="mock_bld_A",
            floor_level=1,
            spaces=[
                WallContourProposal(
                    name="Sala de Pruebas",
                    external_id=str(uuid.uuid4()),
                    confidence=1.0,  # 100% al ser determinista
                    coordinates=[
                        Point2D(x=0.0, y=0.0),
                        Point2D(x=10.0, y=0.0),
                        Point2D(x=10.0, y=10.0),
                        Point2D(x=0.0, y=10.0)
                    ],
                    space_type="ROOM"
                )
            ],
            doors_and_connections=[]
        )
        
        # Metadatos falsos de facturación
        ai_metadata = {
            "provider": "MockProceduralAdapter",
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "estimated_cost_usd": 0.00
        }
        
        return proposal, ai_metadata