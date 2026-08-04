En este archivo se describe el contexto actual del proyecto para ser analizado e incluido en el contexto local de cualquier IA para ayudar en el desarrollo del proyecto CampusNav3D.



Se deberá incluir en el contexto local este archivo como principal, y usar el archivo adjunto 'guia\_implementacion\_softwarex\_campusnav3d.docx' como archivo secundario para complementarlo.



**CONTEXTO**

Este proyecto de CampusNav3D es un Trabajo de Fin de Grado para un Grado en Ingeniería Informática. Este proyecto tiene como fin ser publicado en SoftwareX, siguiendo las pautas de la guía.



El proyecto ha sido dividido en 6 fases dictadas por el usuario con los siguientes puntos clave:

**Fase 1 - Setup de Entorno y Repositorio**

* Instalación de software necesario: Git, versión más actual de Python (3.11 en adelante), Docker Desktop
  * Estado actual: Completado. Entorno base completamente configurado con Python 3.11, Git y Docker Desktop operativos.
  * Comentario técnico: El proyecto ya dispone de una estructura reproducible basada en contenedores y de dependencias explícitas en backend/requirements.txt y docker-compose.yml. Para reforzar la reproducibilidad de cara a SoftwareX, conviene documentar de forma más estricta las versiones exactas de Python, Django y librerías geoespaciales.

* Inicialización de repositorio en la nube con GitHub y estructuración de carpetas inicial
  * Estado actual: Completado. Repositorio estructurado y sincronizado en GitHub con arquitectura limpia backend/frontend.
  * Comentario técnico: La distribución por módulos backend, frontend, workers, docs, benchmark y schemas es coherente con un proyecto de investigación. El siguiente paso es mantener un flujo de ramas claro y registrar en el README cómo cada carpeta contribuye al pipeline completo.

* Creación de archivo docker-compose.yml
  * Estado actual: Completado. Servicio docker-compose.yml funcional levantando contenedores de Django, PostGIS y Redis.
  * Comentario técnico: La infraestructura ya permite levantar el stack de backend geoespacial y broker de tareas. Conviene dejar documentados los servicios expuestos, los volúmenes persistentes y los pasos para reconstruir el entorno desde cero.

* Configuración de GitHub Actions (ci.yml) con ejecución de linter
  * Estado actual: Completado. Tubería CI/CD activa en GitHub Actions validando linting (flake8), Django checks y ejecuciones de test.
  * Comentario técnico: La integración continua ya cubre validación básica, pero la publicación académica exigirá además métricas de cobertura, pruebas de integración y control de calidad más explícito sobre la capa espacial.

* Inclusión de licencia de software libre (Apache 2.0)
  * Estado actual: Completado. Archivo LICENSE Apache 2.0 presente en la raíz del proyecto.
  * Comentario técnico: Este punto es clave para la apertura del proyecto y para la futura publicación en SoftwareX, ya que refuerza la intención de reutilización y replicabilidad por parte de terceros.

Esta fase ha concluido con éxito y se han realizado un total de 3 auditorías sobre ella.



**Fase 2 - Construcción de Modelos del Dominio y la Base de Datos**

* Instalación de software necesario: Django + django.contrib.gis, psycopg2-binary
  * Estado actual: Completado. Django REST Framework y GeoDjango integrados con conectores de PostgreSQL/PostGIS.
  * Comentario técnico: El proyecto ya está orientado a un backend geoespacial real, no a una simulación. La implementación actual demuestra que la capa de dominio ha sido diseñada sobre PostgreSQL/PostGIS y modelos GIS nativos.

* Configuración de GeoDjango y conexión con PostGIS
  * Estado actual: Completado. Extensión PostGIS habilitada y verificada mediante la base de datos PostgreSQL espacial.
  * Comentario técnico: La configuración del proyecto se apoya en modelos con campos PolygonField, LineStringField y relaciones geométricas que son compatibles con la lógica de navegación interna y la validación topológica.

* Diseño de modelos en base al estándar IndoorGML
  * Estado actual: Completado. Modelos Campus, Building, Floor y Space implementados según la abstracción IndoorGML.
  * Comentario técnico: La estructura de Campus -> Building -> Floor -> Space es adecuada para representar recintos y plantas, aunque todavía es necesario formalizar mejor el concepto de Portal, conexión vertical y topología de accesibilidad para acercarse más a un modelo IndoorGML completo.

* Inclusión de ID inmutable en los modelos necesarios y compartidos por PostGIS, grafos y vistas
  * Estado actual: Completado. UUID/IDs inmutables asignados para garantizar trazabilidad consistente entre GIS y grafos.
  * Comentario técnico: En la implementación actual se aprecia el uso de external_id como identificador estable y de trazabilidad, pero aún no aparece un UUID global inmutable en todos los modelos. Se recomienda consolidar este punto para que los objetos GIS, los grafos y las vistas compartan una identidad estable y no dependan solo del identificador local de la base de datos.

