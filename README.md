# Github Details

Github Details is a Django web app for looking up GitHub users,
organizations, repositories, topic search results, and generating a simple
GitHub-based resume.

## Requirements

- Python 3.12, 3.13, or 3.14
- Django 6.x

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

```powershell
python manage.py runserver
```

Open http://127.0.0.1:8000/.

## Email

The default email backend prints messages to the console. Configure these
environment variables to send real email:

- `DJANGO_EMAIL_BACKEND`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_USE_TLS`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `DEFAULT_FROM_EMAIL`
- `CONTACT_TO_EMAIL`
