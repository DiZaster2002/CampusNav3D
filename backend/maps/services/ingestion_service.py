import logging
from ..models import SpatialPlan, SpatialPlanStatus
from ..providers.mock import MockProceduralAdapter

logger = logging.getLogger(__name__)

PROVIDERS_MAP = {
    'mock': MockProceduralAdapter,
    # Futuras integraciones:
    # 'openai': OpenAIProvider,
    # 'claude': ClaudeVisionProvider,
}


class IngestionService:
    """Servicio para la extracción, preprocesamiento e ingesta con IA de planos espaciales."""

    @classmethod
    def process_plan(cls, plan_id: int, provider_name: str = 'mock') -> SpatialPlan | None:
        """
        Orquesta el preprocesamiento de la imagen, la extracción mediante el adaptador seleccionado
        y la actualización de estados de la máquina de estados.
        """
        try:
            plan = SpatialPlan.objects.get(id=plan_id)
        except SpatialPlan.DoesNotExist:
            logger.error(f"SpatialPlan con ID {plan_id} no encontrado. Abortando procesamiento.")
            return None

        mock_geometries = {
            "spaces": [
                {
                    "name": "Laboratorio 01",
                    "type": "LAB",
                    "coordinates": [[0.0, 0.0], [0.0, 8.0], [8.0, 8.0], [8.0, 0.0], [0.0, 0.0]]
                },
                {
                    "name": "Despacho A",
                    "type": "OFFICE",
                    "coordinates": [[8.0, 0.0], [8.0, 8.0], [12.0, 8.0], [12.0, 0.0], [8.0, 0.0]]
                }
            ]
        }

        # 1. Transición a Preprocesamiento
        plan.transition_to(SpatialPlanStatus.PREPROCESSING)

        try:
            # 2. Transición a Extracción
            plan.transition_to(SpatialPlanStatus.EXTRACTING)

            # Inyección de dependencias basada en el parámetro seleccionado
            adapter_class = PROVIDERS_MAP.get(provider_name, MockProceduralAdapter)
            provider = adapter_class()

            # 3. Extraer layout usando el adaptador
            proposal, metadata = provider.extract_layout(plan)

            # 4. Guardar resultados
            plan.intermediate_proposal = mock_geometries
            plan.ai_metadata = metadata
            plan.save(update_fields=['intermediate_proposal', 'ai_metadata'])

            # 5. Finalizar con éxito
            plan.transition_to(SpatialPlanStatus.REQUIRES_REVIEW)
            logger.info(f"Plano {plan_id} procesado exitosamente usando {provider_name}. Requiere revisión manual.")
            return plan

        except Exception as e:
            logger.exception(f"Error procesando el plano {plan_id}")
            plan.transition_to(SpatialPlanStatus.FAILED, error_message=str(e))
            raise e