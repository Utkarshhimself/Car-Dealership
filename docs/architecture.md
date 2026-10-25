# Architecture

The system consists of a React frontend, a FastAPI REST API, and PostgreSQL. Docker Compose coordinates local development.

## Responsibilities

- **Frontend:** user-facing inventory, authentication, vehicle detail, and admin management routes.
- **Backend:** authentication, role authorization, vehicle CRUD, purchases, restocking, and transactional validation.
- **Database:** PostgreSQL is the source of truth; schema changes are versioned through Alembic migrations.
