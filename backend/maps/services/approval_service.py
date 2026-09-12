from django.db import transaction
from django.shortcuts import get_object_or_404
from django.contrib.gis.geos import Polygon

from ..models import SpatialPlan, SpatialPlanStatus, Space, Floor


class ApprovalService:
    """Servicio especializado en la conversión de propuestas JSON a entidades GIS en PostGIS."""

    @classmethod
    @transaction.atomic
    def approve_plan(cls, plan_id: int, edited_draft_data: dict = None) -> tuple[SpatialPlan, list[int]]:
        """
        Valida la propuesta vectorial, crea las geometrías de tipo Space en PostGIS
        y actualiza el estado del plano a APPROVED dentro de una transacción atómica.
        """
        plan = get_object_or_404(SpatialPlan, pk=plan_id)

        if plan.status != SpatialPlanStatus.REQUIRES_REVIEW:
            raise ValueError(f"El plano no se encuentra en estado REQUIRES_REVIEW (estado actual: {plan.status}).")

        intermediate_proposal = edited_draft_data or plan.intermediate_proposal

        if not intermediate_proposal:
            raise ValueError("No existen datos de borrador (intermediate_proposal) asociados a este plano.")

        spaces_data = intermediate_proposal.get('spaces', [])

        if not spaces_data or len(spaces_data) == 0:
            raise ValueError("No se puede aprobar un plano sin geometría. La propuesta no contiene ningún espacio/recinto válido.")

        created_spaces = []
        target_obj = plan.spatial_object

        for space_info in spaces_data:
            coords = space_info.get('coordinates', [])
            if len(coords) >= 3:
                # Garantizar polígono cerrado para PostGIS
                if coords[0] != coords[-1]:
                    coords.append(coords[0])

                try:
                    poly = Polygon(coords)
                    space = Space.objects.create(
                        floor=target_obj if isinstance(target_obj, Floor) else None,
                        name=space_info.get('name', 'Espacio Detectado'),
                        space_type=space_info.get('type', 'ROOM'),
                        geometry=poly
                    )
                    created_spaces.append(space.id)

                except Exception as e:
                    raise ValueError(f"Error al crear el espacio '{space_info.get('name')}': {str(e)}")

        plan.status = SpatialPlanStatus.APPROVED
        if edited_draft_data:
            plan.intermediate_proposal = edited_draft_data
        plan.save(update_fields=['status', 'intermediate_proposal', 'updated_at'])

        return plan, created_spaces