import json
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify
from django.contrib.gis.geos import GEOSGeometry
from maps.models import Campus, Building, Floor, Space, NavigationEdge

class Command(BaseCommand):
    help = 'Carga y automatiza la ingesta procedimental de un campus completo desde un manifiesto JSON'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Ruta al archivo JSON con los datos del campus')

    def handle(self, *args, **options):
        json_file_path = options['json_file']

        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            raise CommandError(f"Error al leer el archivo JSON: {e}")

        # Ejecutamos todo dentro de una transacción atómica: si algo falla, no se guarda nada intermedio
        try:
            with transaction.atomic():
                self.stdout.write(self.style.MIGRATE_LABEL("Iniciando pipeline de ingesta geoespacial..."))

                # 1. Crear Campus
                campus_data = data['campus']
                campus, created = Campus.objects.get_or_create(
                    slug=slugify(campus_data['name']),
                    external_id=campus_data['external_id'],
                    defaults={
                        'name': campus_data['name'],
                        'geometry': GEOSGeometry(campus_data['geometry'])
                    }
                )
                self.stdout.write(f" -> Campus: {campus.name} [{'Creado' if created else 'Ya existía'}]")

                # 2. Crear Edificio
                b_data = data['building']
                building, created = Building.objects.get_or_create(
                    code=b_data['code'],
                    external_id=b_data['external_id'],
                    defaults={
                        'name': b_data['name'],
                        'campus': campus,
                        'geometry': GEOSGeometry(b_data['geometry'])
                    }
                )
                self.stdout.write(f"   -> Edificio: {building.name} [{'Creado' if created else 'Ya existía'}]")

                # 3. Crear Planta
                f_data = data['floor']
                floor, created = Floor.objects.get_or_create(
                    building=building,
                    level=f_data['level'],
                    external_id=f_data['external_id'],
                    defaults={
                        'name': f_data['name'],
                        'altitude': f_data['altitude'],
                        'geometry': GEOSGeometry(f_data['geometry'])
                    }
                )
                self.stdout.write(f"     -> Planta: {floor.name} (Nivel {floor.level}) [{'Creado' if created else 'Ya existía'}]")

                # 4. Crear Espacios (Guardando en un diccionario para mapear las aristas después)
                spaces_map = {}
                for s_data in data['spaces']:
                    space, created = Space.objects.get_or_create(
                        floor=floor,
                        external_id=s_data['external_id'],
                        defaults={
                            'name': s_data['name'],
                            'space_type': s_data['space_type'],
                            'geometry': GEOSGeometry(s_data['geometry'])
                        }
                    )
                    spaces_map[space.external_id] = space
                    self.stdout.write(f"       -> Espacio Celda: {space.name} ({space.external_id})")

                # 5. Crear Aristas del Grafo de Navegación Interior
                for e_data in data['edges']:
                    source = spaces_map.get(e_data['source_external_id'])
                    target = spaces_map.get(e_data['target_external_id'])
                    
                    if not source or not target:
                        self.stdout.write(self.style.WARNING(f" Skip Edge '{e_data['name']}': Nodos no encontrados en el mapa local."))
                        continue

                    edge, created = NavigationEdge.objects.get_or_create(
                        source_space=source,
                        target_space=target,
                        defaults={
                            'name': e_data['name'],
                            'geometry': GEOSGeometry(e_data['geometry']),
                            'is_accessible': True
                        }
                    )
                    self.stdout.write(self.style.SUCCESS(f"         + Grafo Edge Conectado: {edge.source_space.name} -> {edge.target_space.name}"))

                self.stdout.write(self.style.SUCCESS("¡Pipeline ejecutado con éxito! El modelo espacial está completamente sincronizado."))

        except Exception as e:
            raise CommandError(f"Transacción abortada debido a un error en el procesamiento espacial: {e}")