from django.conf import settings


def identity(request):
    return {
        "mybud_mode": settings.MYBUD_MODE,
        "maintainer": "Bikash Kushwaha",
        "image_limit_mb": settings.MYBUD_MAX_IMAGE_MB,
    }
