# Team Task Manager

Full-stack assignment project built for the **Ethara company task**.
This app lets teams create projects, manage members, assign tasks, and track progress with role-based access (Admin/Member).

## Assignment Context
This repository is a submission for:
- **Assignment:** Team Task Manager (Full-Stack)
- **Company:** Ethara
- **Timeline target:** 1–2 days (8–12 hours)

## Features
- Authentication: Signup, Login, Logout, current user (`/auth/me`)
- Project management: create, list, update, delete projects
- Team management: add/remove members, update member roles
- Task management: create, assign, update, delete tasks
- Status tracking: `todo -> in_progress -> done`
- Dashboard: total tasks, overdue tasks, and status breakdown
- RBAC:
  - Admin: full project/task/member management
  - Member: view project data, create tasks, update status on assigned tasks

## Tech Stack
- Frontend: Next.js (App Router) + Tailwind CSS
- Backend: FastAPI + SQLModel
- Database: PostgreSQL
- Auth: JWT access/refresh tokens via httpOnly cookies
- Deployment: Railway (required by assignment)

## Repository Structure
- `frontend/` Next.js app
- `backend/` FastAPI app
- `docker-compose.yml` local Postgres setup

## Local Setup

### 1) Start PostgreSQL (Docker)
```bash
docker compose up -d
```

### 2) Run backend
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3) Run frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### 4) Open app
- Frontend: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`

## Environment Variables

### Backend (`backend/.env`)
| Variable | Example | Purpose |
|---|---|---|
| `APP_NAME` | `Team Task Manager API` | API display name |
| `ENVIRONMENT` | `development` | Runtime environment |
| `DATABASE_URL` | `postgresql+psycopg://postgres:postgres@localhost:5432/ethara` | DB connection |
| `FRONTEND_URL` | `http://localhost:3000` | CORS allowlist |
| `JWT_SECRET_KEY` | `change-me-access-secret` | Access token signing |
| `JWT_REFRESH_SECRET_KEY` | `change-me-refresh-secret` | Refresh token signing |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token TTL |
| `COOKIE_DOMAIN` | `localhost` or `.yourdomain.com` | Cookie scope |
| `COOKIE_SECURE` | `false` (dev), `true` (prod) | Secure cookie flag |

### Frontend (`frontend/.env`)
| Variable | Example | Purpose |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | API base URL |

## API Summary
- Auth: `POST /auth/signup`, `POST /auth/login`, `POST /auth/logout`, `GET /auth/me`, `POST /auth/refresh`
- Projects: CRUD on `/projects`, member management on `/projects/{id}/members`
- Tasks: CRUD on `/projects/{id}/tasks`, status update on `PATCH /tasks/{id}/status`
- Dashboard: `GET /dashboard`

## Validation & Relationships
- SQL relationships enforced via foreign keys between `User`, `Project`, `ProjectMember`, and `Task`
- Input validation via Pydantic schemas
- Role checks enforced in backend dependencies for project/task/member endpoints

## Testing
```bash
cd backend
source venv/bin/activate
pytest -q
```

## Deployment (Railway)
1. Create Railway project
2. Add PostgreSQL service
3. Add backend service from this repo with root directory `backend`
4. Start command:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
5. Set backend env vars (`DATABASE_URL`, `JWT_*`, `FRONTEND_URL`, cookie settings)
6. Deploy frontend service (Railway) with root directory `frontend` and `NEXT_PUBLIC_API_URL`
   
