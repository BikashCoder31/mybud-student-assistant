"""Page views and validated JSON APIs with Django CSRF enforcement."""

import json
import logging
import time

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import RequestDataTooBig
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .services import assistant, expenses

logger = logging.getLogger(__name__)


@require_GET
@ensure_csrf_cookie
def page(request, template="home.html"):
    return render(request, template)


def body(request):
    if request.content_type != "application/json":
        raise ValueError("Send an application/json request.")
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError, RequestDataTooBig) as exc:
        raise ValueError("Provide a valid JSON object within the upload limit.") from exc
    if not isinstance(data, dict):
        raise ValueError("The JSON body must be an object.")
    return data


def failure(message, status):
    return JsonResponse({"success": False, "error": message}, status=status)


@require_POST
def tool_api(request, task):
    try:
        data = assistant.prepare(task, body(request))
    except ValueError as exc:
        return failure(str(exc), 400)
    try:
        if settings.MYBUD_MODE == "live":
            if not request.session.session_key:
                request.session.create()
            key = f"mybud:{request.session.session_key}:{int(time.time() // 60)}"
            cache.add(key, 0, 120)
            if cache.incr(key) > 10:
                return failure("Request limit reached. Try again in a minute.", 429)
        result = assistant.execute(task, data)
        return JsonResponse({**result, "success": True, "mode": settings.MYBUD_MODE})
    except assistant.ConfigurationError as exc:
        return failure(str(exc), 503)
    except Exception:
        logger.warning("Assistant provider failed for tool %s", task)
        return failure("The AI service could not complete this request. Try again later.", 502)


@require_http_methods(["GET", "POST"])
def expenses_api(request):
    try:
        return JsonResponse(
            {
                "success": True,
                **expenses.process(request, body(request) if request.method == "POST" else None),
            }
        )
    except ValueError as exc:
        return failure(str(exc), 400)
    except LookupError as exc:
        return failure(str(exc), 404)


@require_GET
def health(request):
    return JsonResponse({"status": "ok", "mode": settings.MYBUD_MODE})
