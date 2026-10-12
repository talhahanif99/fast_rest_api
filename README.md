# FastAPI REST API Backend with JWT Auth, CRUD & Database

A production-style Task Management REST API built with FastAPI. The project demonstrates secure JWT authentication, SQLAlchemy ORM integration, user-scoped CRUD operations, Pydantic validation, automatic API documentation, and an import-ready Postman collection.

## Project Overview

This backend is designed as a clean portfolio project for GitHub and Upwork. Users can register, authenticate, view their own profile, and manage only the tasks they own. SQLite is used by default for zero-setup local development, while the database configuration is environment-driven so PostgreSQL can be introduced without restructuring the application.

## Features

- User registration with duplicate-email protection
- Secure password hashing using Argon2id via `argon2-cffi`
- JWT bearer authentication with expiration
- Swagger-compatible OAuth2 password flow
- Current-user profile endpoint
- Full task CRUD: create, list, retrieve, replace, patch, delete
- Task ownership enforcement for every protected task operation
- Pagination and completion filtering
- SQLAlchemy 2.x ORM models and relationships
- Pydantic 2.x request/response validation
- Automatic SQLite database/table creation on startup
- Swagger UI at `/docs` and ReDoc at `/redoc`
- Postman collection with automatic token and task ID capture
- Environment-based configuration

## Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy 2.x
- SQLite by default
- Pydantic 2.x / pydantic-settings
- PyJWT
- argon2-cffi (Argon2id)
- Uvicorn

## Project Structure

```text
fastapi-rest-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── security.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── task.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── auth.py
│   │   └── task.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── tasks.py
│   └── dependencies/
│       ├── __init__.py
│       └── auth.py
├── postman/
│   └── FastAPI_REST_API.postman_collection.json
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── run.py
```

## Installation

Clone the repository and enter the project directory:

```bash
git clone <your-repository-url>
cd fastapi-rest-api
```

Create a virtual environment:

```bash
python -m venv venv
```

### Windows

```powershell
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Environment Setup

Copy `.env.example` to `.env`.

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

### Windows Command Prompt

```cmd
copy .env.example .env
```

### macOS / Linux

```bash
cp .env.example .env
```

Before production use, replace `SECRET_KEY` with a strong random value. One option is:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Default configuration:

```env
SECRET_KEY=replace-with-a-random-secret-key-at-least-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./app.db
```

## Running the Server

Start the development server:

```bash
uvicorn app.main:app --reload
```

Alternatively:

```bash
python run.py
```

Server: `http://127.0.0.1:8000`

## API Documentation

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

Swagger's **Authorize** button supports the OAuth2 password flow. Enter your registered email in the `username` field and your account password in the `password` field. The API uses the email as the login identifier.

## Authentication Flow

1. Register with `POST /api/v1/auth/register`.
2. Login with `POST /api/v1/auth/login` using email and password.
3. Receive a JWT access token.
4. Send the token on protected requests:

```http
Authorization: Bearer <access_token>
```

5. Protected endpoints return `401 Unauthorized` when credentials are missing, expired, or invalid.

## API Endpoints

| Method | Endpoint | Auth | Purpose |
|---|---|---:|---|
| GET | `/` | No | API metadata |
| GET | `/health` | No | Health check |
| POST | `/api/v1/auth/register` | No | Register user |
| POST | `/api/v1/auth/login` | No | Login and receive JWT |
| GET | `/api/v1/auth/me` | Yes | Current user profile |
| POST | `/api/v1/tasks` | Yes | Create task |
| GET | `/api/v1/tasks` | Yes | List own tasks |
| GET | `/api/v1/tasks/{task_id}` | Yes | Get own task |
| PUT | `/api/v1/tasks/{task_id}` | Yes | Fully update own task |
| PATCH | `/api/v1/tasks/{task_id}` | Yes | Partially update own task |
| DELETE | `/api/v1/tasks/{task_id}` | Yes | Delete own task |

Task listing supports:

```text
/api/v1/tasks?skip=0&limit=10&completed=false
```

## Example Requests

### Register

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com","password":"SecurePassword123"}'
```

### Login

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"SecurePassword123"}'
```

### Create Task

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/tasks" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Build FastAPI portfolio","description":"Complete the backend API project","completed":false}'
```

### Patch Task

```bash
curl -X PATCH "http://127.0.0.1:8000/api/v1/tasks/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"completed":true}'
```

## Postman Collection

Import:

```text
postman/FastAPI_REST_API.postman_collection.json
```

The collection includes all required requests. Its default collection variable is:

```text
base_url = http://127.0.0.1:8000
```

The Login request automatically stores the returned JWT as `access_token`. Authenticated requests use `Bearer {{access_token}}`. The Create Task request automatically stores the created task ID as `task_id` for subsequent requests.

## Database

SQLite is the default:

```env
DATABASE_URL=sqlite:///./app.db
```

The application creates the SQLite database and required tables automatically at startup.

To move to PostgreSQL, install a PostgreSQL driver such as `psycopg[binary]` and change only `DATABASE_URL`, for example:

```env
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/task_api
```

No application modules contain hardcoded database connection strings.

## Security Features

- Plain-text passwords are never stored
- Passwords are hashed with Argon2
- JWTs are signed with an environment-provided secret
- JWT access tokens expire automatically
- Protected routes require Bearer authentication
- Inactive accounts are rejected
- Users can access only tasks whose `owner_id` matches their authenticated identity
- Duplicate emails return `409 Conflict`
- Missing/invalid credentials return `401 Unauthorized`
- Request validation is handled by Pydantic/FastAPI
- `.env` and local database files are excluded from Git

## Future Improvements

- Alembic migrations for production database evolution
- PostgreSQL deployment profile
- Refresh tokens and token revocation
- Email verification and password reset flow
- Role-based access control
- Automated pytest integration tests
- Docker and Docker Compose support
- Rate limiting and structured application logging
- CI/CD workflow for linting, testing, and deployment
