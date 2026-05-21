# spurlos.app

Django 6 web application with authentication and a protected dashboard.

## Stack

- Python 3.12 + Django 6
- SQLite (dev)
- No external packages beyond Django

## Apps

| App | Purpose |
|-----|---------|
| `accounts` | Login, logout, register, password change & reset |
| `dashboard` | Single protected view — the starting point for app content |

## URL map

```
/accounts/login/                        → sign-in form
/accounts/logout/                       → clears session → /accounts/login/
/accounts/register/                     → create account → /dashboard/
/accounts/password-change/              → change password (must be logged in)
/accounts/password-change/done/         → confirmation
/accounts/password-reset/               → request reset email
/accounts/password-reset/done/          → "check your email"
/accounts/password-reset/<uid>/<token>/ → set new password via link
/accounts/password-reset/complete/      → success
/dashboard/                             → protected dashboard (redirects to login if not authed)
/admin/                                 → Django admin
```

## Running locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # optional
python manage.py runserver
```

Visit `http://127.0.0.1:8000/accounts/login/` to start.

## Notes

- `EMAIL_BACKEND` is set to `console` — password-reset emails print to the terminal.
- Templates live under each app's own `templates/<app>/` directory; Django's `APP_DIRS=True` picks them up automatically.
- `LOGIN_REDIRECT_URL = /dashboard/`, `LOGOUT_REDIRECT_URL = /accounts/login/`.
