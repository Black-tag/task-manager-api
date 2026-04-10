# Task Manager API

Flask + PostgreSQL API for:
- authentication (JWT),
- project management,
- task management with pagination and filtering.

## Prerequisites

- Python 3.11+
- Docker + Docker Compose
- `curl`
- `jq` (optional, but used in examples to extract IDs/tokens)

## 1) Quick Start (API + Postgres in Docker)

```bash
cp .env.example .env
docker compose up --build -d
```

API: `http://127.0.0.1:5000`  
Postgres: `localhost:5432` (`postgres/postgres`, DB `postgres`)

## 2) Local Python setup (optional, without Docker API)

Copy the example env file:

```bash
cp .env.example .env
```

Default values already work with local Postgres and Docker Postgres.

## 3) Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 4) Run the API

```bash
python3 app.py
```

The app runs at `http://127.0.0.1:5000`.

---

## API Test Commands (curl)

### Register

```bash
curl -i -X POST http://127.0.0.1:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","email":"alice@example.com","password":"secret123"}'
```

### Login and capture access token

```bash
ACCESS_TOKEN=$(curl -s -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"secret123"}' | jq -r '.access_token')

echo "$ACCESS_TOKEN"
```

### Create project and capture project ID

```bash
PROJECT_ID=$(curl -s -X POST http://127.0.0.1:5000/projects \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Task Test Project","description":"for task endpoint testing"}' | jq -r '.id')

echo "$PROJECT_ID"
```

### Create tasks

```bash
curl -i -X POST "http://127.0.0.1:5000/projects/$PROJECT_ID/tasks" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Write API docs","description":"Draft docs","status":"todo","due_date":"2026-05-10"}'

curl -i -X POST "http://127.0.0.1:5000/projects/$PROJECT_ID/tasks" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Implement pagination","status":"in_progress","due_date":"2026-04-20"}'

curl -i -X POST "http://127.0.0.1:5000/projects/$PROJECT_ID/tasks" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Finalize tests","status":"done","due_date":"2026-04-15"}'
```

### List tasks (base)

```bash
curl -i -X GET "http://127.0.0.1:5000/projects/$PROJECT_ID/tasks" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Pagination examples

```bash
# page + limit
curl -i -X GET "http://127.0.0.1:5000/projects/$PROJECT_ID/tasks?page=1&limit=2" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# offset + limit
curl -i -X GET "http://127.0.0.1:5000/projects/$PROJECT_ID/tasks?offset=1&limit=2" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Filtering examples

```bash
# by status
curl -i -X GET "http://127.0.0.1:5000/projects/$PROJECT_ID/tasks?status=todo" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# by due date
curl -i -X GET "http://127.0.0.1:5000/projects/$PROJECT_ID/tasks?due_before=2026-04-30" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# title search
curl -i -X GET "http://127.0.0.1:5000/projects/$PROJECT_ID/tasks?searchText=pagination" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# combined
curl -i -X GET "http://127.0.0.1:5000/projects/$PROJECT_ID/tasks?status=done&due_before=2026-05-30&searchText=Implement&page=1&limit=5" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Task by ID endpoints

```bash
TASK_ID=$(curl -s -X GET "http://127.0.0.1:5000/projects/$PROJECT_ID/tasks" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq -r '.items[0].id')

echo "$TASK_ID"
```

```bash
# GET /tasks/{task_id}
curl -i -X GET "http://127.0.0.1:5000/tasks/$TASK_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# PUT /tasks/{task_id}
curl -i -X PUT "http://127.0.0.1:5000/tasks/$TASK_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Implement pagination + filtering","status":"done","description":"completed"}'

# DELETE /tasks/{task_id}
curl -i -X DELETE "http://127.0.0.1:5000/tasks/$TASK_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

---

## Stop services

```bash
docker compose down
```

To remove DB volume too:

```bash
docker compose down -v
```
