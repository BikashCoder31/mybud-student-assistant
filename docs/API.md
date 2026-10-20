# HTTP and data contract

All tools have an HTML page and a separate JSON endpoint. API POST requests require `Content-Type: application/json` and a valid Django `X-CSRFToken` header from the page. The UI supplies both. Page URLs accept GET only. Requests do not execute submitted code.

| Route | Method | JSON request |
| --- | --- | --- |
| `/api/chat/` | POST | `{"message":"Help me plan a study session"}` |
| `/api/code/` | POST | `{"code":"print(1)","language":"python"}` |
| `/api/recipes/` | POST | `{"ingredients":["rice","peas"]}` |
| `/api/detect-food/` | POST | `{"image":"data:image/png;base64,..."}` |
| `/api/travel/` | POST | `{"destination":"Sample destination","duration":3}` |
| `/api/expenses/` | GET | Current browser session and month snapshot |
| `/api/expenses/` | POST | `{"action":"budget","amount":"1000.00"}` |
| `/api/expenses/` | POST | `{"action":"add","category":"Meals","amount":"125.50"}` |
| `/api/expenses/` | POST | `{"action":"delete","id":1}` |
| `/api/expenses/` | POST | `{"action":"reset"}` |
| `/health/` | GET | App status and selected assistant mode |

Assistant success responses include `success: true`, trusted `mode: demo/live`, and one tool result: `response`, `analysis`, `recipes`, `dish`, or `data`. Expense responses include the month, NPR currency, budget, total, remaining amount, exceeded flag, expense rows and category totals. Amounts travel as decimal strings; presentation may format them with separators. The session identifier is never returned in JSON.

Invalid input returns 400. An expense outside the current session/month returns 404. Unsupported HTTP methods return 405. Live throttling returns 429. Missing live configuration returns 503. Provider failures and mismatched response schemas return 502 with a generic message. Standard Django CSRF rejection returns 403. The frontend handles unsuccessful or non-JSON responses without injecting them into HTML.

Limits: message 4000 characters, code 20000 characters, destination 120 characters, duration 1–30 integer days, 1–20 ingredients of up to 80 characters each, category 64 characters. Expense amounts must be positive and below 100000000, with at most two decimal places. Budgets may be zero. Booleans, nonfinite values and excessive precision are rejected.

Images must decode as JPEG, PNG or WebP, up to the configured `MYBUD_MAX_IMAGE_MB` limit (3 MB on the public Vercel app; 5 MB locally) and 16 million pixels. The hosted limit keeps base64 JSON within the platform request limit. The service verifies file contents, converts the image to RGB and resizes it to fit 1600 by 1600 pixels before optional live processing. Images stay in memory and are not saved as uploads. Demo mode does not perform dish recognition. Camera permission is requested only after selecting Use Camera and requires localhost or HTTPS.
