# GitHub and hosting

The maintained project folder and the clean ZIP contain the same shareable files. The original archive and private review tooling live outside the maintained edition. Only Bikash Kushwaha appears as a personal identity in the release documents and app. Technical dependency and framework names remain intact.

## GitHub

Public repository: [BikashCoder31/mybud-student-assistant](https://github.com/BikashCoder31/mybud-student-assistant).

Production: [mybud-student-assistant.vercel.app](https://mybud-student-assistant.vercel.app).

The `main` branch is connected to Vercel project `mybud-student-assistant` in scope `bikash31`. Push reviewed changes from this folder:

```powershell
git add .
git status
git commit -m "Describe the change"
git push origin main
```

The workflow runs Django checks, migration drift detection, static collection, all 28 tests and Ruff on Ubuntu with Python 3.12. [The hosted-edition CI run passed](https://github.com/BikashCoder31/mybud-student-assistant/actions/runs/39472651723). Vercel builds run separately; check both the Actions result and Vercel deployment status after a push.

## Vercel and Neon PostgreSQL

The public app runs native Django on Vercel in Singapore (`sin1`). `pyproject.toml` selects Python 3.12 and `project.wsgi:application`; `uv.lock` pins the build environment. Vercel automatically collects static files. `vercel.json` sets the function region and excludes documentation/private runtime files from the function bundle. Reports and the PowerPoint remain downloadable from GitHub.

A Neon Free PostgreSQL resource supplies durable storage for expenses, budgets and Django sessions. Production and preview use the integration's pooled `DATABASE_URL`; `CONN_MAX_AGE=0`, disabled server-side cursors and a connection timeout suit pooled serverless connections. TLS is required, and stronger URL verification modes are preserved. Vercel refuses startup if a persistent PostgreSQL URL is missing.

Production and preview have private environment settings for `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=false`, exact allowed hosts and HTTPS CSRF origins, `DJANGO_TRUST_PROXY=true`, `MYBUD_MODE=demo` and `MYBUD_MAX_IMAGE_MB=3`. The integration manages database credentials. Keep all `.env*` files private except `.env.example`; do not copy credentials into repository files or commands.

Initial migrations were applied to the new database through `DATABASE_URL_UNPOOLED`. For future schema changes, pull the correct environment into an ignored file, load it privately in the migration process, and use the direct URL as that process's `DATABASE_URL` before running `python manage.py migrate --noinput`. Run migrations as an explicit release operation; request handlers do not run them.

To deploy manually from the linked folder with the installed CLI:

```powershell
vercel deploy --prod --scope bikash31
vercel inspect mybud-student-assistant.vercel.app --scope bikash31
```

The deployed app was checked without Vercel authentication: all six pages and five tools worked, expense totals survived reload, separate browser sessions were isolated, and desktop/mobile layouts had no overflow or console errors. [Verification details](VERIFICATION.md) distinguish these checks from optional live AI.

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

See the official [Django deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/), [Vercel Django guide](https://vercel.com/docs/frameworks/full-stack/django) and [function request limits](https://vercel.com/docs/functions/limitations).
