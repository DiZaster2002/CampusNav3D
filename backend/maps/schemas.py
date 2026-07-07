# maps/schemas.py
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field

class Point2D(BaseModel):
    x: float = Field(..., description="Coordenada X normalizada o en píxeles")
    y: float = Field(..., description="Coordenada Y normalizada o en píxeles")

class ExtractedElement(BaseModel):
    name: str = Field(..., description="Nombre propuesto para el elemento (ej: Aula 101, Pasillo A)")
    external_id: str = Field(..., description="ID temporal inmutable generado por el extractor")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Nivel de confianza de la IA")

class WallContourProposal(ExtractedElement):
    # Lista de puntos que forman el polígono del espacio interior
    coordinates: List[Point2D] = Field(..., description="Polígono cerrado del espacio")
    space_type: str = Field(default="ROOM", description="Tipo de espacio de IndoorGML (ROOM, CORRIDOR, STAIRS)")

class DoorProposal(ExtractedElement):
    # Punto central de la puerta o línea de umbral
    location: Tuple[float, float] = Field(..., description="Coordenadas [x, y] de la transición")
    connects_with: List[str] = Field(..., max_items=2, description="Contiene los external_id de las dos celdas que conecta")

class SpatialExtractionProposal(BaseModel):
    """Contrato final uniforme para la salida de cualquier adaptador de IA."""
    campus_external_id: str
    building_code: str
    floor_level: int
    spaces: List[WallContourProposal] = Field(default_factory=list)
    doors_and_connections: List[DoorProposal] = Field(default_factory=list)