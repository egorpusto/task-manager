# ✅ Task Manager - Django Web Application

A full-featured task management web application built with Django, PostgreSQL, Redis, and Docker.

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Django](https://img.shields.io/badge/Django-5.2-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)
![Redis](https://img.shields.io/badge/Redis-7-red.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)
![CI](https://github.com/egorpusto/task-manager/actions/workflows/ci.yml/badge.svg)
![Tests](https://img.shields.io/badge/Tests-25%20passing-brightgreen.svg)
![Coverage](https://img.shields.io/badge/Coverage-95%25-brightgreen.svg)

## 🎯 Project Overview

A clean, production-ready task manager with user authentication, task filtering, tagging system, and dark mode. Built as a portfolio project demonstrating Django best practices, Docker infrastructure, CI/CD pipeline, and background task processing with Celery.

## ✨ Features

### Tasks
- ✅ Create, edit, and delete tasks with priorities, statuses, and deadlines
- ✅ Set priority (Low / Medium / High)
- ✅ Track status (To Do / In Progress / Done)
- ✅ Filter tasks by status, priority, tag, and search by title
- ✅ Sort tasks by date, deadline, or priority
- ✅ Set deadlines with overdue highlighting
- ✅ Tag system with Select2 autocomplete
- ✅ Email reminders for upcoming deadlines (via Celery)
- ✅ Pagination (9 tasks per page)

### Users
- ✅ Registration with auto-login
- ✅ Custom User model (AbstractUser)
- ✅ Each user sees only their own tasks
- ✅ Protection against accessing other users' tasks (404)

### UI
- ✅ Responsive Bootstrap 5 interface
- ✅ Dark mode with localStorage persistence
- ✅ Success/error notifications (Django messages)
- ✅ Admin panel

## 🛠️ Tech Stack

### Backend
- **Django** 5.2 - Web framework
- **PostgreSQL** 16 - Primary database
- **Redis** 7 - Cache & Celery broker
- **Celery** + **django-celery-beat** - Background tasks & scheduling
- **django-filter** - Declarative filtering and ordering
- **Gunicorn** - WSGI server
- **Whitenoise** - Static files serving
- **python-decouple** - Environment configuration

### Frontend
- **Bootstrap** 5.3 - UI framework
- **Select2** 4.1 - Tag autocomplete
- **Font Awesome** 6 - Icons

### Infrastructure
- **Docker** & **Docker Compose** - Containerization (5 services)
- **GitHub Actions** - CI/CD pipeline (lint + test + coverage)
- **pre-commit** - Automated code quality hooks

### Testing & Quality
- **pytest** + **pytest-django** - Test framework
- **coverage** - Code coverage (95%)
- **black** - Code formatter
- **isort** - Import sorter
- **flake8** - Linter

## 🚀 Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.12+

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/egorpusto/task-manager.git
cd task-manager
```

2. **Create `.env` file:**
```bash
cp .env.example .env
```

3. **Edit `.env` with your values:**
```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=task_manager_db
DB_USER=task_manager_user
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://127.0.0.1:6379/1

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

4. **Start PostgreSQL and Redis:**
```bash
docker compose up db redis -d
```

5. **Create and activate virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

6. **Run migrations:**
```bash
python manage.py migrate
python manage.py setup_periodic_tasks
```

7. **Create superuser:**
```bash
python manage.py createsuperuser
```

8. **Run the development server:**
```bash
python manage.py runserver
```

Open http://127.0.0.1:8000

### Run with Docker (full stack)
```bash
docker compose up -build
```

## 🧪 Testing
```bash
# Run tests with coverage
pytest -cov=tasks -cov=accounts

# Run pre-commit hooks manually
pre-commit run -all-files
```

### Test Coverage - 95%

| Module | Coverage |
|-|-|
| `accounts/` | 100% |
| `tasks/models.py` | 100% |
| `tasks/views.py` | 100% |
| `tasks/filters.py` | 100% |
| `tasks/forms.py` | 100% |
| `tasks/tasks.py` | 100% |
| **Total** | **95%** |

### Test Suite - 25 tests

| Class | Tests |
|-|-|
| `TestTagModel` | 2 |
| `TestTaskModel` | 7 |
| `TestTaskListView` | 3 |
| `TestTaskCreateView` | 1 |
| `TestTaskUpdateView` | 2 |
| `TestTaskDeleteView` | 2 |
| `TestTaskFilterView` | 3 |
| `TestSendDeadlineReminders` | 4 |
| `TestSignUpView` | 1 |
| **Total** | **25** |

## 🔄 CI/CD Pipeline

Every push and pull request to `main` triggers:

✅ **Lint** - black, isort, flake8
✅ **Tests** - Full pytest suite with PostgreSQL and Redis services
✅ **Coverage** - Report artifact uploaded on every run

## 🐳 Docker Services

| Service | Image | Port |
|-|-|-|
| `web` | Custom (Django + Gunicorn) | 8000 |
| `db` | postgres:16-alpine | 5432 |
| `redis` | redis:7-alpine | 6379 |
| `celery_worker` | Custom (Celery worker) | - |
| `celery_beat` | Custom (Celery scheduler) | - |

### Useful Commands
```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f web

# Stop all services
docker compose down

# Remove volumes (reset database)
docker compose down -v

# Run Celery worker locally
celery -A task_manager worker --loglevel=info

# Trigger deadline reminders manually
python manage.py shell -c "from tasks.tasks import send_deadline_reminders; send_deadline_reminders.delay()"
```

## 🗄️ Database Schema

### Task
```
- id: BigInteger (Primary Key)
- user: ForeignKey → accounts.User
- title: VARCHAR(200)
- description: TEXT
- priority: VARCHAR(10) [low, medium, high]
- status: VARCHAR(20) [todo, in_progress, done]
- deadline: TIMESTAMP (nullable)
- tags: ManyToMany → Tag
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

### Tag
```
- id: BigInteger (Primary Key)
- name: VARCHAR(50) UNIQUE
```

### User (custom)
```
- Extends Django AbstractUser
- Ready for future profile extensions (avatar, timezone, bio)
```

## 🏗️ Project Structure
```
task_manager/
├── manage.py
├── task_manager/               # Django project config
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── celery_app.py           # Celery configuration
├── accounts/                   # Custom user app
│   ├── models.py               # AbstractUser
│   ├── forms.py                # CustomUserCreationForm
    ├── apps.py
│   └── admin.py
├── tasks/                      # Main application
│   ├── migrations/
│   ├── management/
│   │   └── commands/
│   │       └── setup_periodic_tasks.py
│   ├── static/tasks/css/
│   ├── templates/
│   │   ├── base.html
│   │   ├── 404.html
│   │   ├── registration/
│   │   └── tasks/
│   ├── models.py               # Task, Tag with TextChoices
│   ├── views.py
    ├── apps.py
│   ├── forms.py
│   ├── filters.py              # django-filter TaskFilter
│   ├── tasks.py                # Celery tasks
│   ├── urls.py
│   ├── admin.py
│   └── tests.py                # 25 pytest tests
├── requirements.txt
├── pyproject.toml              # black, isort, pytest, coverage config
├── .pre-commit-config.yaml
├── docker-compose.yml
├── dockerfile
├── .env.example
└── .github/workflows/ci.yml
```

## 🔒 Security

- **CSRF protection** - All forms protected
- **Login required** - All task views require authentication
- **Object-level protection** - Users can only access their own tasks (404 on foreign objects)
- **Custom User model** - Ready for production from day one
- **Environment variables** - Secrets never hardcoded
- **Password validation** - Django built-in validators

## 📸 Screenshots

| Task List | Task List (Night theme) | Add Task | Edit Task (Night theme) |
|-|-|-|-|
| ![Task List](screenshots/task_list.png) | ![Task List (Night theme)](screenshots/task_list_nt.png) | ![Add Task](screenshots/add_task.png) | ![Edit Task (Night theme)](screenshots/edit_task_nt.png) |

## 👤 Author

**Egor Pusto**
- GitHub: [@egorpusto](https://github.com/egorpusto)

## 📄 License

This project is for educational purposes.
