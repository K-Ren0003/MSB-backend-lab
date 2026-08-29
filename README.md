# MSB Backend Lab

An educational sports-platform backend built to develop practical experience
with APIs, databases, containers, Kubernetes, observability, event-driven
architecture, and microservices.

The application supports teams, sporting events, users, and tips/predictions.
It does not implement real-money gambling, payments, or odds.

## Current Progress

### Day 1 — Python, FastAPI, and REST: complete

- FastAPI application and Swagger/OpenAPI documentation
- Health, team, event, user, and tip endpoints
- Pydantic request validation
- Appropriate success, not-found, and validation status codes
- Automated API tests

### Day 2 — PostgreSQL, SQL, and MongoDB: complete

- PostgreSQL as the transactional datastore
- SQLAlchemy models, foreign keys, and ORM relationships
- Request-scoped database sessions
- Repeatable table-initialization command
- MongoDB `activity_events` collection for audit-style documents
- A `tip.created` MongoDB document after a tip is persisted
- Activity-event retrieval for debugging and demonstration
- Environment-based database configuration
- Isolated tests that do not use the development databases
- Manual SQL and JOIN exercises

### Day 3 — Docker and Docker Compose: complete

- API packaged in a Python 3.14 Docker image
- Docker build context kept small with `.dockerignore`
- Compose stack for API, PostgreSQL, MongoDB, and one-off database setup
- Service-name networking through `postgres` and `mongo`
- Named volumes for PostgreSQL and MongoDB persistence
- Health checks for API, PostgreSQL, and MongoDB
- Verified PostgreSQL persistence after PostgreSQL container recreation
- Diagnosed an invalid database hostname and incorrect API port mapping

### Day 4 — Kubernetes/K3s and Traefik: complete

- API image imported into the single-node K3s container runtime
- Three FastAPI replicas managed by a Kubernetes Deployment
- ClusterIP Service selecting API Pods through `app: msb-api` labels
- Traefik Ingress routing `msb.k3s.test` to the API Service
- PostgreSQL and MongoDB StatefulSets with persistent volumes
- ConfigMap for non-sensitive runtime configuration and Kubernetes Secret for credentials
- One-off Job to initialise PostgreSQL tables before application use
- Verified an end-to-end tip request, including PostgreSQL persistence and a MongoDB `tip.created` event
- Diagnosed and restored invalid images, Service selectors, target ports, and Ingress backends

## Current Architecture

```text
Client
  |
  | HTTP / REST, Host: msb.k3s.test
  v
Traefik LoadBalancer / Ingress
  |
  v
msb-api ClusterIP Service
  |--------------------------|--------------------------|
  v                          v                          v
FastAPI Pod 1              FastAPI Pod 2              FastAPI Pod 3
  |--------------------------|
  v                          v
PostgreSQL StatefulSet     MongoDB StatefulSet
teams, users, events, tips activity_events
```

PostgreSQL stores structured transactional records whose relationships need
foreign-key integrity. MongoDB stores flexible activity/audit documents rather
than duplicating the relational data.

## Technology Stack

- Python 3.14
- FastAPI and Uvicorn
- Pydantic
- PostgreSQL
- SQLAlchemy and Psycopg
- MongoDB and PyMongo
- Pytest, HTTPX, and SQLite for isolated tests
- Docker and Docker Compose
- Kubernetes/K3s
- Traefik
- Git

## Project Structure

```text
MSB-backend-lab/
├── api/
│   ├── app/
│   │   ├── db.py          # PostgreSQL engine and request sessions
│   │   ├── init_db.py     # Repeatable table creation
│   │   ├── main.py        # FastAPI schemas and routes
│   │   ├── models.py      # SQLAlchemy models and relationships
│   │   └── mongo.py       # MongoDB configuration and collection
│   └── tests/
│       ├── conftest.py    # Isolated database and Mongo test fixtures
│       └── test_api.py
├── sql/
│   └── day2_queries.sql   # Manual SQL and JOIN practice
├── .env.example
├── .dockerignore
├── compose.yaml
├── Dockerfile
├── k8s/
│   ├── api-configmap.yaml
│   ├── api-deployment.yaml
│   ├── api-ingress.yaml
│   ├── api-service.yaml
│   ├── init-db-job.yaml
│   ├── mongo.yaml
│   ├── msb-runtime-secret.example.yaml
│   ├── namespace.yaml
│   └── postgres.yaml
├── requirements.txt
└── README.md
```

