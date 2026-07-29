import logging
from celery import shared_task
from maps.models import SpatialPlan, SpatialPlanStatus
from maps.providers.mock import MockProceduralAdapter

logger = logging.getLogger(__name__)

# Mapa de adaptadores disponibles (Soportará inyección dinámica de proveedores)
PROVIDERS_MAP = {
    'mock': MockProceduralAdapter,
    # Futuras integraciones:
    # 'openai': OpenAIProvider,
    # 'claude': ClaudeVisionProvider,
}

@shared_task(bind=True, max_retries=3)
def process_spatial_plan_task(self, plan_id: int, provider_name: str = 'mock'):
    """
    Tarea asíncrona principal para el procesamiento de planos.
    Maneja la máquina de estados de SpatialPlan y delega la extracción al proveedor de IA.
    """
    try:
        plan = SpatialPlan.objects.get(id=plan_id)
    except SpatialPlan.DoesNotExist:
        logger.error(f"SpatialPlan con ID {plan_id} no encontrado. Abortando tarea.")
        return

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

    # 1. Iniciar transición
    plan.transition_to(SpatialPlanStatus.PREPROCESSING)

    try:
        plan.transition_to(SpatialPlanStatus.EXTRACTING)

        # Inyección de dependencias basada en el parámetro seleccionado
        adapter_class = PROVIDERS_MAP.get(provider_name, MockProceduralAdapter)
        provider = adapter_class()
        
        # 3. Extraer layout usando el adaptador
        proposal, metadata = provider.extract_layout(plan)

        # 4. Guardar resultados volcando el modelo de Pydantic a JSON (model_dump en Pydantic v2)
        plan.intermediate_proposal = mock_geometries
        plan.ai_metadata = metadata

        plan.save(update_fields=['intermediate_proposal', 'ai_metadata'])
        
        # 5. Finalizar con éxito
        plan.transition_to(SpatialPlanStatus.REQUIRES_REVIEW)
        logger.info(f"Plano {plan_id} procesado exitosamente usando {provider_name}. Requiere revisión manual.")

    except Exception as e:
        logger.exception(f"Error procesando el plano {plan_id}")
        plan.transition_to(SpatialPlanStatus.FAILED, error_message=str(e))
        
        # Reencolar la tarea si falla (ej: si la API de OpenAI da un error 503)
        raise self.retry(exc=e, countdown=60) # Reintenta en 60 segundos