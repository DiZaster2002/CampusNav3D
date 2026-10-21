# CampusNav3D

[![CI](https://github.com/DiZaster2002/CampusNav3D/actions/workflows/ci.yml/badge.svg)](https://github.com/DiZaster2002/CampusNav3D/actions/workflows/ci.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

> A provider-agnostic architecture for AI-assisted generation of navigable 2D/3D university campus models.

## Overview

CampusNav3D is an open platform that turns architectural floor plans into navigable spatial models of university buildings. A plan is uploaded, an AI provider proposes the spaces it contains, a person reviews the proposal, and the approved spaces are stored in a spatial database. From those spaces and the connections between them, the system builds a navigation graph and computes indoor routes, including routes that avoid stairs.

The project is developed as a final-year degree thesis (TFG) and is being prepared as reproducible research software, with [SoftwareX](https://www.sciencedirect.com/journal/softwarex) as the target venue.

### Goals

* Turn architectural plans into structured, reusable spatial models.
* Generate indoor navigation graphs automatically.
* Compute routes between spaces and floors, including accessible routes.
* Keep the 2D view, the 3D view and the navigation graph synchronised.
* Integrate different AI providers through interchangeable adapters.
* Keep a human in the loop: the AI output is a proposal, never the source of truth.
* Make the system reusable across buildings and institutions, and its results reproducible.

## Project status

The backend (domain model, asynchronous pipeline, navigation graph and routing API) is implemented and covered by an automated test suite. The frontend has only just started. Phases follow the numbering of the project's implementation guide.

Legend: ✅ done · 🔶 partially implemented · ▶️ started · ⏳ not started

| Phase | Objective | Status | Notes |
| ----- | --------- | ------ | ----- |
| 0 | Prototype audit and analysis | ✅ | |
| 1 | Reproducible repository | ✅ | Docker Compose stack, CI, Dependabot, Apache 2.0 licence |
| 2 | Spatial model and persistence | ✅ | `Campus → Building → Floor → Space` and navigation edges in PostGIS. Portals and vertical connections are not modelled yet |
| 3 | Graph and routing system | 🔶 | Graph builder, fastest and accessible strategies, facade and `/api/route/` endpoint. Refinements pending, see [Known limitations](#known-limitations) |
| 4 | 2D and 3D visualisation | ▶️ | React scaffold with login, a placeholder admin page and a public campus list. No map and no 3D view yet |
| 5 | AI provider integration | 🔶 | Provider interface, mock provider and asynchronous pipeline. No real AI provider yet |
| 6 | Human correction and versioning | 🔶 | List, review, approve and reject endpoints. No editing interface and no model versioning |
| 7 | Reproducible benchmark | ⏳ | |
| 8 | Architectural evaluation | ⏳ | |
| 9 | Documentation and publication | ⏳ | |
| 10 | Scientific article | ⏳ | |

## How it works

```text
┌───────────────────────────────────────────┐
│ User interfaces                           │
│ Administration · 2D map · 3D view         │
└───────────────────────────────────────────┘
                    │
┌───────────────────────────────────────────┐
│ REST API (Django REST Framework)          │
└───────────────────────────────────────────┘
                    │
┌───────────────────────────────────────────┐
│ Domain services                           │
│ Spatial model · Graph · Routing           │
└───────────────────────────────────────────┘
          │                      │
          ▼                      ▼
┌─────────────────┐    ┌────────────────────┐
│ AI adapters     │    │ Internal engines   │
└─────────────────┘    └────────────────────┘
                    │
┌───────────────────────────────────────────┐
│ Infrastructure                            │
│ PostgreSQL · PostGIS · Redis · Celery     │
└───────────────────────────────────────────┘
```

The backend runs two independent flows that meet only in the database.

**Flow A: from a plan to spaces**

1. `POST /api/plans/upload/` validates the file (size, extension, MIME type, content signature, duplicates) and stores a `SpatialPlan` in the `UPLOADED` state.
2. A Celery task is queued and the API answers `202 Accepted` immediately.
3. The task moves the plan through `PREPROCESSING` and `EXTRACTING`, calls the selected AI provider through its adapter, stores a proposal (see [Known limitations](#known-limitations), item 1) and sets the state to `REQUIRES_REVIEW`.
4. A person approves (optionally sending a corrected proposal) or rejects the plan. Approval creates the `Space` records in a single transaction and sets the state to `APPROVED`.

**Flow B: from two spaces to a route**

1. `GET /api/route/` receives the origin, the destination and a preference (`fastest` or `accessible`).
2. `NavigationFacade` selects a routing strategy, `GraphBuilder` builds a NetworkX directed graph from the stored spaces and edges, and the strategy computes the shortest path.
3. The response contains the ordered path enriched with the name, type, building, floor and centroid of each space.

### Design patterns

| Pattern | Where it is used |
| ------- | ---------------- |
| Composite | `SpatialComponent` and the `Campus → Building → Floor → Space` hierarchy; the import steps |
| Factory | `SpatialEntityFactory` builds the import handlers |
| State | `SpatialPlan` lifecycle (`SpatialPlanStatus`, `transition_to`) |
| Adapter | `AIExtractionProvider` interface and its providers |
| Strategy | `RoutingStrategy` with `FastestPathStrategy` and `AccessiblePathStrategy` |
| Façade | `NavigationFacade`, the single entry point for routing |

## Technology stack

| Area | Technology |
| ---- | ---------- |
| Backend | Python 3.11, Django 5.2, GeoDjango, Django REST Framework, DRF-GIS, drf-spectacular |
| Spatial database | PostgreSQL with PostGIS (`postgis/postgis:15-3.3`) |
| Asynchronous work | Celery with Redis |
| Validation and graphs | Pydantic, NetworkX |
| Frontend | React 18, Vite, React Router, Axios, generated TypeScript API client |
| Planned frontend | Leaflet (2D) and Three.js (3D) |
| Formats | GeoJSON; IndoorGML 2.0 compatibility planned |
| DevOps | Docker, Docker Compose, GitHub Actions, Dependabot |

## Repository structure

```text
CampusNav3D/
├── .github/
│   ├── workflows/ci.yml        # CI: lint, tests, dependency audit, Docker validation
│   └── dependabot.yml          # Weekly dependency updates
├── backend/
│   ├── core/                   # Django project: settings, URLs, Celery app
│   ├── maps/                   # Main application
│   │   ├── models/             # Campus, Building, Floor, Space, NavigationEdge, SpatialPlan
│   │   ├── providers/          # AI provider interface and mock provider
│   │   ├── services/           # Plan upload, ingestion and approval services
│   │   ├── management/commands/# import_campus, check_networkx
│   │   ├── tests/              # Automated test suite
│   │   ├── graph_builder.py    # Database to NetworkX graph
│   │   ├── routing_strategies.py
│   │   ├── navigation_facade.py
│   │   ├── patterns.py         # Import steps and entity factory
│   │   ├── schemas.py          # Pydantic contract for AI extraction output
│   │   ├── serializers.py, views.py, urls.py, tasks.py
│   │   └── geometry_utils.py   # WGS84 and GeoJSON validation
│   ├── examples/campus_sample.json
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # React + Vite application
│   └── src/api/                # Generated API client
├── test_img/                   # Sample plan images
├── openapi-schema.yaml         # OpenAPI schema of the REST API
├── docker-compose.yml
├── .env.example
├── agent.md, context.md        # Context files for AI-assisted development
└── LICENSE
```

## Getting started

### Prerequisites

* Docker Desktop (v20.10 or later) with Docker Compose v2.
* Node.js and npm, only to run the frontend.

### Run the backend

1. Clone the repository.

   ```bash
   git clone https://github.com/DiZaster2002/CampusNav3D.git
   cd CampusNav3D
   ```

2. Create the environment file and set at least `POSTGRES_PASSWORD`.

   ```bash
   cp .env.example .env
   ```

3. Build and start the stack (PostGIS, Redis, Django and the Celery worker).

   ```bash
   docker compose up --build
   ```

4. In another terminal, apply the migrations and create an administrator account.

   ```bash
   docker compose exec web python manage.py migrate
   docker compose exec web python manage.py createsuperuser
   ```

5. Load the sample campus (one building, one floor, two spaces and one connection).

   ```bash
   docker compose exec web python manage.py import_campus examples/campus_sample.json
   ```

Only the backend is published to the host, on `http://localhost:8000`. PostgreSQL and Redis are reachable only from inside the Compose network.

| URL | Purpose |
| --- | ------- |
| `http://localhost:8000/api/` | REST API root |
| `http://localhost:8000/api/docs/` | Swagger UI |
| `http://localhost:8000/api/redoc/` | ReDoc |
| `http://localhost:8000/api/schema/` | OpenAPI schema |
| `http://localhost:8000/admin/` | Django administration |

### Run the frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend expects the backend at `http://localhost:8000` (set in `frontend/src/config.js`).

## Using the API

Authentication uses tokens. Obtain one with your account and send it in the `Authorization` header.

```bash
curl -X POST http://localhost:8000/api/login/ \
  -d "username=<user>&password=<password>"
# {"token": "<token>"}
```

| Method and path | Description | Access |
| --------------- | ----------- | ------ |
| `GET /api/campuses/`, `/buildings/`, `/floors/`, `/spaces/`, `/edges/` | Spatial entities as GeoJSON (full CRUD for authenticated users) | Read: public. Write: authenticated |
| `GET /api/route/` | Route between two spaces | Public |
| `GET /api/plans/` | List uploaded plans and their state | Authenticated |
| `POST /api/plans/upload/` | Upload a plan and start processing | Authenticated |
| `GET /api/plans/<id>/status/` | Poll the state, proposal and AI metadata of a plan | Authenticated |
| `POST /api/plans/<id>/approve/` | Approve a plan in `REQUIRES_REVIEW` and create its spaces | Authenticated |
| `POST /api/plans/<id>/reject/` | Reject a plan in `REQUIRES_REVIEW` | Authenticated |

Compute a route (`preference` is `fastest` or `accessible`; `building_id` and `floor_id` are optional filters):

```bash
curl "http://localhost:8000/api/route/?start_space_id=1&target_space_id=2&preference=accessible"
```

The response is `200` with the path, `404` when the two spaces are not connected, and `400` when a space is not in the graph.

Upload a plan to a floor and follow its state:

```bash
curl -X POST http://localhost:8000/api/plans/upload/ \
  -H "Authorization: Token <token>" \
  -F "image=@test_img/test2.png" \
  -F "model_type=floor" \
  -F "target_id=1" \
  -F "ai_provider=mock"

curl -H "Authorization: Token <token>" http://localhost:8000/api/plans/1/status/
```

Requests are throttled to 100 per day for anonymous users and 1000 per day for authenticated users.

## Testing and continuous integration

```bash
docker compose exec web python manage.py test
```

During tests Celery runs tasks eagerly, so no worker is needed. The GitHub Actions pipeline (`.github/workflows/ci.yml`) runs on every push and pull request to `main` and has three jobs:

* **lint:** Flake8, limited to syntax errors and undefined names (`E9`, `F63`, `F7`, `F82`).
* **test:** starts PostGIS and Redis services, then runs `pip-audit`, `manage.py check`, a missing-migrations check and the test suite.
* **docker-validate:** validates `docker-compose.yml` and builds the backend image.

Dependabot checks Python and GitHub Actions dependencies weekly. The `main` branch is protected: changes arrive through short-lived `feature/*`, `bugfix/*` or `chore/*` branches validated by CI.

## Known limitations

These are known gaps in the current backend, listed so that results are not over-read.

1. The asynchronous pipeline calls the AI provider but stores a fixed placeholder proposal instead of the provider's output.
2. The extraction schema (`{x, y}` points, `space_type`) and the approval step (`[x, y]` lists, `type`) use different formats for the same proposal.
3. Approving a plan creates spaces but no navigation edges, so spaces created this way are not reachable by routes.
4. A plan uploaded to a `Campus` or `Building` cannot be approved: spaces require a `Floor`.
5. Plan coordinates are stored as WGS84 degrees without georeferencing, and edge weights are lengths in degrees, not metres.
6. The sample import marks every edge as accessible and nothing derives accessibility from the space type (stairs, lifts), so `accessible` and `fastest` routes do not differ on imported data.
7. A rejected or failed plan still occupies its target, so another plan cannot be uploaded for it.
8. Any authenticated user can approve, reject or edit data, CORS is open to all origins and `DEBUG` defaults to on. The configuration is meant for development.
9. `FastestPathStrategy` always reports `is_accessible: false`, even when the route is accessible.

`.env.example` lists `REDIS_URL` and `AI_PROVIDER_API_KEY`, but the Python code does not read them yet: the Celery broker URL is set in `backend/core/settings.py`.

## Roadmap

- [x] Reproducible Docker Compose stack, CI, licence and branch protection
- [x] Spatial model with GeoDjango and PostGIS
- [x] Asynchronous plan pipeline with a mock provider
- [x] Navigation graph, routing strategies and routing API
- [ ] Connect the pipeline to the graph (limitations 1 to 4)
- [ ] Georeferenced coordinates, distances in metres and derived accessibility (limitations 5, 6 and 9)
- [ ] Production-oriented permissions and settings (limitation 8)
- [ ] 2D map with Leaflet and route display
- [ ] Plan review panel
- [ ] 3D view with Three.js
- [ ] First real AI provider adapter
- [ ] Reproducible benchmark and evaluation

## Contributing

The project is in active development as a degree thesis. External contributions will be opened once the base architecture is stable.

## Citation

A `CITATION.cff` file will be added with the first stable release.

## Scientific publication

The medium-term goal is a SoftwareX article centred on:

* an AI-provider-agnostic architecture;
* a reproducible pipeline from 2D plans to navigable models;
* synchronised 2D and 3D representations;
* automatic generation of navigation graphs;
* a reproducible experimental evaluation;
* open publication of the software and experimental materials.

## License

Released under the Apache License 2.0. See [LICENSE](LICENSE).

## Contact

Contact details to be defined.
