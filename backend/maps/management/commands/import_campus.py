import json
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from maps.patterns import (
    BuildingImportStep,
    CampusImportStep,
    FloorImportStep,
    ImportComposite,
    NavigationEdgeImportStep,
    SpaceImportStep,
    SpatialEntityFactory,
)

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

                factory = SpatialEntityFactory({
                    'campus': CampusImportStep(),
                    'building': BuildingImportStep(),
                    'floor': FloorImportStep(),
                    'spaces': SpaceImportStep(),
                    'edges': NavigationEdgeImportStep(),
                })

                pipeline = ImportComposite([
                    factory.create_handler('campus'),
                    factory.create_handler('building'),
                    factory.create_handler('floor'),
                    factory.create_handler('spaces'),
                    factory.create_handler('edges'),
                ])

                context = pipeline.process(data, {})

                campus = context['campus']
                building = context['building']
                floor = context['floor']
                self.stdout.write(f" -> Campus: {campus.name} [{'Creado' if context['campus_created'] else 'Ya existía'}]")
                self.stdout.write(f"   -> Edificio: {building.name} [{'Creado' if context['building_created'] else 'Ya existía'}]")
                self.stdout.write(f"     -> Planta: {floor.name} (Nivel {floor.level}) [{'Creado' if context['floor_created'] else 'Ya existía'}]")

                for space in context['spaces'].values():
                    self.stdout.write(f"       -> Espacio Celda: {space.name} ({space.external_id})")

                for edge, created in context['edges']:
                    self.stdout.write(self.style.SUCCESS(f"         + Grafo Edge Conectado: {edge.source_space.name} -> {edge.target_space.name} [{'Creado' if created else 'Ya existía'}]"))

                self.stdout.write(self.style.SUCCESS("¡Pipeline ejecutado con éxito! El modelo espacial está completamente sincronizado."))

        except Exception as e:
            raise CommandError(f"Transacción abortada debido a un error en el procesamiento espacial: {e}")