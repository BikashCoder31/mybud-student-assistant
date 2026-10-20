# Verification record

Checked on 20 October 2026 for the maintained MyBud portfolio edition by Bikash Kushwaha.

## Backend and configuration

| Check | Observed result |
| --- | --- |
| `python manage.py test main` | 23 tests passed |
| `python manage.py check` | No issues |
| `python manage.py makemigrations --check --dry-run` | No changes detected |
| `python -m ruff check .` | Passed |
| `python -m ruff format --check .` | Passed |
| `python manage.py migrate --noinput` | Applied successfully to a new local database |
| `python manage.py collectstatic --noinput` | Completed with WhiteNoise processing |
| Production-configured `check --deploy --fail-level WARNING` | No issues using a generated secret, debug disabled and explicit test host/origin |
| Production-mode request smoke | HTTPS page, hashed WhiteNoise stylesheet, secure cookies, CSRF-protected expense write and health endpoint passed against an isolated local database |

The suite checks six page routes, tool response contracts, real Python syntax parsing without code execution, recipe shape, itinerary duration, invalid JSON and input types, HTTP methods, CSRF enforcement, exact Decimal arithmetic, invalid/nonfinite money, expense deletion/reset and cross-session isolation. Image checks include a real valid PNG and a corrupt checksum. Mocked live checks cover missing configuration, provider failure, parse errors, wrong schema and attempted response metadata overrides.

The original code could not start with the maintained dependency environment because it imported the old SDK eagerly. Source inspection also found a missing expense template/service, a nonexistent code-analysis function and mismatched frontend API routes. These paths now have direct regression coverage. Provider parsing and metadata-override regression tests were observed failing before their fixes. A corrupt PNG checksum originally raised an unhandled Pillow exception; its regression now returns HTTP 400.

Runtime: Windows CPU, Python 3.12.14, Django 5.2.18, google-genai 1.75.0, Pillow 12.3.0, python-dotenv 1.2.4, WhiteNoise 6.12.0 and Ruff 0.17.1. `requirements-lock.txt` records the full installed snapshot. The upstream provider-error log messages during negative tests are expected. They contain no submitted content or provider exception details.

## Browser QA

The flow under test was: open the home page, choose each tool, submit inputs, observe the rendered response, save/reload/remove expenses and inspect the six routes at desktop and mobile viewport sizes.

Environment: local Django demo at `http://127.0.0.1:8793`, Microsoft Edge through bundled Playwright 1.62.1, desktop 1440 by 1000 and mobile-sized 390 by 844. The Browser plugin was unavailable, so regular Playwright supplied the checks and screenshots. Browser launch and local-server execution required the local execution permission boundary; the successful run used the same repaired app.

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

Live Gemini requests were not made with credentials. The provider boundary is tested with mocks; account model availability, live latency and provider quality remain unverified. Camera hardware/permission, physical mobile devices, macOS, Linux runtime, Firefox and Safari were not tested locally. The included Ubuntu GitHub Actions workflow has not been claimed as remotely executed.

The demo uses sample chat/recipe/travel responses, Python syntax parsing, in-memory image validation and real SQLite expenses. It does not train a model or establish image-recognition accuracy. It has no student account recovery, cross-device expense access, bank connection or chat history. The per-session live limit uses a process-local cache. Public live hosting needs durable storage and appropriate shared access/rate controls.

The project is prepared locally for GitHub and persistent Django hosting. No public repository or deployment URL is asserted. Original archived submission files remain outside the shareable edition. The release audit separately checks all shareable text, document metadata and archive entries for identity and private-file leaks.
