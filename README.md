# Applicant Tracking System (ATS) Backend

## Overview

The Applicant Tracking System (ATS) Backend is a RESTful web application built using FastAPI and PostgreSQL. It provides a secure platform for recruiters to manage job postings and applications while enabling candidates to create professional profiles and apply for available positions.

The project follows a modular architecture with role-based authentication using JWT tokens and demonstrates modern backend development practices with FastAPI, SQLAlchemy, and PostgreSQL.

---

## Features

### Authentication
- User Registration
- User Login
- JWT Authentication
- Password Hashing with Passlib
- Role-Based Authorization (Recruiter & Candidate)

### Recruiter
- Create Job Postings
- View Posted Jobs
- Update Job Details
- Delete Job Postings
- View Applicants for Each Job
- Update Candidate Application Status

### Candidate
- Create Candidate Profile
- View Profile
- Update Profile
- Apply for Jobs
- View Submitted Applications

### Application Management
- Prevent Duplicate Applications
- Track Application Status
- Recruiter Access Control
- Candidate Access Control

---

## Technology Stack

| Category | Technology |
|----------|------------|
| Backend Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Data Validation | Pydantic |
| Authentication | JWT (JSON Web Tokens) |
| Password Hashing | Passlib (bcrypt) |
| API Testing | Swagger UI |
| ASGI Server | Uvicorn |

---

## Project Structure

```
app/
├── auth/
│   ├── hashing.py
│   ├── oauth2.py
│   └── token.py
│
├── models/
│   ├── application.py
│   ├── candidate.py
│   ├── job.py
│   └── user.py
│
├── routers/
│   ├── application.py
│   ├── auth.py
│   ├── candidate.py
│   └── job.py
│
├── schemas/
│   ├── application.py
│   ├── candidate.py
│   ├── job.py
│   └── user.py
│
├── database.py
└── main.py
```

---

## Database Design

### Users
Stores recruiter and candidate accounts.

### Jobs
Stores job postings created by recruiters.

### Candidates
Stores additional profile information for candidates.

### Applications
Stores job applications submitted by candidates.

---

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and obtain JWT token |

---

### Jobs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/jobs/` | Create a new job |
| GET | `/jobs/my` | View recruiter's jobs |
| GET | `/jobs/{job_id}` | Get job details |
| PUT | `/jobs/{job_id}` | Update job |
| DELETE | `/jobs/{job_id}` | Delete job |

---

### Candidate

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/candidate/profile` | Create candidate profile |
| GET | `/candidate/profile` | View profile |
| PUT | `/candidate/profile` | Update profile |

---

### Applications

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/applications/{job_id}` | Apply for a job |
| GET | `/applications/my` | View candidate applications |
| GET | `/applications/job/{job_id}/applicants` | View applicants for a job |
| PUT | `/applications/{application_id}/status` | Update application status |

---

## Authentication

Protected endpoints require a valid JWT access token.

Authorization Header:

```
Authorization: Bearer <access_token>
```

Role-based authorization ensures that:

- Recruiters can manage only their own jobs.
- Recruiters can update only applications for their own job postings.
- Candidates can manage only their own profiles.
- Candidates can apply only once for a job.

---

## Getting Started

### Clone the Repository

```bash
git clone https://github.com/agilan-0110/applicant-tracking-system-backend.git

cd applicant-tracking-system-backend
```

---

### Create a Virtual Environment

```bash
python -m venv venv
```

Activate the virtual environment.

Windows

```bash
venv\Scripts\activate
```

Linux/macOS

```bash
source venv/bin/activate
```

---

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Configure PostgreSQL

Create a PostgreSQL database and update your database connection string inside your configuration.

Example:

```
postgresql://username:password@localhost:5432/ats_db
```

---

### Run the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```
http://127.0.0.1:8000
```

Interactive API Documentation:

```
http://127.0.0.1:8000/docs
```

Alternative ReDoc Documentation:

```
http://127.0.0.1:8000/redoc
```

---

## Security Features

- JWT Authentication
- Password Hashing
- Protected Endpoints
- Role-Based Authorization
- Duplicate Application Prevention
- Ownership Validation for Recruiters

---

## Future Enhancements

- Resume Upload
- Resume Parsing
- AI-Based Candidate Ranking
- Job Search and Filtering
- Email Notifications
- Pagination
- Docker Support
- Alembic Database Migrations
- Unit and Integration Testing
- Cloud Deployment

---

## Author

**Agilan T**

Artificial Intelligence and Data Science Student

- GitHub: https://github.com/agilan-0110
- LinkedIn: https://www.linkedin.com/in/agilanthiyagarajan
