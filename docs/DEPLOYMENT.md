# GitHub and hosting preparation

The maintained project folder and the clean ZIP contain the same shareable files. The original archive and private review tooling live outside the maintained edition. Only Bikash Kushwaha appears as a personal identity in the release documents and app. Technical dependency and framework names remain intact.

## GitHub

Create a repository for this project and upload the contents of this folder, or use Git from this folder after reviewing the files:

```powershell
git init
git add .
git status
git commit -m "Prepare MyBud student assistant portfolio edition"
git branch -M main
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main
```

Replace `YOUR_REPOSITORY_URL` with the actual repository URL. No repository or live deployment link is claimed until publication occurs. The included workflow runs Django checks, migration drift detection, static collection, the test suite, and Ruff on Ubuntu with Python 3.12. Local checks have passed; that does not prove remote CI has run.

## Persistent Django host

Use a host with Python 3.12, HTTPS and a persistent writable disk for SQLite, or migrate to a durable database supported by Django. On Linux install the pinned environment and a production WSGI server such as Gunicorn. Configure the WSGI application as `project.wsgi:application`. Development `runserver` is for local review.

Set `DJANGO_DEBUG=false`, a long random `DJANGO_SECRET_KEY`, the exact `DJANGO_ALLOWED_HOSTS`, and the full HTTPS `DJANGO_CSRF_TRUSTED_ORIGINS`. Set `DJANGO_DB_PATH` to the durable database location. Run migrations and static collection before starting the server. For a trusted reverse proxy that reliably sets the HTTPS forwarding header, set `DJANGO_TRUST_PROXY=true`. Check the host's proxy configuration first.

```bash
python -m pip install -r requirements-lock.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py check --deploy --fail-level WARNING
```

The deployment check expects the production environment values to be set. Secure cookies, HTTPS redirect, HSTS and clickjacking protection activate when debug is false. The development fallback secret is a private local file and is absent from the release ZIP. Set production secrets explicitly.

Default to `MYBUD_MODE=demo` for a public showcase. Live mode requires the model and API key, incurs provider usage, and sends submitted tool inputs to that provider. The local-memory session limiter is a basic demo control; a public live service needs a shared rate limit store and appropriate account/access controls. SQLite and cookie-based browser ownership suit a small demo, with no account recovery or cross-device access.

## Vercel scope

This full Django/SQLite app is prepared for conventional persistent hosting. Do not claim a Vercel deployment of the working expense tracker without configuring durable storage and checking the complete runtime flow. The report PDFs and screenshots can be hosted separately as static portfolio content. This edition includes no invented deployment status or public URL.

See the official [Django deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/).
