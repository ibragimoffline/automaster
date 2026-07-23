# Automaster

Automaster is a Django REST Framework + React/Vite MVP for finding auto masters,
creating repair orders, reviews, and using an admin dashboard.

## Stack

- Backend: Django 6, Django REST Framework, Simple JWT, PostgreSQL
- Async tasks: Celery with RabbitMQ; Redis stores task results and application cache
- Frontend: React 18, Vite
- Demo data: `fixtures/initial_data.json`

## Backend setup

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
```

Create a PostgreSQL database named `automaster`, then update `.env` if your
database user, password, host, or port are different.

```powershell
python manage.py migrate
python manage.py loaddata fixtures\initial_data.json
python manage.py runserver
```

API docs:

```text
http://127.0.0.1:8000/api/docs/
```

## Demo accounts

The fixture contains ready demo data:

```text
admin / admin12345
mijoz1 / parol1234
usta1 / parol1234
```

If you want to recreate demo data instead of loading the fixture:

```powershell
python manage.py seed
```

## Frontend setup

```powershell
cd frontend
npm install
npm run dev
```

Vite dev server proxies API requests to Django at `http://127.0.0.1:8000`.

## Docker and background tasks

Start PostgreSQL, Redis, RabbitMQ, Django, Celery, and the frontend:

```powershell
docker compose up --build
```

RabbitMQ is the Celery message broker. Its management UI is available at
`http://127.0.0.1:15672/`; the default local username and password are both
`automaster`. Change `RABBITMQ_DEFAULT_USER`, `RABBITMQ_DEFAULT_PASS`, and
`RABBITMQ_DEFAULT_VHOST` in `.env` outside local development.

To run the services without Docker, start RabbitMQ and Redis first, then run the
Celery worker in a separate terminal:

```powershell
celery -A config worker --loglevel=info
```

## Useful endpoints

```text
POST /api/token/
POST /api/token/refresh/
POST /api/auth/register/
GET  /api/auth/me/
GET  /api/masters/nearby/
GET  /api/services/categories/
GET  /api/orders/
GET  /api/admin/stats/
```

Use JWT like this:

```http
Authorization: Bearer <access_token>
```
