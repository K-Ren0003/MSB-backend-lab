# MSB Backend Lab

A practical backend engineering learning project built to develop hands-on experience with modern backend development, APIs, databases, containers, Kubernetes, observability, event-driven architecture, and microservices.

The application is a small sports platform API supporting teams, sporting events, users, and tips/predictions.

## Current Progress

### Day 1 — Python, FastAPI and REST

The first stage of the project implements a REST API using Python and FastAPI.

Current functionality includes:

- Health check endpoint
- Create and retrieve teams
- Create and retrieve sporting events
- Update sporting events
- Create and retrieve users
- Create and retrieve tips
- Retrieve tips belonging to a specific user
- Pydantic request validation
- HTTP status codes
- 404 error handling
- Automatic Swagger/OpenAPI documentation
- Automated API testing with pytest

Data is currently stored in memory. Persistent storage using PostgreSQL and MongoDB will be introduced later in the project.

## Tech Stack

Current:

- Python
- FastAPI
- Pydantic
- Uvicorn
- Pytest
- HTTPX / FastAPI TestClient
- Git

Planned later in the project:

- PostgreSQL
- MongoDB
- Docker
- Docker Compose
- Kubernetes / K3s
- Traefik
- Grafana
- Loki
- Apache Kafka
- Go
- gRPC
- Protocol Buffers
- React

## Project Structure

```text
MSB-backend-lab/
├── api/
│   ├── __init__.py
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py
│   └── tests/
│       └── test_healthy.py
├── .gitignore
├── README.md
└── .venv/
```

The project structure will expand as databases, containers, Kubernetes resources, messaging, observability, and additional services are introduced.

## Running Locally

### 1. Activate the virtual environment

From the project root:

```bash
source .venv/bin/activate
```

### 2. Start the API

```bash
uvicorn api.app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

## Swagger API Documentation

FastAPI automatically generates interactive API documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

Swagger can be used to inspect endpoints, submit requests, and inspect response bodies and HTTP status codes.

## API Endpoints

### Health

```text
GET /health
```

Returns the health status of the API.

Example response:

```json
{
  "status": "ok"
}
```

### Teams

```text
GET  /teams
GET  /teams/{team_id}
POST /teams
```

Example team creation request:

```json
{
  "name": "North Queensland Cowboys",
  "code": "NQL"
}
```

### Events

```text
GET  /events
GET  /events/{event_id}
POST /events
PUT  /events/{event_id}
```

Example event:

```json
{
  "home_team_id": 1,
  "away_team_id": 2,
  "starts_at": "2026-08-30T18:00:00",
  "status": "scheduled"
}
```

Events currently support statuses such as:

```text
scheduled
live
completed
cancelled
```

### Users

```text
POST /users
GET  /users/{user_id}
```

Example user:

```json
{
  "display_name": "Kaden",
  "email": "kaden@example.com"
}
```

### Tips

```text
POST /tips
GET  /tips/{tip_id}
GET  /users/{user_id}/tips
```

Example tip:

```json
{
  "user_id": 1,
  "event_id": 1,
  "predicted_winner_team_id": 1
}
```

## Validation and Error Handling

Incoming request bodies are validated using Pydantic models.

For example, if a required field is missing from a request, FastAPI rejects the request with a validation error.

Example:

```text
422 Unprocessable Content
```

Requests for resources that do not exist return:

```text
404 Not Found
```

For example:

```json
{
  "detail": "Event not found"
}
```

## HTTP Status Codes Used

The API currently demonstrates:

- `200 OK` — successful request
- `201 Created` — resource successfully created
- `404 Not Found` — requested resource does not exist
- `422 Unprocessable Content` — request failed validation
- `500 Internal Server Error` — unexpected backend application failure

## Testing

Automated API tests are written using pytest and FastAPI's test client.

Run the test suite from the project root:

```bash
python -m pytest -v
```

Current tests cover:

- Health endpoint
- Event creation
- Event retrieval
- Invalid event retrieval
- Tip creation

Current Day 1 test result:

```text
5 passed
```

## Day 1 Learning Outcomes

Day 1 introduced practical experience with:

- REST APIs
- HTTP requests and responses
- GET, POST and PUT methods
- API endpoints
- Path parameters
- JSON request and response bodies
- HTTP status codes
- FastAPI
- Pydantic models
- Request validation
- Error handling
- Swagger/OpenAPI
- Basic automated API testing
- Debugging Python backend errors

## Current Data Storage

The application currently stores data in Python lists while the initial API behaviour is being developed.

This means data is lost whenever the application process restarts.

Persistent storage will be introduced using PostgreSQL and MongoDB in the next stage of the project.

## Future Development

Planned stages of the project include:

1. PostgreSQL and MongoDB persistence
2. Docker and Docker Compose
3. Kubernetes/K3s deployment
4. Traefik Ingress and replicated API Pods
5. Centralised logging using Loki and Grafana
6. Kafka event-driven communication
7. Go worker service
8. gRPC and Protocol Buffers
9. Small React frontend exposure
10. Final architecture, troubleshooting, and interview documentation

## Project Goal

The goal of this project is not to represent commercial experience.

It is designed to provide genuine hands-on project experience with backend engineering technologies and to develop the ability to explain how the components work, communicate, fail, and are troubleshot.