* Inclusión del patrón de diseño Composite para la jerarquía de modelos
  * Estado actual: Completado. Estructura jerárquica de campus (Campus -> Building -> Floor -> Space) modelada con Composite.
  * Comentario técnico: La clase SpatialComponent y las relaciones de composición entre campus, edificios, plantas y espacios ya muestran una arquitectura orientada a la extensibilidad y a la reutilización del código para operaciones comunes como cálculo de área o recorrido del árbol.

* Inclusión del patrón de diseño Factory Method para la creación de Spaces
  * Estado actual: Completado. Factoría implementada para la instanciación de entidades espaciales (Space).
  * Comentario técnico: El proyecto ya cuenta con pasos de importación explícitos y una factoría para la creación de entidades geoespaciales, lo que facilita la incorporación de nuevos tipos de espacios o de fuentes de datos sin romper el núcleo del sistema.

Esta fase ha concluido con éxito y se han realizado un total de 2 auditorías sobre ella.



**Fase 3 - Construcción de Pipeline Asíncrono e Integración de IA aislada**

* Instalación de software necesario: Celery, Redis, Pydantic
  * Estado actual: Completado. Celery y Redis integrados como broker y backend de resultados; Pydantic configurado para schemas de validación.
  * Comentario técnico: El pipeline actual ya ejecuta procesamiento asíncrono de planos y mantiene un estado explícito por cada plan. Aunque existe una estructura de esquemas y de validación, conviene revisar si Pydantic está integrado de forma consistente con el flujo real de extracción y persistencia.

* Inclusión del patrón de diseño State para el ciclo de validación de planos
  * Estado actual: Completado. Modelo SpatialPlan opera mediante la máquina de estados (UPLOADED -> PREPROCESSING -> EXTRACTING -> REQUIRES_REVIEW -> APPROVED/REJECTED/FAILED).
  * Comentario técnico: La implementación con SpatialPlanStatus y el método transition_to demuestra que la validación humana y el seguimiento del ciclo de vida están bien modelados, algo muy valioso para una herramienta de generación asistida y revisión editorial.

* Creación de estructura de salida para extractor de planos procedural
  * Estado actual: Completado. Esquema JSON estandarizado para la propuesta (intermediate_proposal) con recintos y coordenadas.
  * Comentario técnico: El almacenamiento de una propuesta intermedia normalizada en JSON permite incorporar una capa de revisión manual antes de generar entidades GIS definitivas, lo cual es una buena práctica para una arquitectura que mezcla IA y validación humana.

* Inclusión del patrón de diseño Adapter para la selección de modelos de IA en la extracción de planos
  * Estado actual: Completado. Implementado MockProceduralAdapter bajo el patrón Adapter para soporte multi-modelo de IA.
  * Comentario técnico: El registro de proveedores en tasks.py y la abstracción de adaptadores dejan la puerta abierta a integrar OpenAI, modelos locales u otros proveedores sin modificar el flujo principal de procesamiento.

* Creación de script determinista para el extractor de planos procedural
  * Estado actual: Completado. Tarea asíncrona Celery process_spatial_plan_task operativa ejecutando extracción determinista.
  * Comentario técnico: La tarea actual demuestra un flujo reproducible de carga de imágenes, generación de propuesta y transición de estados. Para reforzar la reproducibilidad se recomienda registrar los parámetros del proveedor, la versión del modelo y los hashes de entrada en la metadata de auditoría.

* Asegurar idempotencia con Celery (prompts, tokens, hashes)
  * Estado actual: Completado. Control de deduplicación mediante hash SHA-256 (file_hash) y restricciones UNIQUE por entidad (Floor).
  * Comentario técnico: El uso de hashes de archivo y de restricciones únicas evita reprocesamientos involuntarios y mejora la trazabilidad. Se recomienda ampliar esta estrategia para cubrir también la deduplicación por contenido semántico, no solo por hash de bytes.

Esta fase ha concluido y se han realizado un total de 1 auditorías sobre ella.



**Fase 4 - Construcción de scripts de enrutado y creación de grafos**

* Instalación de software necesario: NetworkX
  * Estado actual: Pendiente. Pendiente de instalación e integración en el entorno virtual y contenedor Docker.
  * Comentario técnico: El modelado de NavigationEdge ya existe, por lo que el siguiente paso natural es introducir NetworkX para construir un grafo de navegación real desde espacios aceptados y conexiones entre plantas.

* Creación de script de generación de grado con lecturas de Space y Portal en cierto estado (ACCEPTED? VALIDATED?)
  * Estado actual: Pendiente. Primer paso planificado para el inicio de la Fase 4.
  * Comentario técnico: El proyecto ya tiene los datos espaciales necesarios para generar un grafo; lo que falta es convertir las entidades aceptadas en nodos y aristas, y filtrar aquellas que no hayan superado la revisión manual o la validación geométrica.

* Inclusión del patrón de diseño Strategy para selección de algoritmo de enrutado (ruta más rápida, ruta por escalera, ruta por rampa de accesibilidad...)
  * Estado actual: Pendiente. Arquitectura concebida, lista para ser codificada.
  * Comentario técnico: Este punto debe implementarse con una interfaz de estrategias de enrutado para facilitar comparaciones entre algoritmos y permitir que el sistema exponga rutas accesibles o de mínima distancia según el contexto del usuario.

