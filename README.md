# spurlos.app

Django 6 web application with authentication and a protected dashboard.

## Stack

- Python 3.12 + Django 6.0.5
- python-dotenv for environment variable management
- SQLite (default) — configurable via `.env`

## Apps

| App | Purpose |
|-----|---------|
| `accounts` | Login, logout, password change & reset — custom email-based user model |
| `dashboard` | Single protected view — the starting point for app content |

## User model

`accounts.User` replaces Django's built-in user. Authentication is by **email** (no username field).

| Field | Type | Notes |
|-------|------|-------|
| `email` | EmailField | unique, used as `USERNAME_FIELD` |
| `first_name` | CharField | optional |
| `last_name` | CharField | optional |
| `is_active` | BooleanField | default `True` |
| `is_staff` | BooleanField | default `False` |
| `date_joined` | DateTimeField | auto-set on creation |

## URL map

```
/                                       → redirects to /dashboard/
/accounts/login/                        → sign-in form
/accounts/logout/                       → clears session → /accounts/login/
/accounts/password-change/              → change password (must be logged in)
/accounts/password-change/done/         → confirmation
/accounts/password-reset/               → request reset email
/accounts/password-reset/done/          → "check your email"
/accounts/password-reset/<uidb64>/<token>/ → set new password via link
/accounts/password-reset/complete/      → success
/dashboard/                             → protected dashboard (redirects to login if not authed)
/admin/                                 → Django admin (user list at /admin/accounts/user/)
```

## Environment variables

Copy `.env.example` to `.env` and adjust as needed:

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | — | **Required.** Django secret key |
| `DEBUG` | `False` | Set to `True` in development |
| `ALLOWED_HOSTS` | `` | Comma-separated list of allowed hosts |
| `DATABASE_ENGINE` | `django.db.backends.sqlite3` | Database backend |
| `DATABASE_NAME` | `db.sqlite3` | Database name / path |
| `EMAIL_BACKEND` | `django.core.mail.backends.console.EmailBackend` | Email backend |

## Running locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then set a SECRET_KEY value
python manage.py migrate
python manage.py createsuperuser   # optional — uses email as username
python manage.py runserver
```

Visit `http://127.0.0.1:8000/accounts/login/` to start.

## Notes

- `EMAIL_BACKEND` defaults to `console` — password-reset emails print to the terminal instead of being sent.
- Templates live under each app's own `templates/<app>/` directory; `APP_DIRS=True` picks them up automatically.
- `LOGIN_REDIRECT_URL = /dashboard/`, `LOGOUT_REDIRECT_URL = /accounts/login/`.
- The admin redirects `/admin/auth/user/` → `/admin/accounts/user/` to account for the custom user model.
