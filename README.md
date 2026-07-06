# Applicant Tracking System (ATS) Backend

## Overview

This project is a FastAPI backend for an Applicant Tracking System. It supports two roles:

- Recruiters can create and manage jobs, view applicants, and update application status.
- Candidates can create a profile, apply for jobs, and view their submitted applications.

The API uses PostgreSQL, SQLAlchemy, Alembic migrations, JWT authentication, and role-based access control.

## Features

- User registration and login
- JWT authentication
- Password hashing with Passlib bcrypt
- Candidate profile CRUD
- Recruiter job CRUD
- Job applications with duplicate prevention
- Applicant listing for job owners
- Application status updates
- Docker and Docker Compose support
- Pytest test coverage for auth, candidates, jobs, applications, and root endpoint

## Tech Stack

| Area | Technology |
| --- | --- |
| API | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Validation | Pydantic |
| Auth | JWT with python-jose |
| Passwords | Passlib bcrypt |
| Tests | Pytest, FastAPI TestClient |
| Runtime | Uvicorn/Gunicorn |

## Project Structure

```text
app/
|-- auth/
|   |-- __init__.py
|   |-- hashing.py
|   |-- oauth2.py
|   `-- token.py
|-- models/
|   |-- __init__.py
|   |-- application.py
|   |-- candidate.py
|   |-- job.py
|   `-- user.py
|-- routers/
|   |-- __init__.py
|   |-- application.py
|   |-- auth.py
|   |-- candidate.py
|   `-- job.py
|-- schemas/
|   |-- __init__.py
|   |-- application.py
|   |-- candidate.py
|   |-- job.py
|   `-- user.py
|-- __init__.py
|-- config.py
|-- database.py
`-- main.py

alembic/
|-- versions/
|-- env.py
`-- script.py.mako

tests/
|-- conftest.py
|-- test_applications.py
|-- test_auth.py
|-- test_crud_candidate.py
|-- test_jobs.py
`-- test_root.py
```



## Local Setup

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run migrations:

```powershell
alembic upgrade head
```

Start the API:

```powershell
uvicorn app.main:app --reload
```

The API runs at:

```text
http://127.0.0.1:8000
```

Interactive docs:

```text
http://127.0.0.1:8000/docs
```

## Docker Setup

Start the API and PostgreSQL:

```powershell
docker compose up --build
```

The API container waits for PostgreSQL health checks before starting.

## Running Tests

Use the project virtual environment:

```powershell
.\venv\Scripts\python.exe -m pytest -q
```

Current suite coverage includes:

- Authentication
- Candidate profiles
- Job management
- Applications
- Root health endpoint

## API Endpoints

### Auth

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/auth/register` | Register a candidate or recruiter |
| POST | `/auth/login` | Login and receive a JWT |

### Candidate

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/candidate/profile` | Create candidate profile |
| GET | `/candidate/profile` | View own profile |
| PUT | `/candidate/profile` | Update own profile |

### Jobs

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/jobs/` | Recruiter creates a job |
| GET | `/jobs/my` | Recruiter views own jobs |
| GET | `/jobs/{job_id}` | View a job |
| PUT | `/jobs/{job_id}` | Recruiter updates own job |
| DELETE | `/jobs/{job_id}` | Recruiter deletes own job |

### Applications

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/applications/{job_id}` | Candidate applies to a job |
| GET | `/applications/my` | Candidate views own applications |
| GET | `/applications/job/{job_id}/applicants` | Recruiter views applicants for own job |
| PUT | `/applications/{application_id}/status` | Recruiter updates application status |

## Authentication

Protected endpoints require:

```text
Authorization: Bearer <access_token>
```

Role rules:

- Only candidates can create and update candidate profiles.
- Only candidates can apply for jobs.
- Only recruiters can create, update, and delete jobs.
- Recruiters can manage only their own jobs and applicants.

## Application Status Values

Applications use these status values:

- `Applied`
- `Shortlisted`
- `Interview`
- `Rejected`
- `Hired`

## Future Enhancements

- Resume upload
- Resume parsing
- Candidate ranking
- Job search and filtering
- Email notifications
- Pagination
- Cloud deployment
