from django.shortcuts import get_object_or_404
from ..models import SpatialPlan, SpatialPlanStatus
from ..tasks import process_spatial_plan_task


class PlanService:
    """Servicio para la gestión del ciclo de vida y orquestación de planos espaciales."""

    @staticmethod
    def upload_and_enqueue_plan(serializer) -> SpatialPlan:
        """Persiste la subida del plano e inicia el job asíncrono en Celery."""
        ai_provider = serializer.validated_data.get('ai_provider', 'mock')

        spatial_plan = serializer.save(
            content_type=serializer.validated_data['content_type'],
            object_id=serializer.validated_data['target_id']
        )

        process_spatial_plan_task.delay(spatial_plan.id, provider_name=ai_provider)
        return spatial_plan

    @staticmethod
    def reject_plan(plan_id: int, reason: str = 'Sin motivo especificado') -> SpatialPlan:
        """Rechaza un plano manualmente cuando se encuentra en revisión."""
        plan = get_object_or_404(SpatialPlan, pk=plan_id)

        if plan.status != SpatialPlanStatus.REQUIRES_REVIEW:
            raise ValueError(f"El plano no se puede rechazar en su estado actual ({plan.status}).")

        plan.status = SpatialPlanStatus.REJECTED
        plan.error_log = f"Rechazado manualmente: {reason}"
        plan.save(update_fields=['status', 'error_log', 'updated_at'])

        return plan