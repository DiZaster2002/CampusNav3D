import logging
from celery import shared_task
from maps.services.ingestion_service import IngestionService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_spatial_plan_task(self, plan_id: int, provider_name: str = 'mock'):
    """
    Tarea asíncrona orquestadora (Celery Wrapper).
    Delega la ejecución de la ingesta y extracción a IngestionService.
    """
    try:
        IngestionService.process_plan(plan_id, provider_name=provider_name)
    except Exception as e:
        raise self.retry(exc=e, countdown=60)