## Local Setup

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 2. Start PostgreSQL and MongoDB

Both services must be reachable locally. Create the PostgreSQL database if it
does not already exist:

```bash
createdb msb_backend_lab
```

The MongoDB collection is created automatically when the first activity
document is inserted.

### 3. Configure environment variables

The defaults in `.env.example` match the original local development setup.
Copy and adjust them for your machine:

```bash
cp .env.example .env
set -a
source .env
set +a
```

Configuration values:

- `DATABASE_URL`: SQLAlchemy PostgreSQL connection URL
- `MONGO_URL`: MongoDB server URL
- `MONGO_DATABASE`: MongoDB database name

The `.env` file is intentionally not committed. Do not put real credentials in
Git.

### 4. Create the PostgreSQL tables

```bash
python -m api.app.init_db
```

This uses the SQLAlchemy model metadata to create missing tables. It does not
delete or replace existing tables or data. A migration tool such as Alembic can
be introduced when the schema begins changing frequently.

### 5. Start the API

```bash
uvicorn api.app.main:app --reload
```

Open:

- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Docker Compose (Ubuntu)

Day 3 runs the full local stack on the Ubuntu development host. Docker Engine
and the Docker Compose plugin must be installed there before running these
commands.

Start the full stack:

```bash
docker compose up --build -d
docker compose ps
curl -i http://localhost:8000/health
```

The stack starts four services:

- `postgres`: transactional PostgreSQL database
- `mongo`: activity/audit document database
- `init-db`: one-off PostgreSQL table-initialization container
- `api`: FastAPI application exposed on Ubuntu port 8000

Compose gives services a shared private network. The API uses `postgres` and
`mongo` as hostnames rather than `localhost`, because `localhost` inside a
container means that container itself.

The API image is built from `Dockerfile`. It uses a Python base image, installs
the dependencies before copying source code to make use of Docker's build
cache, and starts Uvicorn on `0.0.0.0:8000`. `.dockerignore` excludes local
virtual environments, Git metadata, caches, and `.env` files from the build
context.

### Data persistence

PostgreSQL data is stored in the named `postgres_data` volume. Recreating the
PostgreSQL container without deleting that volume preserved the teams and tip
created through the API. MongoDB data is stored separately in `mongo_data`.

Do not run `docker compose down -v` unless you intentionally want to remove
both named volumes and all containerized database data.

### Troubleshooting completed

- Using `wrong-postgres` as the database hostname produced a DNS-resolution
  error, confirming that Compose service names are part of container networking.
- Mapping host port `8001` to unused container port `9999` produced a
  connection reset. Uvicorn listens on container port `8000`, so the correct
  mapping is `8000:8000`.

## Kubernetes/K3s Deployment (Ubuntu)

Day 4 runs a separate K3s environment on the Ubuntu server. The existing
Docker Compose stack is left intact for Docker development; it has separate
database data from the K3s StatefulSets.

### 1. Build and import the API image

K3s uses containerd rather than Docker's local image store, so the locally
built API image must be imported before a Pod can run it:

```bash
docker build -t msb-api:day4 .
docker save msb-api:day4 | sudo k3s ctr images import -
sudo k3s ctr images ls | grep msb-api
```

The API Deployment uses `imagePullPolicy: Never` so K3s uses that imported
image rather than attempting to pull it from a registry.

### 2. Create the namespace and runtime credentials

Real credentials are deliberately not committed. On the Ubuntu server, create
an ignored `.k8s-runtime.env` file using
`k8s/msb-runtime-secret.example.yaml` as the shape, then create the Secret:

```bash
sudo k3s kubectl apply -f k8s/namespace.yaml
sudo k3s kubectl create secret generic msb-runtime -n msb \
  --from-env-file=.k8s-runtime.env
```

The file contains PostgreSQL and MongoDB credentials plus the API connection
URLs. Use URL-safe passwords and keep this file local to the server.

### 3. Deploy databases, initialise tables, and deploy the API

```bash
sudo k3s kubectl apply -f k8s/api-configmap.yaml
sudo k3s kubectl apply -f k8s/postgres.yaml
sudo k3s kubectl apply -f k8s/mongo.yaml

sudo k3s kubectl rollout status statefulset/postgres -n msb
sudo k3s kubectl rollout status statefulset/mongo -n msb

sudo k3s kubectl apply -f k8s/init-db-job.yaml
sudo k3s kubectl wait --for=condition=complete job/init-db -n msb

sudo k3s kubectl apply -f k8s/api-deployment.yaml
sudo k3s kubectl apply -f k8s/api-service.yaml
sudo k3s kubectl apply -f k8s/api-ingress.yaml
sudo k3s kubectl rollout status deployment/msb-api -n msb
```