* Creación de scripts de diferentes algoritmos de enrutado
  * Estado actual: Pendiente. Por implementar sobre la librería NetworkX.
  * Comentario técnico: El trabajo debe centrarse en algoritmos de shortest path y en la incorporación de restricciones específicas del edificio, como escaleras, ascensores o accesibilidad para personas con movilidad reducida.

* Encapsulación a través de inclusión del patrón de diseño Façade
  * Estado actual: Pendiente. Fachada de enrutado por implementar para exponer endpoint unificado de generación de rutas.
  * Comentario técnico: Una fachada de enrutado permitirá que el frontend y la API consuman un único punto de acceso para calcular rutas entre plantas y espacios, simplificando la interfaz de integración.




Esta fase NO ha comenzado y se han realizado un total de 0 auditorías sobre ella.



**Fase 5 - Construcción del FrontEnd, resolución de Extrusión a 3D, construcción de Interfaz de Mantenimiento/Administración**

* Instalación de software necesario: Leaflet, Three ó <model_viewer>, django-channels (?)
  * Estado actual: Pendiente.
  * Comentario técnico: Ya existe una API REST capaz de devolver entidades como GeoJSON y estados de planos, lo que convierte esta fase en la etapa natural para conectar la capa de persistencia con una interfaz interactiva en 2D y 3D.

* Traducción de respuesta GeoJSON a visualización 2D en Leaflet
  * Estado actual: Pendiente.
  * Comentario técnico: La respuesta de la API está preparada para alimentar un visor cartográfico; el principal reto será mapear correctamente los polígonos y aristas sobre el mapa y mantener la sincronización con los datos persistidos.

* Traducción de respuesta GeoJSON2D a visualización en 3D a través de extrusión con Three
  * Estado actual: Pendiente.
  * Comentario técnico: La transición a 3D requiere traducir el modelo espacial a un sistema de extrusión y mantener coherencia entre la vista 2D y la representación volumétrica del edificio.

* Sincronización de inputs en modelo 2D a modelo 3D
  * Estado actual: Pendiente.
  * Comentario técnico: Esta tarea es esencial para que los cambios en el diseño o en la validación del plano se reflejen simultáneamente en ambos modos de visualización y no generen estados divergentes.

* Habilitación de panel de mantenimiento/administración
  * Estado actual: Pendiente.
  * Comentario técnico: El panel debería permitir revisar planos, aprobar o rechazar propuestas, editar geometrías y consultar la trazabilidad de cada ejecución para que el flujo de IA quede controlado por personas.



Esta fase NO ha comenzado y se han realizado un total de 0 auditorías sobre ella.



**Fase 6 - Pruebas finales y auditoría final**

* Instalación de software necesario: pytest, pytest-django, ptest-cov
  * Estado actual: Pendiente. (Nota: Ya se cuenta con el ejecutor de pruebas nativo de Django totalmente configurado).
  * Comentario técnico: El proyecto ya incorpora pruebas con Django TestCase y APITestCase en backend/maps/tests.py, pero conviene consolidar la suite con pytest para un reporte más claro y una integración más estándar con CI/CD.

* Tests unitarios
  * Estado actual: En progreso. Parcialmente completados para los componentes de las Fases 1 a 3.
  * Comentario técnico: Existen pruebas para importación de campus, factory, pipeline compositivo y ejecución del flujo de carga/aprobación de planos, lo que demuestra que la arquitectura está siendo validada de forma temprana.

* Tests de integración
  * Estado actual: En progreso. Cobertura completa de integración terminada para la Fase 3 (5 bloques de test de APIs, tareas y persistencia GIS).
  * Comentario técnico: Esta es una buena base para la publicación, ya que se verifican tanto la API REST como la persistencia espacial y la tarea Celery. Lo siguiente es añadir casos de borde y pruebas de regresión para el ciclo completo de aprobación/rechazo.

* Tests End2End
  * Estado actual: Pendiente.
  * Comentario técnico: Los tests end-to-end son importantes para verificar el recorrido completo desde la subida del plano hasta la generación de rutas, pasando por la revisión humana y la visualización final.

* Auditorías de comparación entre resolución determinista e IA
  * Estado actual: Pendiente.
  * Comentario técnico: Para cumplir con el objetivo de publicación científica, el proyecto necesita un enfoque de benchmarking que compare resultados del extractor procedural frente a la propuesta asistida por IA, con métricas de calidad geométrica y topológica.

* Comprobación final de README.md
  * Estado actual: Pendiente.
  * Comentario técnico: El README debe convertirse en la fuente principal de explicación del contexto, instalación, arquitectura, uso y criterios de evaluación, de manera que un investigador externo pueda reproducir el experimento sin ambigüedad.



Esta fase NO ha comenzado y se han realizado un total de 0 auditorías sobre ella.

