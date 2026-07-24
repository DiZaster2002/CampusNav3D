import os
from celery import Celery

# Establecer el módulo de settings por defecto para Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Usar una cadena para que el worker no tenga que serializar el objeto de configuración
# El prefijo 'CELERY_' significa que todas las variables de celery deben empezar así en settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodescubrir tareas asíncronas en todas las apps instaladas (buscará archivos tasks.py)
app.autodiscover_tasks()