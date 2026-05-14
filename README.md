# Multi-Tenant SaaS Backend

A backend for managing projects and tasks across multiple companies. Each company's data is completely separate from others — that's the multi-tenant part.

**Live Demo:** http://15.134.38.227:8000/docs

---

## How it works

There are 3 roles — super_admin, admin, and user.

- **super_admin** creates companies and assigns admins to them
- **admin** creates users in their company, creates projects, creates tasks and assigns them to users
- **user** can only update the status of tasks assigned to them (todo → in_progress → done)

No one can see or touch data from another company.

---

## Tech used

Python, FastAPI, PostgreSQL (Supabase), JWT auth, Docker, AWS EC2

---

## Endpoints

**Auth**
- `POST /auth/login`
- `POST /auth/register`

**Companies** — super admin only
- `POST /companies/`
- `GET /companies/get_all_company`
- `DELETE /companies/{company_id}`

**Users**
- `POST /users/`
- `GET /users/`
- `PATCH /users/{user_id}`
- `DELETE /users/{user_id}`

**Projects** — admin only
- `POST /projects/`
- `GET /projects/`
- `PATCH /projects/{project_id}`
- `DELETE /projects/{project_id}`

**Tasks**
- `POST /tasks/`
- `GET /tasks/`
- `PATCH /tasks/{task_id}`
- `DELETE /tasks/{task_id}`

---

## Running locally

Clone the repo and install dependencies:

```bash
git clone https://github.com/PG181997/multi-tenant-saas-backend.git
cd multi-tenant-saas-backend
pip install -r requirements.txt
```

Create a `.env` file:

```
DATABASE_URL=your_postgresql_url
SECRET_KEY=your_secret_key
```

Start the server:

```bash
uvicorn main:app --reload
```

## Running with Docker

```bash
docker-compose up --build
```

Visit `http://localhost:8000/docs`