# Verification record

Checked on 20–21 October 2026 for the maintained MyBud portfolio edition by Bikash Kushwaha.

## Backend and configuration

| Check | Observed result |
| --- | --- |
| `python manage.py test main` | 28 tests passed locally and in GitHub Actions |
| `python manage.py check` | No issues |
| `python manage.py makemigrations --check --dry-run` | No changes detected |
| `python -m ruff check .` | Passed |
| `python -m ruff format --check .` | Passed |
| `python manage.py migrate --noinput` | Applied successfully to a new local database |
| `python manage.py collectstatic --noinput` | Completed with WhiteNoise processing |
| Production-configured `check --deploy --fail-level WARNING` | No issues using a generated secret, debug disabled and explicit test host/origin |
| Production-mode request smoke | HTTPS page, hashed WhiteNoise stylesheet, secure cookies, CSRF-protected expense write and health endpoint passed against an isolated local database |
| PostgreSQL provisioning | Initial migrations applied to Neon through its direct URL; client TLS confirmed |
| Serverless configuration | PostgreSQL required; weaker TLS modes strengthened and stronger modes preserved; 3 MB hosted image limit enforced |
| GitHub Actions | [Run 39472651723](https://github.com/BikashCoder31/mybud-student-assistant/actions/runs/39472651723) passed on Ubuntu/Python 3.12, including all 28 tests and Ruff |
| Vercel production | Deployment ready; [public canonical URL](https://mybud-student-assistant.vercel.app) exercised without authentication |
| Redeployment persistence | Isolated budget, expense and browser session survived a GitHub-triggered production redeployment; test records then reset |
| Public security configuration | Missing-CSRF POST rejected with 403; HTTPS HSTS and `X-Frame-Options: DENY` present |

The suite checks six page routes, tool response contracts, real Python syntax parsing without code execution, recipe shape, itinerary duration, invalid JSON and input types, HTTP methods, CSRF enforcement, exact Decimal arithmetic, invalid/nonfinite money, expense deletion/reset and cross-session isolation. Image checks include a real valid PNG and a corrupt checksum. Mocked live checks cover missing configuration, provider failure, parse errors, wrong schema and attempted response metadata overrides.

The original code could not start with the maintained dependency environment because it imported the old SDK eagerly. Source inspection also found a missing expense template/service, a nonexistent code-analysis function and mismatched frontend API routes. These paths now have direct regression coverage. Provider parsing and metadata-override regression tests were observed failing before their fixes. A corrupt PNG checksum originally raised an unhandled Pillow exception; its regression now returns HTTP 400.

Runtime: Python 3.12, Django 5.2.18, google-genai 1.75.0, Pillow 12.3.0, python-dotenv 1.2.4, WhiteNoise 6.12.0, dj-database-url 3.1.2, psycopg 3.3.6 and Ruff 0.17.1. Local checks used Windows CPU/Python 3.12.14; remote CI used Ubuntu. `requirements-lock.txt` records the installed snapshot and `uv.lock` pins Vercel dependencies. The provider-error log messages during negative tests are expected and contain no submitted content or exception details.

## Browser QA

The flow under test was: open the home page, choose each tool, submit inputs, observe the rendered response, save/reload/remove expenses and inspect the six routes at desktop and mobile viewport sizes.

Environment: local Django demo at `http://127.0.0.1:8793`, Microsoft Edge through bundled Playwright 1.62.1, desktop 1440 by 1000 and mobile-sized 390 by 844. The Browser plugin was unavailable, so regular Playwright supplied the checks and screenshots. Browser launch and local-server execution required the local execution permission boundary; the successful run used the same repaired app.

The same complete flow also passed on the public production URL `https://mybud-student-assistant.vercel.app`, with Neon PostgreSQL persistence and no Vercel login. Both viewport sizes, all six page routes, all five tools, actual image upload, cross-session isolation and harmless rendering of injected markup were checked. No console errors/warnings, uncaught errors or failed requests were observed. Published screenshots illustrate the local run; separate hosted captures were reviewed during deployment.

| Required browser check | Result |
| --- | --- |
| Page identity | Correct MyBud pages, visible demo label and Bikash Kushwaha |
| Meaningful first screen | Heading, navigation, tool controls and app content render |
| Framework/server error pages | None observed |
| Console health | No browser console errors/warnings or uncaught page errors in the successful run |
| Asset/network health | No failed requests in the successful run; local assets require no CDN |
| Interaction proof | All five tool workflows produced their expected demo/local results |
| Persistence | Expense totals survived a page reload; deletion updated the saved balance |
| Session ownership | A separate browser context saw no expenses from the first context |
| HTML injection | Submitted chat markup remained text and created no image element |
| Responsive layout | All six routes had no horizontal page overflow at both viewport sizes |
| Screenshots | Seven captures included under `docs/screenshots/` |

The expense screenshot records a budget of NPR 1000.00 and three illustrative expenses totalling NPR 800.25, leaving NPR 199.75. The browser then removed the NPR 150.00 transport item and observed NPR 349.75 remaining. These are demonstration records, not financial performance metrics. The image-upload browser test uses a valid small PNG and confirms the explicit no-classification message.

## Boundaries

Live Gemini requests were not made with credentials. The provider boundary is tested with mocks; account model availability, live latency and provider quality remain unverified. Camera hardware/permission, physical mobile devices, macOS, Firefox and Safari were not tested. Ubuntu CI and the hosted Vercel runtime were checked as described above.

The demo uses sample chat/recipe/travel responses, Python syntax parsing, in-memory image validation and real expenses in Neon PostgreSQL (SQLite locally). It does not train a model or establish image-recognition accuracy. It has no student account recovery, cross-device expense access, bank connection or chat history. The per-session live AI limit uses a process-local cache; enabling public live AI requires shared access/rate controls.

The project is public on [GitHub](https://github.com/BikashCoder31/mybud-student-assistant) and [Vercel](https://mybud-student-assistant.vercel.app). Original archived submission files remain outside the shareable edition. The release audit separately checks all shareable text, document metadata and archive entries for identity and private-file leaks.
