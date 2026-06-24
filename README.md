# CampusNav3D

> A Provider-Agnostic Architecture for AI-Assisted Generation of Navigable 2D/3D University Campus Models

## Descripción

CampusNav3D es una plataforma abierta para la generación de modelos espaciales navegables de edificios universitarios a partir de planos arquitectónicos. El sistema permite transformar planos 2D en modelos semánticos reutilizables, generar representaciones sincronizadas en 2D y 3D, construir grafos de navegación interior y calcular rutas accesibles mediante una arquitectura desacoplada de proveedores de Inteligencia Artificial.

El proyecto se desarrolla como Trabajo Fin de Grado (TFG) con el objetivo de evolucionar hacia un software de investigación reproducible, documentado y potencialmente publicable en la revista SoftwareX.

---

# Objetivos del proyecto

CampusNav3D persigue los siguientes objetivos principales:

* Transformar planos arquitectónicos en modelos espaciales estructurados y reutilizables.
* Generar automáticamente grafos de navegación interior.
* Permitir el cálculo de rutas entre espacios y plantas.
* Mantener sincronizadas las representaciones 2D, 3D y los grafos de navegación.
* Integrar distintos proveedores o modelos de IA mediante adaptadores intercambiables.
* Incorporar validación humana para garantizar la calidad de los modelos generados.
* Facilitar la reutilización del sistema en diferentes edificios e instituciones.
* Garantizar la reproducibilidad experimental y la trazabilidad de los resultados.

---

# Stack tecnológico

## Backend

* Python
* Django
* GeoDjango
* Django REST Framework (DRF)
* Celery
* Redis

## Base de datos espacial

* PostgreSQL
* PostGIS

## Frontend

* JavaScript / TypeScript
* Leaflet (visualización 2D)
* Three.js (visualización 3D)

## Formatos y estándares

* GeoJSON
* IndoorGML 2.0 (compatibilidad futura)

## Inteligencia Artificial

Arquitectura basada en adaptadores para permitir la integración de:

* Proveedores comerciales de IA
* Modelos locales
* Implementaciones simuladas para pruebas

## DevOps y reproducibilidad

* Docker
* Docker Compose
* GitHub Actions
* Testing automatizado
* Benchmark reproducible

---

# Arquitectura general

```text
┌───────────────────────────────────────────┐
│ Interfaces de Usuario                     │
│ Administración · Mapa 2D · Vista 3D       │
└───────────────────────────────────────────┘
                    │
┌───────────────────────────────────────────┐
│ API y Casos de Uso                        │
└───────────────────────────────────────────┘
                    │
┌───────────────────────────────────────────┐
│ Servicios de Dominio                      │
│ Modelo Espacial · Grafo · Rutas           │
└───────────────────────────────────────────┘
          │                      │
          ▼                      ▼
┌─────────────────┐    ┌────────────────────┐
│ Adaptadores IA  │    │ Motores Internos   │
└─────────────────┘    └────────────────────┘
                    │
┌───────────────────────────────────────────┐
│ Infraestructura                           │
│ PostgreSQL · PostGIS · Redis · Celery     │
└───────────────────────────────────────────┘
```

La IA no constituye la fuente de verdad final del sistema. Los resultados generados deberán ser validados automáticamente y podrán corregirse manualmente antes de su publicación.

---

# Funcionalidades previstas

## Gestión espacial

* Gestión de campus
* Gestión de edificios
* Gestión de plantas
* Gestión de espacios
* Gestión de accesos y puertas
* Gestión de conexiones verticales

## Procesamiento de planos

* Importación de PDF, PNG y JPG
* Preprocesamiento automático
* Extracción semántica asistida por IA
* Normalización de resultados
* Validación geométrica y topológica

## Navegación interior

* Generación automática de grafos
* Cálculo de rutas
* Rutas accesibles
* Navegación entre plantas

## Visualización

* Vista 2D interactiva
* Vista 3D sincronizada
* Resaltado cruzado entre vistas
* Visualización de rutas

---

# Objetivos de desarrollo

| Fase | Objetivo                           |
| ---- | ---------------------------------- |
| 0    | Auditoría y análisis del prototipo |
| 1    | Repositorio reproducible           |
| 2    | Modelo espacial y persistencia     |
| 3    | Grafo y sistema de rutas           |
| 4    | Visualización 2D y 3D              |
| 5    | Integración de proveedores IA      |
| 6    | Corrección humana y versionado     |
| 7    | Benchmark experimental             |
| 8    | Evaluación arquitectónica          |
| 9    | Documentación y publicación        |
| 10   | Redacción del artículo científico  |

---

# Principios de diseño

* Arquitectura desacoplada de proveedores de IA.
* Separación entre dominio, infraestructura e interfaces.
* Reproducibilidad experimental.
* Extensibilidad mediante patrones de diseño.
* Persistencia espacial basada en estándares abiertos.
* Sincronización entre modelo espacial, grafo y visualizaciones.
* Trazabilidad completa de ejecuciones y resultados.

---

# Estructura prevista del repositorio

```text
campusnav3d/
├── backend/
├── frontend/
├── workers/
├── docs/
├── schemas/
├── examples/
├── benchmark/
├── scripts/
├── README.md
├── LICENSE
├── CITATION.cff
├── docker-compose.yml
└── .env.example
```

---

# Estado actual

🚧 Proyecto en fase inicial de desarrollo.

Las primeras iteraciones estarán centradas en:

1. Definición del modelo espacial.
2. Implementación del almacenamiento geoespacial.
3. Generación de grafos de navegación.
4. Integración del pipeline de extracción.
5. Construcción de las visualizaciones 2D y 3D.
6. Preparación de la infraestructura reproducible para investigación.

---

# Hoja de ruta inmediata

* [ ] Configurar repositorio GitHub.
* [ ] Seleccionar licencia de software.
* [ ] Configurar Docker Compose.
* [ ] Definir modelo espacial mínimo.
* [ ] Diseñar esquema normalizado de extracción.
* [ ] Implementar `ProceduralExtractor`.
* [ ] Implementar interfaz de proveedor IA.
* [ ] Implementar `MockAIProvider`.
* [ ] Crear edificio sintético de demostración.
* [ ] Implementar primeras pruebas de geometría, grafos y rutas.

---

# Licencia

Pendiente de definición.

Opciones recomendadas:

* MIT
* Apache-2.0

---

# Citación

La información de citación se publicará mediante un archivo `CITATION.cff` cuando el proyecto alcance su primera versión estable.

---

# Contribuciones

Actualmente el proyecto se encuentra en desarrollo activo como parte de un Trabajo Fin de Grado. Las contribuciones externas serán habilitadas una vez se estabilice la arquitectura base.

---

# Contacto

Información de contacto pendiente de definir.

---

# Publicación científica prevista

El objetivo a medio plazo es preparar CampusNav3D para una posible publicación en SoftwareX, centrando la contribución en:

* Arquitectura desacoplada de proveedores de IA.
* Pipeline reproducible desde planos 2D hasta modelos navegables.
* Generación sincronizada de representaciones 2D y 3D.
* Construcción automática de grafos de navegación.
* Evaluación experimental reproducible.
* Publicación abierta del software y los materiales experimentales.