The `init-db` Job creates missing PostgreSQL tables once. PostgreSQL and
MongoDB each use a `ReadWriteOnce` persistent volume claim, so their K3s data
survives a Pod replacement.

### 4. Verify routing

Traefik is exposed by K3s at the Ubuntu server's LAN address. A host-header
request proves the whole route without requiring local DNS setup:

```bash
sudo k3s kubectl get pods -n msb
sudo k3s kubectl get endpointslice -n msb \
  -l kubernetes.io/service-name=msb-api
curl -i -H 'Host: msb.k3s.test' http://192.168.4.26/health
```

Expected response:

```json
{"status":"ok"}
```

### Kubernetes troubleshooting completed

- An invalid locally unavailable image produced `ErrImageNeverPull`.
- A wrong Service selector left the Service with no endpoints and Traefik
  returned HTTP `503`.
- A wrong Service `targetPort` left endpoints present but forwarded to no
  listening application port, producing HTTP `502`.
- A broken Ingress backend Service reference produced HTTP `404`.
- Job logs identified a PostgreSQL password mismatch; correcting the Secret's
  `DATABASE_URL` allowed the table-initialisation Job to succeed.

## API Endpoints

```text
GET  /health

GET  /teams
GET  /teams/{team_id}
POST /teams

GET  /events
GET  /events/{event_id}
POST /events
PUT  /events/{event_id}

GET  /users
GET  /users/{user_id}
POST /users

GET  /tips/{tip_id}
GET  /users/{user_id}/tips
POST /tips

GET  /activity-events
```

Creating a tip performs two storage operations:

1. The tip is committed to PostgreSQL.
2. A `tip.created` activity document is written to MongoDB.

Example MongoDB document:

```json
{
  "event_type": "tip.created",
  "user_id": 1,
  "tip_id": 1,
  "event_id": 1,
  "metadata": {
    "source": "api"
  },
  "created_at": "2026-08-29T00:00:00Z"
}
```

## Testing

Run the suite from the repository root:

```bash
python -m pytest -v
```

Tests use an isolated in-memory SQLite database and a fake activity collection.
Every test starts with empty tables, creates its own prerequisites, and leaves
the local PostgreSQL and MongoDB databases unchanged.

Current coverage includes:

- Health response
- Event creation and retrieval through separate database sessions
- Missing-resource handling
- Pydantic status validation
- Relational tip creation
- MongoDB activity-document creation and retrieval
- Query-parameter validation

Current result: **6 passed**.

## Manual SQL Practice

The Day 2 queries include filters, joins, aggregation, and a rolled-back write
transaction:

```bash
psql msb_backend_lab -f sql/day2_queries.sql
```

The final `UPDATE` and `DELETE` are wrapped in a transaction followed by
`ROLLBACK`, allowing write practice without retaining those changes.

## Day 2 Troubleshooting Exercise

To observe a dependency failure without editing saved configuration, run the
initializer once with an intentionally invalid hostname:

```bash
DATABASE_URL='postgresql+psycopg://kaden@wrong-host/msb_backend_lab?connect_timeout=3' \
python -m api.app.init_db
```

Inspect the hostname and connection error, then run the normal initializer
again. This demonstrates that the API depends on correct runtime configuration.

## Day 2 Learning Checkpoint

Before moving on, be able to explain:

- A primary key identifies a row; a foreign key connects rows across tables.
- A transaction groups database changes into one commit or rollback boundary.
- An ORM maps Python objects to relational tables but does not remove the need
  to understand SQL.
- A JOIN combines related rows; the included practice query joins tips, users,
  events, and teams.
- PostgreSQL is appropriate for the core data because integrity and structured
  relationships matter.
- MongoDB is appropriate for the activity records because documents can carry
  flexible event metadata and are mainly retrieved for auditing/debugging.
- Persistence means data remains after an API process restarts because it lives
  in an external database rather than a Python list.

## Next Stage

Day 5 adds Loki and Grafana for centralised logging and observability.

This project represents hands-on educational experience, not commercial or
production experience.
